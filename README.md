# Arena Bot

This is a Discord Bot that plays an arena battle minigame.
Refer to the how to play pdf on what it's about

## Setup

- In the [Discord developer portal](https://discord.com/developers/applications) create a new application and give it a name. Under `Bot` select "add bot"
- Under `Bot`, turn on PRESENCE INTENT, SERVER MEMBERS INTENT and MESSAGE CONTENT INTENT
- Generate an invite link for your bot under `QAuth2 > URL Generator`, with "bot" > "manage roles", "read messages/view channels", "send messages", "use external emojis" and "add reactions" permissions
- Use the invite link in your browser to invite your bot to your server
- Download the `arenabot` folder to your environment, the one with the `__main__.py` file, `.env` file and `cogs` folder
- Install python 3+. Make sure you have set Python to the system path
- Install dependencies with `pip install REQUIREMENTS.txt`
- You can change the bot prefix in the `__main__.py` file
- Rename the file `.env.example` to `.env`. Make sure the file is called `.env` and _not_ ".env.txt"
- Back in the developer portal, under `Bot`, copy your bot's secret token. In your `.env` file, replace the "a" with your secret token. Save the file.
- Similarly, you will need to get your Google Sheets client's [private_key and client_email](https://www.python-engineer.com/posts/google-sheets-api/) from your generated credentials json file and put these things in your `.env` file
- Create a new Google Sheet and give the Google Client editor access. Then create a header row with the following values: `UserID, Username, Combatant, AT, IN, DF, AR, HP, SP, EN, Wins, Ability 1, Ability 2, Weapon, Image`
- Get your workbook key by copying the URL of your Google Sheets spreadsheet between the `d/` and the `/edit` and paste it into the `constants.py` file under `WORKBOOK_KEY`
- Run it as a module with `python arenabot`, or `sudo nohup python3 arenabot` or whatever command you use to run python scripts in your environment; or directly run the `__main__.py` file. Congratulations, you are now self-hosting a discord bot
- You might need to turn on all intents in the developer portal or change the bots intents in the `__main__.py` file
- If you do not want to self-host, I suggest using Heroku or [Fly.io](https://fly.io/docs/getting-started/)
