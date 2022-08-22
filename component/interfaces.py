#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module containing building blocks for interface layouts.

Authors:
    - Jonathan Shulgach
    - Max Murphy
"""
from definitions import DEFAULT_ICON_FILE, ADD_BUTTON_FILE
from tkinter import ttk, Tk, Event, Frame, Toplevel, Label, PhotoImage
from tkinter import CENTER, N, S, E, W, StringVar
from component.arg_formats import buttonsFormat, buttonsIndexFormat
from component.decorations import Decorations
from component.utilities import get_photo_image
from component.callbacks import Callbacks

app = Tk()
myDecorations = Decorations(app)


class ParentWindow(Toplevel):
    """Window that is the main 'app' class."""

    def __init__(self,
                 master: app = None,
                 title: str = "Task",
                 width: int = 1028,
                 height: int = 720,
                 icon_file: str = DEFAULT_ICON_FILE,
                 notebooks: dict = None,
                 **kwargs):
        """Constructor for generic Window class.

        :param master: The main application.
        :param title: The name that will go in the top-left of window.
        :param width: Number of pixels wide.
        :param height: Number of pixels high.
        :param icon_file: Path to icon *.ico file.
        :param notebooks: (Optional) Dict of all notebooks if they already exist.
        :param kwargs: (Optional) Keyword parameters dictionary for Toplevel
        :type master: app or None
        :type title: str
        :type width: int
        :type height: int
        :type icon_file: str
        :type notebooks: dict or None
        :type kwargs: str or int or dict or None

        .. seealso:: tkinter.Tcl, tkinter.Toplevel, Pane, component.layout.ParametersWindow
        """
        if master is None:
            master = app

        super(ParentWindow, self).__init__(master=master, width=width, height=height, **kwargs)
        self.wm_title(title)
        self.setGeometry(width, height)
        self.title = title
        self.width = width
        self.height = height
        self.icon_file = icon_file
        self.master.iconphoto(False, PhotoImage(file=self.icon_file))
        self.iconphoto(False, PhotoImage(file=self.icon_file))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.loadNotebooks(notebooks)
        
    def loadNotebooks(self, notebooks):
        """Loads all specified notebooks."""
        self.notebooks = {}
        if notebooks is not None:
            for nb in notebooks.values():
                self._addNotebook(pane=nb)

    def _addNotebook(self,
                    pane=None,
                    title: str = "Untitled Notebook",
                    width: int = None,
                    height: int = None,
                    **kwargs):
        """Adds a notebook to the top-level window.

        :param pane: (Optional) Can give notebook directly, in which case other parameters are ignored.
        :param title: Title of the notebook (serves as `key` in notebooks property dict of ParentWindow).
        :param width: (Optional) width of notebook.
        :param height: (Optional) height of notebook.
        :param kwargs: Other parameter options (see Pane class).
        :type pane: None or Pane or ttk.Notebook
        :type title: str
        :type width: None or int
        :type height: None or int
        :returns: None
        :rtype: Pane

        .. seealso:: Pane, tkinter.ttk.Notebook, ParentWindow, tkinter.Toplevel
        """
        if pane is not None:
            title = pane.title
            if title in self.notebooks.keys():
                raise Exception("That notebook (" + title + ") already exists!")
            kwargs.update(pane.toArgs())
            self.notebooks[title] = Pane(**kwargs)
        else:
            if width is None:
                width = self.winfo_width()
            if height is None:
                height = round(self.winfo_height() * 0.85)
            if title in self.notebooks.keys():
                raise Exception("That notebook (" + title + ") already exists!")
            self.notebooks[title] = Pane(master=self, title=title, width=width, height=height, **kwargs)
        self.notebooks[title].grid_rowconfigure(0, weight=1)
        self.notebooks[title].grid_columnconfigure(0, weight=1)
        self.bind("<Configure>", self.notebooks[title].on_resize)
        return self.notebooks[title]

    def setGeometry(self, width: int, height: int) -> None:
        """Set geometry of the window (pixels)."""
        geometry = str(round(width)) + "x" + str(round(height))
        self.geometry(geometry)

    def toArgs(self):
        """Convert properties to arguments for subclass constructor use.

        :returns: kwargs -style optional input arguments based on current property values.
        :rtype: dict
        """
        return dict(master=self.master,
                    title=self.title,
                    width=self.winfo_width(),
                    height=self.winfo_height(),
                    icon_file=self.icon_file,
                    notebooks=self.notebooks
                    )


class ChildWindow(ParentWindow):
    """Create a child 'copy' of `ParentWindow` or `ParentWindow`-subclassed Toplevel window."""

    def __init__(self, parent: ParentWindow):
        """Constructor for `ChildWindow` copies `ParentWindow` to create duplicate window.

        :param parent: The main window that this receives properties from and can update properties of.
        :type parent: ParentWindow

        .. seealso:: component.interfaces.ParentWindow, tkinter.Toplevel
        """
        kwargs = parent.toArgs()
        super(ChildWindow, self).__init__(**kwargs)


class Pane(ttk.Notebook):
    """A `Pane` is simply a ttk.Notebook holder for the ttk.Frame 'tabs' (`Page` objects)."""

    def __init__(self,
                 master: ParentWindow = None,
                 title: str = "Untitled Notebook",
                 width: int = None,
                 height: int = None,
                 padding: str = '10p',
                 pages: dict = None,
                 **kwargs):
        """Constructor for `Pane` class that holds the tabs.

        :param master: This is a window that the `Pane` (notebook) sits in.
        :param title: The name of the notebook serves as its reference key in .notebooks dict.
        :param width: Width (pixels)
        :param height: Height (pixels)
        :param padding: Padding (as a dimension)
        :param pages: (Optional) dict of all the pages in this `Pane`
        :param kwargs: Keyword arguments that can be used with `ttk.Notebook`.
        :type master: ParentWindow or Toplevel
        :type title: str
        :type width: int or None
        :type height: int or None
        :type padding: str
        :type pages: dict or None
        :type kwargs: dict
        :returns: None
        :rtype: None
        .. seealso:: tkinter.ttk.Notebook, ParentWindow, tkinter.Toplevel, Page, tkinter.Frame
        """
        if master is None:
            master = ParentWindow(master=app)
        if width is None:
            width = master.winfo_width()
        if height is None:
            height = master.winfo_height()
        args = dict(master=master, width=width, height=height, padding=padding)
        args.update(**kwargs)
        super(Pane, self).__init__(**args)
        self.title = title
        self.width = args['width']
        self.height = args['height']
        self.padding = args['padding']
        self.grid(row=0, column=0, sticky=(N, S, E, W))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.enable_traversal()
        self.pages = {}
        if pages is not None:
            for page in pages.values():
                self.addPage(page=page, copy=True)

    def addPage(self, page=None, copy=False, **kwargs) -> None:
        """Adds a page (tab) to the window.

        :param page: A `Page` object.
        :param copy: Default is False, set to True if this page is in ChildWindow object.
        :param kwargs: Keyword dict (see also: Page).
        :type page: Page or Frame or ttk.LabelFrame or ttk.Frame
        :type copy: bool
        :type kwargs: dict
        """
        if page is None:
            page = Page.create(master=self, **kwargs)
        elif copy:
            args = page.toArgs()
            kwargs.update(**args)
            page = Page.create(**kwargs)
        key = page.title
        if key in self.pages:
            msg = "The `Page` " + key + " already exists for `Window` " + self.title + "!"
            raise Exception(msg)
        else:
            page.grid(row=0, column=0, sticky=(N, S, E, W))
        self.pages[key] = page
        self.select(page)

    def on_resize(self, event):
        """Callback on resize events."""
        if issubclass(event.widget.__class__, ParentWindow):
            if (self.width != event.width) or (self.height != event.height):
                self.width = event.width
                self.height = event.height

    def toArgs(self):
        """Convert properties to arguments for subclass constructor use.

        :returns: kwargs -style optional input arguments based on current property values.
        :rtype: dict
        """
        return dict(master=self.master,
                    title=self.title,
                    width=self.width,
                    height=self.height,
                    padding=self.padding,
                    pages=self.pages
                    )


class Page(Frame):
    """Page that is comparable to a `tab` in Matlab.

    The `Page` class will serve as a container for any parameters
    configurator widgets. Any such widgets should go into a child `Panel`.

    Note:
        Page can only be constructed by the Pane.addPage() method.
    """
    init_key = object()

    @classmethod
    def create(cls,
               master,
               title: str = "Untitled Page",
               bg: str = "White",
               width: int = 1028,
               height: int = 720,
               wraplength: str = "14.0c",
               tooltip_character_width: int = 100,
               exit_command=None,
               buttons: buttonsFormat = None,
               button_types: buttonsFormat = None,
               **kwargs):
        """Static constructor to be called by Pane.addPage().

        :param master: The parent/master Pane (notebook) holding the page.
        :param title: The title of the page (serves as its `key`)
        :param bg: Background color
        :param width: Number of pixels wide that this page is.
        :param height: Number of pixels high that this Page is.
        :param wraplength: The length of the tooltip text line before it wraps around (as a dimension).
        :param tooltip_character_width: Number of characters wide the tooltip box is.
        :param exit_command: Command to add to "Exit Button".
        :param buttons: (Optional) dict referencing all button elements on `Page`.
        :param button_types: (Optional) dict referencing the type of each button in `buttons`
        :param kwargs: Parameter options for ttk.Frame
        :type master: Pane or app
        :type title: str
        :type bg: str
        :type width: int
        :type height: int
        :type wraplength: str
        :type tooltip_character_width: int
        :type exit_command: function or None or () -> None,
        :type buttons: buttonType or None
        :type button_types: buttonType or None
        :type kwargs: dict or None
        :returns: A `Page` that is essentially a "tab".
        :rtype: Page

        .. seealso:: Frame, Pane, Panel
        """
        return Page(key=cls.init_key,
                    master=master,
                    title=title,
                    wraplength=wraplength,
                    bg=bg,
                    width=width,
                    height=height,
                    tooltip_character_width=tooltip_character_width,
                    exit_command=exit_command,
                    buttons=buttons,
                    button_types=button_types,
                    **kwargs)

    def __init__(self, key: object, master,
                 title: str = "Untitled Page", wraplength='14.0c', bg="White",
                 width: int = 1028, height: int = 720, tooltip_character_width: int = 100,
                 buttons: buttonsFormat = None, button_types: buttonsFormat = None,
                 exit_command=None, **kwargs):
        """Constructor for `Page` object that is like a "tab" basically.

        :param key: Key to compare with Page.init_key
        :param master: Master Pane (or ttk.Notebook) to put the page on.
        :param title: Title of the Page (serves as its reference key)
        :param wraplength: The width of the tooltip text before it wraps to new line (as a dimension).
        :param bg: Background color
        :param width: Width of the Page in pixels
        :param height: Height of the Page in pixels.
        :param tooltip_character_width: Number of characters wide the tooltip box is.
        :param exit_command: (Optional) `Exit` pushbutton command function.
        :param buttons: (Optional) dict referencing all button elements on `Page`.
        :param button_types: (Optional) dict referencing the type of each button in `buttons`
        :param kwargs: Optional parameters dict for ttk.Notebook
        :type key: object
        :type master: ttk.Notebook or Pane
        :type title: str
        :type wraplength: str
        :type bg: str
        :type width: int
        :type height: int
        :type tooltip_character_width: int
        :type buttons: buttonsFormat
        :type button_types: buttonsFormat
        :type exit_command: function or None or () -> None
        :returns: __init__ should not return anything.
        :rtype: None

        Note:
            Constructor should be invoked from Page.create() method.

        .. seealso:: Page.create(), Pane.addPage(), ttk.Notebook, tkinter.Frame
        """
        assert key == Page.init_key, \
            "Pages must be created using Page.create(). \n" \
            " -> The preferred way is by using Pane.addPage()."
        args = dict(bg=bg, width=width, height=height)
        args.update(**kwargs)
        super().__init__(master=master, **args)
        if exit_command is None:
            w = self.winfo_toplevel()
            exit_command = w.destroy
        self.title, self.bg = title, bg
        self.width, self.height = width, height
        self.exit_command = exit_command
        self.panels = dict(Top=[], Bottom=[], Left=[], Right=[])
        self._top_bar = Frame(self, bg=bg, highlightbackground=bg)
        self.contents = Frame(self, bg=bg, highlightbackground=bg)
        self._bottom_bar = Frame(self, bg=bg, highlightbackground=bg)
        self.button_bar = Frame(self._bottom_bar, borderwidth=1, bg=bg, highlightbackground=bg)
        self._tooltip_bar = Frame(self._bottom_bar, relief='sunken', borderwidth=2, bg=bg, highlightbackground=bg)
        self.tooltip = Label(self._tooltip_bar,
                             text="",
                             bg='#d3d6d4',
                             bd=4,
                             fg="black",
                             font=myDecorations.font['TINY'],
                             width=tooltip_character_width,
                             wraplength=wraplength,
                             anchor=CENTER)
        self.buttons, self.button_types = {}, {}
        self._init_grid()
        if (buttons is not None) and (button_types is not None):
            for (k, btn) in buttons.items():
                args = btn.toArgs()
                btn_type = button_types[k]
                if btn_type == "Navigation":
                    self.addNavigation(**args)
                else:
                    self.addButton(**args)
        else:
            self.addButton(text="Exit", desc="Exit parameters interface.", command=self.exit_command)
        # Always finish constructor by using add to attach the Page to the master `Pane` (if it is a `Pane`)
        if self.master.__class__ in (Pane, ttk.Notebook):
            self.master.add(self, padding='0.1i', text=self.title)

    def addButton(self,
                  text: str = "Untitled Button",
                  desc: str = "",
                  command=None,
                  row: int = 0,
                  column_weight: int = 1,
                  min_width: int = 85,
                  tooltip: Frame = None,
                  **kwargs) -> None:
        """Add ui pushbutton to bottom-left of page.

        :param text: Text to go on the ui pushbutton.
        :param command: Function executed by the pushbutton.
        :param desc: Description of what the button does.
        :param row: The column that this navigation button goes into (default: 0).
        :param column_weight: The weight of the row that this button goes into (default: 1).
        :param min_width: The minimum number of pixels wide that this column (and effectively, widget) will be.
        :param tooltip: (Optional) Frame that will be where the tooltip text in `desc` is displayed.
        :param kwargs: (Optional) keyword arguments dict for StandardButton
        :type text: str
        :type command: function or None or () -> None
        :type desc: str
        :type row: int
        :type column_weight: int
        :type min_width: int
        :type tooltip: Frame
        :type kwargs: dict

        .. seealso:: ttk.Button, StandardButton, Panel, Page
        """
        if tooltip is None:
            tooltip = self.tooltip
        in_args = dict(text=text,
                       command=command,
                       desc=desc,
                       row=row,
                       column_weight=column_weight,
                       min_width=min_width,
                       kwargs=kwargs)
        self.buttons[text] = StandardButton(self.button_bar,
                                            command=command,
                                            text=text,
                                            desc=desc,
                                            in_args=in_args,
                                            tooltip=tooltip,
                                            **kwargs)
        self.button_types[text] = "Standard"
        myDecorations.addButtonStyle()
        self.button_bar.grid_columnconfigure(self._button_offset['Standard'],
                                             weight=column_weight,
                                             minsize=min_width)
        self.buttons[text].grid(row=row, column=self._button_offset['Standard'], sticky=(N, S, E, W))

    def addNavigation(self,
                      text: str,
                      command=None,
                      desc: str = "",
                      min_height: int = 50,
                      column: int = 0,
                      row_weight: int = 1,
                      **kwargs) -> None:
        """Add ui pushbutton to center of page.

        :param text: Text to go on the ui pushbutton.
        :param command: Function executed by the pushbutton.
        :param desc: Description of the navigation button.
        :param min_height: Minimum size of the configured row (pixels), effectively the button height.
        :param column: The column that this navigation button goes into (default: 0).
        :param row_weight: The weight of the row that this button goes into (default: 1).
        :param kwargs: (Optional) keyword parameter arguments dict for StandardButton
        :type text: str
        :type command: function or None or () -> None
        :type desc: str
        :type row_weight: int
        :type min_height: int
        :type column: int
        :type kwargs: dict
        :returns: None
        :rtype: None
        .. seealso:: StandardButton, Panel, Page, tkinter.ttk.Button
        """
        in_args = dict(text=text,
                       command=command,
                       desc=desc,
                       column=column,
                       row_weight=row_weight,
                       min_height=min_height,
                       kwargs=kwargs)
        self.buttons[text] = StandardButton(master=self.contents,
                                            command=command,
                                            tooltip=self.tooltip,
                                            desc=desc,
                                            text=text,
                                            in_args=in_args,
                                            **kwargs)
        self.button_types[text] = "Navigation"
        myDecorations.addButtonStyle()
        self.contents.grid_rowconfigure(self._button_offset['Navigation'],
                                        weight=row_weight,
                                        minsize=min_height)
        self.buttons[text].grid(row=self._button_offset['Navigation'], column=column, sticky=(N, S, E, W))

    def addTaskHeader(self, text: str, textvariable: StringVar, anchor=CENTER) -> ttk.Label:
        """Add header label to Contents part of page.

        :param text: Text that will initially populate the label.
        :param textvariable: Variable that updates the label.
        :param anchor: One of: tkinter.E, tkinter.W, or tkinter.CENTER.
        :type text: str
        :type textvariable: StringVar
        :type anchor: E or W or CENTER
        :returns: Graphic for the header that changes with Task.
        :rtype: ttk.Label
        """
        h = ttk.Label(self._top_bar,
                      text=text,
                      textvariable=textvariable,
                      font=myDecorations.font['HEADER'],
                      anchor=anchor)
        myDecorations.addLabelStyle()
        textvariable.set(text)
        # h.grid(row=0, column=self._button_offset['Navigation'], sticky=(N, S, E, W))
        h.grid(row=0, column=2, sticky=(N, S, E, W))
        images = get_photo_image(ADD_BUTTON_FILE)
        cb = {"btn": Callbacks(**images)}
        btn = Label(master=self._top_bar, image=images['base'])
        btn.grid(row=0, column=0, sticky=(N, W))
        btn.bind("<Button>", cb['btn'].show_clicked_image)
        btn.bind("<Leave>", cb['btn'].show_base_image)
        btn.bind("<Enter>", cb['btn'].show_hovered_image)
        return h

    def toArgs(self):
        """Convert properties to arguments for subclass constructor use.

        :returns: kwargs -style optional input arguments based on current property values.
        :rtype: dict
        """
        return dict(master=self.master,
                    title=self.title,
                    width=self.width,
                    height=self.height,
                    buttons=self.buttons,
                    button_types=self.button_types
                    )

    def _init_grid(self):
        """Initialize the grid layout for the page."""
        # Make it fill the window (tab)
        self.grid(row=0, column=0, sticky=(N, S, E, W))
        # Just do everything as equally weighted columns and rows
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self._top_bar.grid(row=0, rowspan=1, column=0, columnspan=4, sticky=(N, S, E, W))
        self._top_bar.grid_rowconfigure(0, weight=1)
        self._top_bar.grid_columnconfigure(0, weight=1)
        self.contents.grid(row=1, rowspan=5, column=0, columnspan=4, sticky=(N, S, E, W))
        self.contents.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)
        self.contents.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._bottom_bar.grid(row=6, rowspan=1, column=0, columnspan=4, sticky=(N, S, E, W))
        self._bottom_bar.grid_rowconfigure(0, weight=1)
        self._bottom_bar.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.button_bar.grid(row=0, rowspan=1, column=0, columnspan=1, sticky=(N, S, E, W))
        self.button_bar.grid_rowconfigure(0, weight=1)
        self.button_bar.grid_columnconfigure(0, weight=1)
        self._tooltip_bar.grid(row=0, rowspan=1, column=1, columnspan=3, sticky=(N, S, E, W))
        self._tooltip_bar.grid_rowconfigure(0, weight=1, minsize=60)
        self._tooltip_bar.grid_columnconfigure(0, weight=1)
        self.tooltip.grid(row=0, column=0, columnspan=3, sticky=(N, S, E, W))

    @property
    def _button_offset(self) -> buttonsIndexFormat:
        """This dict contains indexing offset for each type of button."""
        n = dict(Standard=0, Navigation=0)
        for k in self.button_types.values():
            n[k] += 1
        return n


# noinspection PyUnusedLocal
class StandardButton(ttk.Button):
    """Button widget for holding `desc` property."""

    def __init__(self,
                 master=None,
                 command=None,
                 desc: str = "",
                 text: str = "Untitled Button",
                 in_args: dict = None,
                 tooltip: Label = None,
                 **kwargs):
        """Constructor for simple BottomButton class.

        :param master: Container for this button
        :param command: Function that the button executes.
        :param desc: Descriptor of what the button does.
        :param text: Text string that goes on the button.
        :param in_args: Dict of input arguments
        :param tooltip: (Optional) frame where the tooltip text in `desc` is displayed.
        :param kwargs: Parameter options for ttk.Button
        :type master: ttk.Frame or ttk.LabelFrame or Page or Panel
        :type command: function
        :type desc: str
        :type text: str
        :type in_args: dict
        :type tooltip: Label or ttk.Label
        :type kwargs: dict
        .. seealso:: ttk.Button, ttk.Frame, Page, Panel
        """
        args = dict(master=master, command=command, text=text)
        args.update(**kwargs)
        super().__init__(**args)
        self.desc = desc
        self.window = self.winfo_toplevel()
        self._tooltip = None
        self.tooltip = tooltip
        self._in_args = in_args

    def on_enter(self, event: Event = None) -> None:
        """Callback that occurs on hovering over a widget in the Panel.

        :param event: This is just here so that callback syntax works.
        :type event: Event
        """
        self.tooltip.configure(text=self.desc)

    def on_leave(self, event: Event = None):
        """Callback to remove tooltip when widget not hovered.

        :param event: This is just here so that callback syntax works.
        :type event: Event
        """
        del event
        self.tooltip.configure(text="")

    @property
    def tooltip(self):
        """Tooltip containing indicator of what the button does."""
        return self._tooltip

    @tooltip.setter
    def tooltip(self, value: ttk.Frame = None):
        """When tooltip property is set, configure binds for displaying it.

        :param value: The `tooltip` ttk.Frame that displays info about the hovered item.
        :type value: ttk.Frame
        .. seealso:: ttk.Frame
        """
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self._tooltip = value

    def toArgs(self) -> dict:
        """Return constructor arguments."""
        return self._in_args
