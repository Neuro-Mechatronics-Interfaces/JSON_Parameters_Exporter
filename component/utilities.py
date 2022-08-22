#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module miscellaneous utility functions & classes.

Note:
    - Still a work in progress (2021-03-14).

Authors:
    - Jonathan Shulgach
    - Max Murphy
"""
import json
import cairosvg
import io
from sys import platform
from component.callbacks import Callbacks
from definitions import ROOT_DIR
from tkinter import Tk, Label, ttk, LabelFrame, Frame
from PIL import Image, ImageTk  # (Pillow)
from os import path
from time import sleep


def app_check(obj: object, app: object, alt_class=None) -> object:
    """
    Args:
        obj (object):
        app (object):
        alt_class:
    """
    if app is None:
        if alt_class is None:
            raise TypeError('No alternative app class supplied.')
        else:
            root = Tk()
            return alt_class(app=root)
    else:
        return app


def check_for_file(filename: str, sleep_time: float = 0.5, n_retries: int = 5) -> bool:
    """Check existence of a file with known path/name.

    Args:
        filename (str): Name of the file to check with full filepath and extension.
        sleep_time (float): (Optional | default 0.5 sec) duration to sleep on each check interval.
        n_retries (int): (Optional | default 5 attempts) number of attempts to re-check for file.
    Returns:
        ready (bool): True if the file exists, False if not.
    """
    sleep(sleep_time)
    ready = path.exists(filename)
    counter = 0
    while (counter < n_retries) and not ready:
        sleep(sleep_time)
        ready = path.exists(filename)
        counter += 1
    return ready


def gen_range(stop: int, start: int = 0, step: int = 1) -> tuple:
    """Returns a tuple with a range and fixed increment size.

    :param stop: The value you want the tuple to count to.
    :param start: (Optional) the value to start counting from (default is zero).
    :param step: (Optional) the count step size (default is one).
    :type stop: int
    :type start: int
    :type step: int
    :returns: Tuple of the range between start and stop incremented by step.
    :rtype: tuple
    """
    return tuple(range(start, stop, step))

def json_array_2_params_property(file) -> dict and str or None and str or None:
    """Convert array structure from spencer.json into property field value.
    :param file: The *.json parameters file.
    :type file: SupportsRead[Union[str, bytes]]
    :returns: Parameters dict as would be used in the Parameters UI main property field, and associated layout file name
    :rtype: dict and str or None and str or None
    """
    array_form = json.load(file)
    params = array_form['parameters']  # Handles both lists and dict format parameters.
    if type(params) is list:
        parameters = {}
        for p in params:
            parameters[p['Name']] = p
    else:
        parameters = array_form['parameters']
    layout = None
    if 'layout' in array_form.keys():
        layout = array_form['layout']
        layout = fix_path(layout)
    icon_file = None
    if 'icon' in array_form.keys():
        icon_file, _ = path.splitext(array_form['icon'])
        icon_file = fix_path(path.join('assets', icon_file)) + ".png"
    return parameters, layout, icon_file

def fix_path(f: str) -> str:
    """Prepend the project root path to the file path string.
    :param f: A relative file path string.
    :type f: str
    :rtype: str
    :returns: The same file as f but with the full path prepended.
    """
    return path.abspath(f)

def get_photo_image(file: dict) -> dict:
    """Convert image filename dict into output dict of PhotoImage objects.

    :param file: The dict from definitions.py for Images, for example.
    :type file: dict
    :returns: Image dict
    :rtype: dict
    """
    img = {}
    for (k, v) in file.items():
        image_data = cairosvg.svg2png(url=v)
        image = Image.open(io.BytesIO(image_data))
        img[k] = ImageTk.PhotoImage(image)
    return img

def add_image_button(master, images: dict):
    """Add ui pushbutton-like label """
    cb = {"btn": Callbacks(**images)}
    btn = Label(master=master, image=images['base'])
    btn.pack(expand=False, side="top")
    btn.bind("<Button>", cb['btn'].show_clicked_image)
    btn.bind("<Leave>", cb['btn'].show_base_image)
    btn.bind("<Enter>", cb['btn'].show_hovered_image)
