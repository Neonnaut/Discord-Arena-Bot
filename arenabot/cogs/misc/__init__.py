import platform # Version
import pytz
from datetime import datetime
from typing import Optional, List

import discord
from discord.ext import commands
from discord import app_commands

from constants import CHECK, ERR, WARN, INFO

from cogs.misc.help import MyHelpCommand

class Misc(commands.Cog, name="Misc"):
    """Useful commands"""

    COG_EMOJI = "🏷️"

    def __init__(self, bot: discord.Client):
        self.bot = bot

        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @app_commands.command()
    async def help(self, interaction: discord.Interaction, command: Optional[str]):
        """Shows help on a command or category of commands."""

        ctx = await self.bot.get_context(interaction, cls=commands.Context)
        await ctx.reply(f"{INFO} Help on prefix commands", mention_author=False, delete_after=3)
        if command is not None and not "all":
            await ctx.send_help(command)
        else:
            await ctx.send_help()

    @help.autocomplete("command")
    async def command_autocomplete(self, interaction: discord.Interaction, needle: str) -> List[app_commands.Choice[str]]:
        assert self.bot.help_command
        ctx = await self.bot.get_context(interaction, cls=commands.Context)
        help_command = self.bot.help_command.copy()
        help_command.context = ctx
        """
        if not needle:
            return [
                app_commands.Choice(name=f"{getattr(cog, 'COG_EMOJI', None)} {cog_name}", value=cog_name)
                for cog_name, cog in self.bot.cogs.items()
                if await help_command.filter_commands(cog.get_commands())
            ][:25]
        """
        if needle:
            needle = needle.lower()

            return_commands = []
            for command in await help_command.filter_commands(self.bot.walk_commands(), sort=True):
                if needle in command.qualified_name:
                    return_commands.append(app_commands.Choice(name=command.qualified_name, value=command.qualified_name))

            for cog_name, cog in self.bot.cogs.items():
                if needle in cog_name.casefold():
                    return_commands.append(app_commands.Choice(name=f"{getattr(cog, 'COG_EMOJI', None)} {cog_name}", value=cog_name))

            return_commands = return_commands[:10]

            return return_commands
        else:
            return [app_commands.Choice(name="Type a command or category...", value="all")]

    @commands.command()
    @commands.is_owner()
    async def list_permissions(self, ctx: commands.Context):
        """Command which lists the bot's permissions."""

        permissions = "**Bot Permissions**:```\n" + "\n".join([
            f"{name.lower().replace('_', ' ').title()}: {'❌' if not value else '✅'}"
            for name, value in ctx.guild.me.guild_permissions
        ]) + "```"
        await ctx.send(permissions)

        intents = "**Bot Intents**:```\n" + "\n".join([
            f"{name.lower().replace('_', ' ').title()}: {'❌' if not value else '✅'}"
            for name, value in discord.Intents.all()
        ]) + "```"
        await ctx.send(intents)

    @commands.command()
    @commands.is_owner()
    async def list_servers(self, ctx: commands.Context):
        """Lists al the servers the bot is in"""

        servers = "**Servers bot is in**:```\n" + "\n".join([
            str(guild)
            for guild in self.bot.guilds
        ]) + "```" or "None" 
        await ctx.send(servers)

    @commands.command()
    @commands.is_owner()
    async def sync_commands(self, ctx: commands.Context):
        """Syncs slash commands."""
        try:
            await self.bot.tree.sync()  # Sync any slash commands the bot has set up
            await ctx.send(f"{CHECK} Slash commands synced!")
        except:
            await ctx.send(f"{ERR} Slash commands were not synced!", delete_after=5)
            try:
                await ctx.message.delete(delay=5)
            except Exception:
                pass

async def setup(bot: commands.bot):
    await bot.add_cog(Misc(bot))
