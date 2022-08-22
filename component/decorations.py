#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module containing small decorations class.

Authors:
    - Jonathan Shulgach
    - Max Murphy
"""
from tkinter import font, ttk


class Decorations(object):
    """Small class to track things like fonts and styles etc."""
    def __init__(self, app):
        self._font = {}
        app.loadtk()
        self._init_fonts(app)
        self.style = ttk.Style()
        self.style.configure('.', background="white", foreground="black")

    def addButtonStyle(self, style_dict: dict = None, map_dict: dict = None):
        """Set style for buttons on bottom row."""
        stylings = dict(background='white', font=self.font['TINY'], borderwidth=1)
        if style_dict is not None:
            stylings.update(**style_dict)
        self.style.configure('TButton', **stylings)
        mappings = dict(foreground=[('active', '!disabled', '#4cb87f'),
                                    ('!active', '!disabled', 'black')],
                        font=[('active', '!disabled', self.font['HOVERED']),
                              ('!active', '!disabled', self.font['TINY'])],
                        background=[('active', '!disabled', 'black'),
                                    ('!active', '!disabled', '#afa4a8')],)
        if map_dict is not None:
            mappings.update(**map_dict)
        self.style.map('TButton', **mappings)

    def addCheckboxStyle(self, style_dict: dict = None, map_dict: dict = None):
        """Set style for Checkboxes of boolean parameters."""
        stylings = dict(background='white', font=self.font['SMALL'])
        if style_dict is not None:
            stylings.update(**style_dict)
        self.style.configure('TCheckbutton', **stylings)
        mappings = dict(foreground=[('active', '#4cb87f'), ('!active', 'black')])
        if map_dict is not None:
            mappings.update(**map_dict)
        self.style.map('TCheckbutton', **mappings)

    def addComboBoxStyle(self, style_dict: dict = None, map_dict: dict = None):
        """Set style for Combobox of Dropdown parameters."""
        stylings = dict(background='white', font=self.font['SMALL'])
        if style_dict is not None:
            stylings.update(**style_dict)
        self.style.configure('TCombobox', **stylings)
        mappings = dict(foreground=[('active', '#4cb87f'), ('!active', 'black')])
        if map_dict is not None:
            mappings.update(**map_dict)
        self.style.map('TCombobox', **mappings)

    def addLabelStyle(self, font_name: str = 'HEADER', style_dict: dict = None, map_dict: dict = None):
        """Set style for Labels."""
        stylings = dict(background='white', font=self.font[font_name])
        if style_dict is not None:
            stylings.update(**style_dict)
        self.style.configure('TLabel', **stylings)
        mappings = dict(foreground=[('active', '#4cb87f'), ('!active', 'black')])
        if map_dict is not None:
            mappings.update(**map_dict)
        self.style.map('TLabel', **mappings)

    def addLabelFrameStyle(self, font_name: str = 'LABEL', style_dict: dict = None, map_dict: dict = None):
        """Set style for LabelFrames."""
        stylings = dict(background='white', font=self.font[font_name])
        if style_dict is not None:
            stylings.update(**style_dict)
        self.style.configure('TLabelframe', **stylings)
        mappings = dict(foreground=[('active', '#4cb87f'), ('!active', 'black')])
        if map_dict is not None:
            mappings.update(**map_dict)
        self.style.map('TLabelframe', **mappings)

    def addFrameStyle(self, font_name: str = 'LABEL', style_dict: dict = None, map_dict: dict = None):
        """Set style for Frames."""
        stylings = dict(bg='white', font=self.font[font_name])
        if style_dict is not None:
            stylings.update(**style_dict)
        self.style.configure('TFrame', **stylings)
        self.style.configure('TFrame.TLabelframe')
        mappings = dict(foreground=[('active', '#4cb87f'), ('!active', 'black')])
        if map_dict is not None:
            mappings.update(**map_dict)
        self.style.map('TFrame', **mappings)
        self.style.map('TFrame.TLabelframe')

    def addEntryStyle(self, font_name: str = 'LABEL', style_dict: dict = None, map_dict: dict = None):
        """Set style for Entry widgets."""
        stylings = dict(background='white', font=self.font[font_name])
        if style_dict is not None:
            stylings.update(**style_dict)
        self.style.configure('TEntry', **stylings)
        mappings = dict(foreground=[('active', '#4cb87f'), ('!active', 'black')])
        if map_dict is not None:
            mappings.update(**map_dict)
        self.style.map('TEntry', **mappings)

    def addSpinBoxStyle(self, style_dict: dict = None, map_dict: dict = None):
        """Set style for Spinbox of scalar parameters."""
        stylings = dict(background='white', font=self.font['SMALL'])
        if style_dict is not None:
            stylings.update(**style_dict)
        self.style.configure('TSpinbox', **stylings)
        mappings = dict(foreground=[('active', '#4cb87f'), ('!active', 'black')])
        if map_dict is not None:
            mappings.update(**map_dict)
        self.style.map('TSpinbox', **mappings)

    @property
    def font(self):
        """This is the "store" for the actual .font property."""
        return self._font

    @font.setter
    def font(self, value: tuple) -> None:
        """Sets `font` property.

        Args:
            value (tuple): Should be of the form (name, {param1: val1, ..., etc.})
        """
        name = value[0]
        p = value[1]
        if name not in self._font.keys():
            self._font[name] = font.Font(**p, name=name)

    def _init_fonts(self, app) -> None:
        """Initialize fonts property."""
        self.font = ('LARGE', dict(root=app, family='Verdana', size=36, weight='bold'))
        self.font = ('HEADER', dict(root=app, family='Verdana', size=24, weight='bold'))
        self.font = ('MEDIUM', dict(root=app, family='Verdana', size=24))
        self.font = ('HOVERED', dict(root=app, family='Verdana', size=14, weight='bold'))
        self.font = ('SMALL', dict(root=app, family='Verdana', size=12))
        self.font = ('LABEL', dict(root=app, family='Verdana', size=12, weight='bold'))
        self.font = ('TINY', dict(root=app, family='Verdana', size=10, slant='italic'))
