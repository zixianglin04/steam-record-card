# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 07/02/2025
# @Author  : Zixiang Lin
# @FileName: main.py


from fastapi import FastAPI, Response, Query
from generator_api import generate_svg_string

app = FastAPI()

@app.get("/card")
def generate_card(
    steam_id: str = Query(...),
    appid: int = Query(...)
):
    try:
        svg_data = generate_svg_string(appid, steam_id)
        return Response(content=svg_data, media_type="image/svg+xml")
    except Exception as e:
        return {"error": str(e)}