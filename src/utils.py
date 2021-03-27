# Built-in
import asyncio
import math
from os.path import join
from pathlib import Path
import random
import re
from typing import Union
# 3rd-party
import discord
# Local
import gamedata
from localization import DEFAULT_LOCALIZATION, LOCALIZATION_DATA, LANGUAGE_KEY
from resources import ImageResource


def flip():
    return random.choice([LOCALIZATION_DATA["flip"]["heads"], LOCALIZATION_DATA["flip"]["tails"]])


def codeblock(text: str):
    return f"```{text}```"


def get_text_channels(guild):
    return {
        channel.name: channel
        for channel in guild.text_channels
    }


def time_string(time):
    """Takes # of seconds and returns formatted string mm:ss"""

    def pad(num):
        return str(int(num)).zfill(2)

    minutes = pad(math.floor(time / 60))
    seconds = pad(time % 60)

    return f"{minutes}:{seconds}"


def get_image(directory: Path, name: str) -> Path:
    img = ImageResource(ImageResource.IMAGE_EXTENSIONS)
    try:
        return img.get(directory, name)
    except FileNotFoundError as err:
        parts = list(directory.parts)
        try:
            idx = parts.index(LANGUAGE_KEY)
            parts[idx] = DEFAULT_LOCALIZATION
            return img.get(Path(join(*parts)), name)
        except ValueError:
            raise err


# pylint: disable=unsubscriptable-object   # https://github.com/PyCQA/pylint/issues/3637#issuecomment-720097674
def send_image(channel, filepath: Union[Path, str], ctx=None):
    """Sends an image to a specified channel"""

    if isinstance(channel, str):
        if not ctx:
            raise ValueError(
                "Cannot send to channel without ctx.text_channels"
            )
        channel = ctx.text_channels[channel]

    if isinstance(filepath, Path):
        # If sending image as a file, attach it
        asyncio.create_task(channel.send(file=discord.File(filepath)))
    else:
        # Otherwise send the link directly
        asyncio.create_task(channel.send(filepath))


def send_folder(channel, path, ctx=None):
    """Sends all images in a folder in alphabetical order"""

    for image in sorted(path.glob("*.*")):
        filepath = get_image(path, image.stem)
        send_image(channel, filepath, ctx)


def is_command(message: str):
    """Checks if a string seems like an attempt to send a command"""

    # Check if message has ! prefix
    if not message.startswith("!"):
        return False
    # If space after the !, not a command
    if message.startswith("! "):
        return False

    # Remove ! from start of string
    message = message[1:]

    # If string contains non-alphanumeric characters (besides spaces)
    # then it is not a command
    if not message.replace(' ', '').isalnum():
        return False

    # If it passes all the above checks it is probably a command attempt
    return True


def clean_message(ctx, text: str):
    """Removes emojis and out of character parts of a string"""

    text = remove_emojis(text).strip()
    text = ooc_strip(ctx, text).strip()

    return text


def remove_emojis(text: str):
    emojis = re.compile(pattern="["
                        u"\U0001F170-\U0001F19A"  # more emojis
                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                        u"\U0001F600-\U0001F64F"  # emoticons
                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                        u"\U0001F90C-\U0001F9FF"  # more emojis
                        "]+", flags=re.UNICODE)

    return emojis.sub(r'', text)


def ooc_strip(ctx, text: str):
    """
    Takes a string and removes out of context portions

    String should be stripped of whitespace first
    """

    # If entire message is out of character, ignore
    if ctx.game.ooc_strip_level >= 1:
        if text.startswith("(") and text.endswith(")"):
            return ""

    # If using aggressive removal for OOC messages, greedy remove anything
    # inside parentheses
    if ctx.game.ooc_strip_level >= 2:
        re.sub(r'\([^)]*\)', '', text)

    return text
