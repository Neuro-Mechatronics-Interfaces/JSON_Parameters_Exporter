#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module that defines project root folder etc.

Authors:
    - Jonathan Shulgach
    - Max Murphy
"""
from os import path
from sys import platform


ROOT_DIR = path.dirname(path.abspath(__file__))
ASSETS_DIR = path.join(ROOT_DIR, "assets")
ADD_BUTTON_FILE = {
    "base": path.join(ASSETS_DIR, "add.svg"),
    "hovered": path.join(ASSETS_DIR, "add_hover.svg"),
    "clicked": path.join(ASSETS_DIR, "add_click.svg")
}
DEFAULT_ICON_FILE = path.join(ASSETS_DIR, "CMU_Tartans.png")
DEFAULT_LAYOUTS_DIR = path.join(ROOT_DIR, "default_layouts")
DEFAULT_PARAMETERS_DIR = path.join(ROOT_DIR, "default_parameters")
DEFAULT_PARAMETERS_FILE = "params_Spencer-MID.json";
SAVED_PARAMETERS_DIR = path.join(ROOT_DIR, "saved_parameters")
