# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 07/02/2025
# @Author  : Zixiang Lin
# @FileName: generator_api.py


import os
import requests
import base64
from io import BytesIO
from PIL import Image


def get_game_info(appid, STEAM_ID, API_KEY):
    api_url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={API_KEY}&steamid={STEAM_ID}&include_appinfo=true'
    res = requests.get(api_url).json()
    games = res.get('response', {}).get('games', [])
    for game in games:
        if game['appid'] == appid:
            name = game['name']
            playtime_h = round(game['playtime_forever'] / 60, 1)
            user_url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?key={API_KEY}&steamid={STEAM_ID}&appid={appid}"
            user_data = requests.get(user_url).json()
            if user_data.get("playerstats", {}).get("success") != True:
                return name, playtime_h, None
            achievements = user_data["playerstats"].get("achievements", [])
            unlocked = sum(1 for a in achievements if a.get("achieved") == 1)
            schema_url = f"https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={API_KEY}&appid={appid}"
            schema_data = requests.get(schema_url).json()
            total = len(schema_data.get("game", {}).get("availableGameStats", {}).get("achievements", []))
            if total == 0:
                return name, playtime_h, None
            completion = round((unlocked / total) * 100, 1)
            return name, playtime_h, completion
    return None, None, None


def fetch_image_base64(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content)).convert("RGB")
    image = image.resize((460, 215))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def generate_svg(appid, STEAM_ID, API_KEY):
    name, playtime_h, achievement_pct = get_game_info(appid, STEAM_ID, API_KEY)
    if name is None:
        print(f"❌ ID {appid}: No game found!")
        return
    image_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
    output_file = f"./svg/{appid}-{name}.svg"
    img_b64 = fetch_image_base64(image_url)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="460" height="215">
    <style>
        .stat {{
            font: 32px "American Typewriter", cursive;
            fill: white;
            stroke: black;
            stroke-width: 3px;
            paint-order: stroke fill;
        }}
        .shadow {{
            font: 32px "American Typewriter", cursive;
            fill: black;
            opacity: 0.4;
            font-weight: regular;
        }}
    </style>

    <!-- Background image -->
    <image href="data:image/png;base64,{img_b64}" x="0" y="0" width="460" height="215" />

    <!-- Text -->
    <text x="10" y="205" class="shadow">⏳️ {playtime_h}h</text>
    <text x="10" y="205" class="stat">⏳️ {playtime_h}h</text>
    '''

    if achievement_pct is not None:
        svg += f'''
        <text x="450" y="205" class="shadow" text-anchor="end">{achievement_pct}% 🏆</text>
        <text x="450" y="205" class="stat" text-anchor="end">{achievement_pct}% 🏆</text>
        '''

    svg += '</svg>'

    return svg


def generate_svg_string(appid, STEAM_ID):
    API_KEY = os.getenv("STEAM_API_KEY")
    return generate_svg(appid, STEAM_ID, API_KEY)
