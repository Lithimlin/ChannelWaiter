## Description
This is a bot to temporarily create voice channels for a limited number of users.

## Using the bot
If can be added to a server using this link:
https://discord.com/api/oauth2/authorize?client_id=793804339256492062&permissions=93264&scope=bot

Currently, there are 3 commands available:
```
t!setup - setup the bot for the current server. Should only be called once.
          Currently, this command can be called by anyone so anyone could theoretically change the setup.

t!open X - open a new temporary voice channel for X users.

t!resize X - resize the current temporary voice channel to X users.
```

## Hosting it yourself
If you want to host it yourself, follow these steps:
  1. create a file called `.env` and add the following line to it:
```
DISCORD_TOKEN=<ADD YOUR TOKEN HERE!>
```
  2. Open a new python 3 environment using `python3 -m venv env`
  3. Activate the environment with `source env/bin/activate`
  4. Install the modules from `requirements.txt` using `pip install -r requirements.txt`
  5. Finally, run the bot using `python run.py`
