#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main entry point for module.
Authors:
    - Max Murphy
"""
# import json
from os import path
import tkinter as tk
from definitions import DEFAULT_PARAMETERS_DIR, DEFAULT_PARAMETERS_FILE
from component.parameters_ui import ParametersParentWindow, app


if __name__ == "__main__":
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)
    btn = tk.Button(master=app, text="EXIT", command=app.destroy)
    btn.grid()
    ParametersParentWindow(master=app, defaults_name=path.join(DEFAULT_PARAMETERS_DIR, DEFAULT_PARAMETERS_FILE))
    app.mainloop()
