import os
import requests
import threading
import logging
import json
from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from discord.ext.ipc import Client
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from pymongo import MongoClient

app = Quart(__name__)
ipc_client = Client(secret_key = os.getenv("SECRET_KEY"), host="0.0.0.0", standard_port=1026)
app.asgi_app = ProxyHeadersMiddleware(app.asgi_app, trusted_hosts=["192.168.1.1"])
app.secret_key = b"thisisatestofwill"
app.config["DISCORD_CLIENT_ID"] = os.getenv("CLIENT")   # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("SECRET")   # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = os.getenv("CALLBACK")

discord = DiscordOAuth2Session(app)

@app.route("/")
async def home():
    return await render_template("index.html", authorized = await discord.authorized)

@app.route("/login")
async def login():
    return await discord.create_session()

@app.route("/callback")
async def callback():
    try:
        await discord.callback()
    except Exception:
        pass
    return redirect(url_for("dashboard"))

@app.route("/dashboard/")
@app.route("/dashboard")
async def dashboard():
    print(await discord.authorized)
    if not await discord.authorized:
        return redirect(url_for("login"))
    guild_count = int((await ipc_client.request("get_guild_count")).response)
    guild_ids_req = await ipc_client.request("get_guild_ids")
    logging.info(guild_ids_req)
    guild_ids = guild_ids_req.response["guild_ids"]
    user_guilds = await discord.fetch_guilds()
    guilds = []
    for guild in user_guilds:
        guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
        guilds.append(guild)
    guilds.sort(key = lambda x: x.class_color == "red-border")
    user = await discord.fetch_user()
    name = user.name
    return await render_template("dashboard.html", guild_count = guild_count, guilds = guilds, username=name)

@app.route("/dashboard/<int:guild_id>")
async def dashboard_server(guild_id):
    if not await discord.authorized:
        return redirect(url_for("login"))

    user = await discord.fetch_user()
    name = user.name
    guild = (await ipc_client.request("get_guild", guild_id = guild_id, user_id = user.id)).response
    print(user, name)
    if guild is None:
        return "I am not in that server"
    if not guild["has_user"]:
        return "You don't exist..."
    client = MongoClient("mongodb://192.168.1.107:27016/")
    events = []
    calendar_events = client["Joey"].calendar.find({"server": guild_id})
    for event in calendar_events:
        print(event)
        events.append({"title": event["title"], "date": event["date"]})
    return await render_template("calendar.html", guild_id = guild_id, events = json.dumps(events))

if __name__ == "__main__":
    app.run(debug=True)
