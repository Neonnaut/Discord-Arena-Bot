from difflib import SequenceMatcher
import os
from discord import Intents
from discord.ext import commands
import discord
import logging

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from constants import DISCORD_CLIENT, ERR, LoggerFormatter

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(LoggerFormatter())
logger.addHandler(ch)

def main():
    bot = MyBot( # define an instance of this bot
        command_prefix=commands.when_mentioned_or(*["!!", "++"]),
        intents=Intents().all(),
        case_insensitive=True,
    )
    bot.run(DISCORD_CLIENT,log_handler=None) # Run this bot instance

class MyBot(commands.Bot):

    async def setup_hook(self):
        for cog in sorted(os.listdir("./cogs")): # Load all the cogs / extensions in the cogs folder
            if cog.endswith(".py"):
                cog = cog[:-3]
            if not cog.startswith("_"):
                try:
                    await self.load_extension("cogs." + cog)
                except Exception as e:
                    logger.error(str(e))

    async def on_ready(self): # Prints that the bot is running
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="!!help"))
        logger.info(f'Logged in as {self.user.name}')

        # await self.tree.sync()  # Sync any slash commands the bot has set up

    async def on_command_error(self, ctx: commands.Context, e): # Error messages
        if isinstance(e, commands.CommandNotFound):
            # If command not found find the most similar command before deleting both messages
            message = ctx.message  # later overwrite the attributes
            used_prefix = str(ctx.prefix)  # the prefix used
            used_command = message.content.split()[0][len(used_prefix):]  # getting the command, `!foo a b c` -> `foo`

            available_commands = [cmd.name for cmd in self.commands]
            matches = {  # command name: ratio
                cmd: SequenceMatcher(None, cmd, used_command).ratio()
                for cmd in available_commands
            }

            command = max(matches.items(), key=lambda item: item[1])[0]  # the most similar command

            try:
                arguments = message.content.split(" ", 1)[1]
            except IndexError:
                arguments = "" # command didn't take any arguments

            new_content = f"{used_prefix}{command} {arguments}".strip()

            await ctx.channel.send(f"{ERR} Command \"{used_command}\" was not found.\nDid you mean: `{new_content}`?", delete_after=5)
            try:
                await ctx.message.delete(delay=5)
            except:
                pass
            # "Command "_" is not found."
        if isinstance(e, commands.MissingRequiredArgument):
            await ctx.send(f"{ERR} Missing required arguments."
                        + f"Run `{ctx.clean_prefix}help {ctx.command}` for help on this command.", delete_after=5)
            try:
                await ctx.message.delete(delay=5)
            except:
                pass
            # "Missing required arguments. Run !!help _ for help on this command."
        if isinstance(e, commands.NotOwner):
            await ctx.send(f"{ERR} {e}", delete_after=5)
            try:
                await ctx.message.delete(delay=5)
            except:
                pass
            # You do not own this bot.
        if isinstance(e, commands.MissingPermissions):
            await ctx.send(f"{ERR} {e}", delete_after=5)
            try:
                await ctx.message.delete(delay=5)
            except:
                pass
            # "You are missing Administrator permission(s) to run this command."
        if isinstance(e, commands.CommandOnCooldown):
            await ctx.send(f"{ERR} {e}.", delete_after=5)
            try:
                await ctx.message.delete(delay=5)
            except:
                pass
            # "You are on cooldown. Try again in _."
        if isinstance(e, commands.BadArgument):
            await ctx.send(f"{ERR} {e}", delete_after=5)
            try:
                await ctx.message.delete(delay=5)
            except:
                pass
            # "<argument> not found."
        elif isinstance(e, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f"{ERR} {e}", delete_after=5)
                # "This command cannot be used in private messages."
            except:
                pass
        if isinstance(e, commands.HelpCommand):
            await ctx.send(f"{ERR} {e}", delete_after=5)
            try:
                await ctx.message.delete(delay=5)
            except:
                pass        

if __name__ == '__main__':
    main()