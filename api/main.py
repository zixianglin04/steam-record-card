# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 07/02/2025
# @Author  : Zixiang Lin
# @FileName: main.py


from fastapi import FastAPI, Response, Query
from fastapi.responses import PlainTextResponse
from generator_api import generate_svg_string

app = FastAPI()

@app.get("/card")
def generate_card(steam_id: str, appid: int):
    try:
        svg = generate_svg_string(appid, steam_id)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        return PlainTextResponse(f"Error: {str(e)}", status_code=500)

handler = app
