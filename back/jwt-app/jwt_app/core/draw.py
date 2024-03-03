# -*- coding: utf-8 -*-
import io

import cv2
import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont

FILE_WAY = "./core/refresh{}.png"
font_path = "./core/fonts/Roboto-Black.ttf"


def make_ticket(refr: str, num: str = "1"):
    file_name = "refresh{}.png".format(num)
    img = Image.open(FILE_WAY.format(num))
    tim = Image.new("RGBA", (1500, 1400), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tim)

    ticket_point = {
        "refresh1.png": {
            "cord": (300, 10),
            "entity": refr.upper(),
            "text": ImageFont.truetype(font_path, size=36),
            "color": ImageColor.colormap["black"],
            "angle": 55,
        },
        "refresh2.png": {
            "cord": (720, 430),
            "entity": refr.upper(),
            "text": ImageFont.truetype(font_path, size=36),
            "color": ImageColor.colormap["black"],
            "angle": 97,
        },
        "refresh3.png": {
            "cord": (320, 620),
            "entity": refr.upper(),
            "text": ImageFont.truetype(font_path, size=36),
            "color": ImageColor.colormap["black"],
            "angle": -7,
        },
        "refresh4.png": {
            "cord": (660, 110),
            "entity": refr.upper(),
            "text": ImageFont.truetype(font_path, size=38),
            "color": ImageColor.colormap["black"],
            "angle": 45,
        },
    }
    draw.text(
        ticket_point[file_name]["cord"],
        ticket_point[file_name]["entity"],
        font=ticket_point[file_name]["text"],
        fill=ticket_point[file_name]["color"],
    )
    tim = tim.rotate(ticket_point[file_name]["angle"], expand=1)

    if num == "1":
        img.paste(tim, (0, -370), tim)
    if num == "2":
        img.paste(tim, (0, 0), tim)
    if num == "3":
        img.paste(tim, (0, -100), tim)
    if num == "4":
        img.paste(tim, (0, -200), tim)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    jpg_file_path = "refresh_res.jpeg"
    data = np.frombuffer(byte_im, np.uint8)
    png_img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    res, encode_param = cv2.imencode(
        jpg_file_path, png_img, [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    )
    return bytes(encode_param)
