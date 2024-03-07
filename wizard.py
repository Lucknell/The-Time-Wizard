import os
import sys
import time
import discord
import logging
import asyncio
import requests

from typing import Literal
from datetime import datetime
from discord.utils import find
from discord import app_commands
from discord.ext import commands, ipc

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Bot(commands.Bot):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ipc_server = ipc.Server(self, secret_key=os.getenv("SECRET_KEY"), host="0.0.0.0", standard_port=1026)
        logger = logging.getLogger("discord")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "{asctime}: {levelname}: {name}: {message}", style="{"))
        logger.addHandler(handler)


    async def setup_hook(self):
        files = os.listdir("/src/bot/cogs/")
        for f in files:
            if f.endswith(".py"):
                await self.load_extension("cogs." + f.replace(".py", ""))
                print(f)
        await self.tree.sync()
        print(f"Synced Slash commands for {self.user}.")

    async def on_ipc_ready(self):
        print("I just wanna talk")
        
    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)
        
    async def on_ready(self):
        logging.info("The time wizard")

    async def on_command_error(self, ctx, error):
        if ctx.interaction:
            await ctx.reply(error, ephemeral = True)
    
client = Bot(command_prefix = None, intents = intents)
        
@client.ipc_server.route()
async def get_guild_count(fake, data):
    return str(len(client.guilds))

@client.ipc_server.route()
async def get_guild_ids(fake, data):
    final = []
    for guild in client.guilds:
        final.append(guild.id)
    return {"guild_ids":final}

@client.ipc_server.route()
async def get_guild(fake, data):
    guild = client.get_guild(data.guild_id)
    has_user = guild.get_member(data.user_id) is not None
    if guild is None: return None
    guild_data = {
        "name": guild.name,
        "id": guild.id,
        "has_user": has_user
    }
    return guild_data

async def main():
    async with client:
        await client.ipc_server.start()
        logging.info("Starting bot")
        await client.start(os.getenv('TOKEN'))
        avatar_path = "/src/bot/avatar.png"
        with open(avatar_path, 'rb') as image:
            client.wait_until_ready() 
            client.user.edit(avatar=image.read())

asyncio.run(main())