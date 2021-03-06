# Discord bot project template
##### *Start your discord.py bot projects quicker*
This is a template repository you may fork in order to start your discord bot project quicker. This takes care of all
the setup and project structure for you.

Although this template currently works as intended, it is not in a completed state. All crossed out features are
currently not implemented.

## Features list
- Nice and modern discord rewrite class based file structure (notice the cogs folder)
- Clean, commented, and easy to understand code
- Built in config file that is easily modifiable and has easy to write type conversions for less verbose config calls
- Useful already built in functions in utils folder
- Built in basic commands, such as ping, ~~help, and common admin commands~~
- Auto generating help text for failed commands showing intended syntax
- Built in song bot functionality, because it's never a complete bot without music and it's a pain of a feature to add. Includes support for searching youtube, adding spotify/youtube playlists, and all the little things you'd expect like shuffle, repeat, play, pause, etc
- ~~Built in per-user sql lite database, so you can easily store user to user data~~

## Dependencies
1. Install all python package requirements from the requirements.txt file  
`pip3 install -r requirements.txt`

2. Install required dependencies for voice support (linux only)  
`apt install libffi-dev libnacl-dev python3-dev`

## Setup
1. Create an app at https://discord.com/developers/applications
2. Navigate to the `bot` section in your new application
3. Add a bot and obtain it's `token` (don't share your token with anyone, this is essentially it's password)
4. Set environment variable `TOKEN` to your discord bot's `token`. Run the following commands to do so in your python console
`import os`  
`os.environ["TOKEN"] = (your token here)`
Running main.py should now successfully start up your discord bot
Music bot functionality requires additionally installing ffmpeg

## Inviting your bot to your server
1. Under your application at https://discord.com/developers/applications, navigate to the `OAuth2` section
2. Under `scopes` enable `bot` and save the provided link
3. Navigate to the `Bot` section, scroll down to the bot permissions, and enable whichever permissions you wish to grant your
bot
4. With the link obtained in step 2, replace the number following `permissions=` with the `permissions integer` obtained
in step 3. You may not visit this link in order to add your bot to your server

## File structure
Different sets of commands are stored under separate files in the `cogs` folder, at startup all cogs will be loaded. See
file `/cogs/example.py`. useful "utility" files are stored under the `utils` folder. All utility files included with this
template have docstrings, so don't be afraid to explore the utils files!