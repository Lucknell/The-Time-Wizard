from discord.ext import commands
import discord
import os
import requests
from pymongo import MongoClient
from datetime import datetime


class AddEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class AddFlags(commands.FlagConverter):
        day: int = commands.flag(description="Day")
        month: int = commands.flag(description="Month")
        event_title: str = commands.flag(description="Event title")

    @commands.hybrid_command(name = "addevent", with_app_command = True, description ="Add an event")
    async def add_event(self, ctx: commands.Context, flags: AddFlags):
        try:
            datetime(month=flags.month,day=flags.day, year=datetime.now().year)
        except ValueError:
            return await ctx.send("Invalid date provided")
        client = MongoClient("mongodb://192.168.1.107:27016/")
        query = {"title": flags.event_title,
            "date": f"{flags.day:02d}-{flags.month:02d}-{datetime.now().year}",
            "server": ctx.guild.id
        }
        client["Joey"].calendar.insert_one(query)
        return await ctx.send(f"Added {flags.event_title}")


async def setup(bot):
    await bot.add_cog(AddEvent(bot))
