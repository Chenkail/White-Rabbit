# 3rd-party
import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dev_ids = []
        with open("dev_ids.txt") as f:
            for line in f:
                self.dev_ids.append(int(line.strip()))

    async def cog_check(self, ctx):
        return ctx.author.id in self.dev_ids

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot has logged in")

    @ commands.command()
    async def load(self, ctx, extension_name: str = "all"):
        """(Re)loads an extension"""

        if extension_name == "all":
            loaded_extensions = list(self.bot.extensions.keys())
            for extension in loaded_extensions:
                self.bot.reload_extension(extension)
            await ctx.send(f"Reloaded {', '.join(loaded_extensions)}")
            return

        # Load extension
        try:
            if extension_name in self.bot.extensions:
                self.bot.reload_extension(extension_name)
            else:
                self.bot.load_extension(extension_name)
            await ctx.send(f"Loaded {extension_name}")
        except discord.ext.commands.errors.ExtensionNotFound:
            await ctx.send(f"Couldn't find {extension_name}")

    @ commands.command()
    async def unload(self, ctx, extension_name: str):
        """Unloads an extension."""

        self.bot.unload_extension(extension_name)
        await ctx.send(f"Unloaded {extension_name}")

    @ commands.command()
    async def quit(self, ctx):
        """Quits the bot"""

        await ctx.send("Shutting down, thanks for playing!")
        await self.bot.close()


def setup(bot):
    bot.add_cog(Admin(bot))