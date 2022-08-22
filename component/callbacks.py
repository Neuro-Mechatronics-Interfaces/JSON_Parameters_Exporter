#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module containing callbacks for different widgets.

Authors:
    - Jonathan Shulgach
    - Max Murphy
"""


class Callbacks:
    """Collection of widget callbacks."""
    def __init__(self, **kwargs):
        self._p = kwargs

    def show_clicked_image(self, event):
        """Callback to show different image on click."""
        event.widget.config(image=self._p['clicked'])

    def show_base_image(self, event):
        """Callback to show different image by default."""
        event.widget.config(image=self._p['base'])

    def show_hovered_image(self, event):
        """Callback to show different image on hover."""
        event.widget.config(image=self._p['hovered'])
