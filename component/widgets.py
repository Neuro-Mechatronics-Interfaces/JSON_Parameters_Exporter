#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module containing classes that make parameter-type-specific interactive widgets.

Authors:
    - Jonathan Shulgach
    - Max Murphy
"""
from math import sqrt, floor, ceil
from pymitter import EventEmitter
from tkinter import ttk, Event, IntVar, StringVar
from tkinter import N, S, E, W, colorchooser    # TODO: add color selection interface compatibility
from component.interfaces import myDecorations
from component.utilities import gen_range

VALID_TYPES = ["Boolean",
               "Scalar",
               "Label",
               "Dropdown",
               "Array",
               "Tags",
               "DropdownTags",
               "Object"]


def parse_widget(master=None, tooltip=None, **kwargs):
    """Parse the correct type of widget to put in the container.

    :param master: The container that widget goes in.
    :param tooltip: The container that displays the Description of the widget parameter.
    :type master: None or Page or ttk.LabelFrame or ttk.Frame or Frame or LabelFrame
    :type tooltip: None or Page or ttk.LabelFrame or ttk.Frame or Frame or LabelFrame
    :returns: Widget control for adjusting parameters.
    :rtype: Union[ParamBoolean, ParamArray, ParamLabel, ParamScalar, ParamDropdown, ParamDropdownTags,
    .. ParamTags, ParamObject]
    """
    name = kwargs['name']
    p_type = kwargs['Type']
    if p_type == "Label":
        print("Handling `Label` parameter (" + name + ")...")
        entry_widget = ParamLabel(master=master,
                                  tooltip=tooltip,
                                  Name=name,
                                  Page=kwargs['Page'],
                                  Value=kwargs['Value'],
                                  Description=kwargs['Description'],
                                  font=kwargs['font'],
                                  layout=kwargs['layout'],
                                  emitter=kwargs['emitter'])
    elif p_type == "Tags":
        print("Handling `Tags` parameter (" + name + ")...")
        entry_widget = ParamTags(master=master,
                                 tooltip=tooltip,
                                 Name=name,
                                 Value=kwargs['Value'],
                                 Description=kwargs['Description'],
                                 Page=kwargs['Page'],
                                 font=kwargs['font'],
                                 layout=kwargs['layout'],
                                 emitter=kwargs['emitter'])

    elif p_type == "Array":
        print("Handling `Array` parameter (" + name + ")...")
        entry_widget = ParamArray(master=master,
                                  tooltip=tooltip,
                                  Name=name,
                                  Value=kwargs['Value'],
                                  Page=kwargs['Page'],
                                  Description=kwargs['Description'],
                                  Units=kwargs['Units'],
                                  font=kwargs['font'],
                                  layout=kwargs['layout'],
                                  emitter=kwargs['emitter'])

    elif p_type == "Scalar":
        print("Handling `Scalar` parameter (" + name + ")...")
        entry_widget = ParamScalar(master=master,
                                   tooltip=tooltip,
                                   Name=name,
                                   Value=kwargs['Value'],
                                   Page=kwargs['Page'],
                                   Description=kwargs['Description'],
                                   Units=kwargs['Units'],
                                   Bounds=kwargs['Bounds'],
                                   Increment=kwargs['Increment'],
                                   font=kwargs['font'],
                                   layout=kwargs['layout'],
                                   emitter=kwargs['emitter'])

    elif p_type == "Boolean":
        print("Handling `Boolean` parameter (" + name + ")...")
        entry_widget = ParamBoolean(master=master,
                                    tooltip=tooltip,
                                    Name=name,
                                    Value=kwargs['Value'],
                                    Description=kwargs['Description'],
                                    Page=kwargs['Page'],
                                    layout=kwargs['layout'],
                                    emitter=kwargs['emitter'])

    elif p_type == "Dropdown":
        print("Handling `Dropdown` parameter (" + name + ")...")
        entry_widget = ParamDropdown(master=master,
                                     tooltip=tooltip,
                                     Name=name,
                                     Value=kwargs['Value'],
                                     Page=kwargs['Page'],
                                     Description=kwargs['Description'],
                                     Options=kwargs['Options'],
                                     font=kwargs['font'],
                                     layout=kwargs['layout'],
                                     emitter=kwargs['emitter'])

    elif p_type == "DropdownTags":
        print("Handling `DropdownTags` parameter (" + name + ")...")
        entry_widget = ParamDropdownTags(master=master,
                                         tooltip=tooltip,
                                         Name=name,
                                         Value=kwargs['Value'],
                                         Page=kwargs['Page'],
                                         Description=kwargs['Description'],
                                         Options=kwargs['Options'],
                                         font=kwargs['font'],
                                         layout=kwargs['layout'],
                                         emitter=kwargs['emitter'])
    else:
        raise_type_error(v=p_type)
        return None  # to keep linter happy
    return entry_widget

def raise_type_error(all_valid_types: list = None, v: str = None) -> None:
    """Raise error (and optionally report bad given `Type`).

    :param all_valid_types: (Optional) list of allowable types.
    :param v: (Optional) The invalid `Type` (str) to report.
    :type all_valid_types: list
    :type v: str
    :rtype: None
    :returns: None
    """
    if all_valid_types is None:
        all_valid_types = VALID_TYPES
    msg = "Type must be one of: "
    for valid_type in all_valid_types:
        msg += valid_type + " | "
    if v is not None:
        msg += "(Type given was `" + v + "`)"
    raise Exception(msg)


class InputWidgets(object):
    """For type checks on .input property of ParamWidget."""
    def __init__(self,
                 String: ttk.Entry = None,
                 Bool: ttk.Checkbutton = None,
                 Dropdown: ttk.Combobox = None,
                 Spin: ttk.Spinbox = None,
                 Button: ttk.Button = None):
        """Creates the InputWidgets dict, effectively."""
        self.String = String
        self.Bool = Bool
        self.Dropdown = Dropdown
        self.Spin = Spin
        self.Button = Button
        self.StringValue = StringVar()
        self.BoolValue = IntVar()
        self.DropdownValue = StringVar()


class ParamJSONFormat(dict):
    """Class to define how parameters look in JSON file."""
    Name: str
    Type: str
    Page: str
    Value: any
    Description: str
    Options: list
    Bounds: list
    Increment: float or int

    def __init__(self,
                 Name: str = None,
                 Type: str = None,
                 Page: str = None,
                 Value: any = None,
                 Description: str = None,
                 Options: list = None,
                 Bounds: list = None,
                 Increment: float or int = None):
        """Class constructor defines the structure of parameter JSON objects.

        :param Name: Name of the parameter
        :param Type: "Type" of parameter.
        :param Page: The name of the page the parameter goes on.
        :param Value: The actual parameter value.
        :param Description: Description of what parameter is (for tooltip hover-info box).
        :param Options: If a dropdown is involved, this is a list of options.
        :param Bounds: If numbers are involved, this represents bounds on the range of possible values.
        :param Increment: If numbers are involved, this represents the step-size for clicking on spinbox arrows.
        :type Name: str
        :type Type: str
        :type Page: str
        :type Value: any
        :type Description: str
        :type Options: list
        :type Bounds: list
        :type Increment: float or int
        :rtype: None
        :returns: __init__ should return None

        Available Parameter Types:
            * 'Array'
            * 'Boolean'
            * 'Dropdown'
            * 'DropdownTags'
            * 'Label'
            * 'Object'
            * 'Scalar'
            * 'Tags'
        """
        kw = locals()
        kw.pop('self')
        super().__init__(**kw)


class ParamWidget(ttk.LabelFrame):
    """Superclass for Parameter widget."""
    def __init__(self,
                 master,
                 tooltip,
                 Type: str,
                 Name: str,
                 Page: str,
                 Description: str = "",
                 Units: str = None,
                 Options: list = None,
                 Bounds: list = None,
                 Increment: float or int = None,
                 layout: dict = None,
                 font: tuple = ('Verdana', 10),
                 emitter: EventEmitter = None,
                 **kwargs):
        """ Constructor for parameter widget superclass.

        :param master: (REQUIRED) Container that widget goes in.
        :param tooltip: (REQUIRED) Tooltip that displays the widget description.
        :param Type: (REQUIRED) Type of widget that this is.
        :param Name: (REQUIRED) Name of the parameter.
        :param Page: (REQUIRED) Page on which the parameter will go.
        :param Description: Description of the parameter for tooltip.
        :param Units: Units of the parameter (if applicable)
        :param Options: Possible choices for values of the parameter.
        :param Bounds: Lower and Upper bounds on numeric values of the parameter.
        :param Increment: Amount the spinbox increments or decrements the parameter each click.
        :param layout: Grid layout dict for where it should go in the container.
        :param font: Tuple containing the font specification for the label.
        :param emitter: The event emitter to use with listener callbacks.
        :param kwargs: Keyword parameter options for ttk.LabelFrame superclass constructor.
        :type master: Frame or LabelFrame or ttk.Frame or ttk.LabelFrame or Page or TypedPage
        :type tooltip: Frame or LabelFrame or ttk.Frame or ttk.LabelFrame or Page or TypedPage
        :type Name: str
        :type Type: str
        :type Page: str
        :type Description: str
        :type Units: str or None
        :type Options: list or None
        :type Bounds: list or None
        :type Increment: float or int or None
        :type layout: dict or None
        :type font: tuple
        :type emitter: EventEmitter or None
        :type kwargs: dict
        :rtype: None
        :returns: __init__ should not return anything.
        .. seealso:: ParamBoolean, ParamDropdown, ParamDropdownTags, ParamLabel, ParamObject, ParamScalar, ParamTags
        """
        if layout is None:
            layout = dict(column=0, row=0, sticky=(N, S, E, W))
        if Units is None:
            lab = ttk.Label(master, text=Name, font=font)
        else:
            lab = ttk.Label(master, text=Name + " (" + Units + ")", font=font)
        myDecorations.addLabelStyle('SMALL')
        super().__init__(master=master, labelwidget=lab, **kwargs)
        myDecorations.addLabelFrameStyle()
        self.tooltip = tooltip
        self.emitter = emitter
        self.grid(**layout)
        self.to_grid()
        self.input: InputWidgets = InputWidgets()
        self.name = Name
        self.type = Type
        self.page = Page
        self.desc = Description
        self._opts = Options
        self.opts = Options
        self.bounds = Bounds
        self.increment = Increment
        # Bind the widget area to the tooltip area for displaying descriptions.
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event: Event = None) -> None:
        """Callback that occurs on hovering over a widget in the Panel.

        :param event: Event object containing parameter description.
        :type event: Event
        :returns: None
        :rtype: None
        """
        if self.tooltip is not None:
            self.tooltip.configure(text=event.widget.desc)

    # noinspection PyUnusedLocal
    def on_leave(self, event: Event = None) -> None:
        """Callback to remove tooltip when widget not hovered.

        :param event: This is just here so that callback syntax works.
        :type event: Event
        :returns: None
        :rtype: None
        """
        del event
        if self.tooltip is not None:
            self.tooltip.configure(text="")

    def addCheckBox(self,
                    checked: bool = False,
                    layout: dict = None,
                    callback=None,
                    **kwargs) -> None:
        """Add text entry box to the widget layout.

        :param checked: Value to initialize the checkbutton to (default is False).
        :param layout: Grid layout dict for the input ttk.Entry. Should have 'row', 'column' and 'sticky' keys.
        :param callback: (Optional) Default callback is self.handle_emitter; should take (self, event) as args.
        :param kwargs: (Optional) Keyword arguments for ttk.Checkbutton.
        :type checked: bool
        :type layout: dict
        :type callback: None or function or () -> None
        :type kwargs: any
        :returns: None
        :rtype: None
        """
        if layout is None:
            layout = dict(row=0, column=0, sticky=(N, S, E, W))
        if callback is None:
            callback = self.handle_emitter
        self.input.Bool = ttk.Checkbutton(self, variable=self.input.BoolValue, **kwargs)
        myDecorations.addCheckboxStyle()
        self.input.Bool.grid(**layout)
        self.input.BoolValue.set(checked)
        self.input.Bool.bind("<Button>", callback)

    def addDropdown(self,
                    text: str = "",
                    opts: list = None,
                    font: tuple = ('Verdana', 12),
                    layout: dict = None,
                    callback=None,
                    **kwargs) -> None:
        """Adds dropdown menu with opts to the widget.

        :param text: Current (text) value from the list.
        :param opts: List with possible values to select.
        :param font: Tuple specifying ('FontName', FontPointSize)
        :param layout: Grid layout dict for ttk.Combobox. Should have 'row', 'column', 'columnspan' and 'sticky' keys.
        :param callback: (Optional) Default callback is self.handle_emitter; should take (self, event) as args.
        :param kwargs: (Optional) Keyword arguments for ttk.Combobox.
        :type text: str
        :type opts: list
        :type font: tuple
        :type layout: dict
        :type callback: None or function or () -> None
        :type kwargs: any
        :rtype: None
        :returns: None
        """
        if layout is None:
            layout = dict(row=0, column=0, columnspan=2, sticky=(N, S, E, W))
        if callback is None:
            callback = self.handle_emitter
        self.to_grid(n_rows=2, n_columns=2)
        self.grid_rowconfigure(0, weight=2)  # Make top row weighted more heavily (for dropdown vs. text entry button)
        self.input.Dropdown = ttk.Combobox(self,
                                           font=font,
                                           textvariable=self.input.DropdownValue,
                                           exportselection=0,
                                           **kwargs)
        myDecorations.addComboBoxStyle()
        self.input.Dropdown.grid(**layout)
        self.updateDropdown(v=text, o=opts)
        self.input.Dropdown.state(('readonly',))
        self.addPushTextEntry()
        self.input.Dropdown.bind("<<ComboboxSelected>>", callback)

    def addOption(self) -> None:
        """Add value from Entry widget to list of Combobox dropdown opts.

        :rtype: None
        :returns: None
        """
        opts = self.input.Dropdown['values']
        new_opts = []
        for opt in opts:
            new_opts.append(opt)
        new_opts.append(self.input.StringValue.get())
        self.input.Dropdown['values'] = new_opts
        self.input.Dropdown.current(len(new_opts) - 1)

    def addPushTextEntry(self,
                         font: tuple = ('Verdana', 12),
                         button_text: str = "Add",
                         entry_weight: int = 5,
                         row: int = 1) -> None:
        """Add combination of ttk.Entry and ttk.Button to specified row in columns (0, 1).

        :param font: Font tuple as ('FontName', FontPointSize)
        :param button_text: Text string that goes on the pushbutton.
        :param entry_weight: The weight of the text entry widget. Pushbutton is always weighted as 1.
        :param row: Which row should this combination of entry and button go into (int)
        :type font: tuple
        :type button_text: str
        :type row: int
        :type entry_weight: int
        :rtype: None
        :returns: None
        """
        self.grid_columnconfigure(0, weight=entry_weight)
        self.input.Button = ttk.Button(self, text=button_text, command=self.addOption)
        myDecorations.addButtonStyle()
        self.input.String = ttk.Entry(self, font=font, textvariable=self.input.StringValue)
        myDecorations.addEntryStyle()
        self.input.String.grid(row=row, column=0, sticky=(N, S, E, W))
        self.input.Button.grid(row=row, column=1, sticky=(N, S, E, W))

    def addSpinBox(self,
                   value: int or float,
                   font: tuple = ('Verdana', 12),
                   width: int = 4,
                   layout: dict = None,
                   callback=None,
                   **kwargs) -> None:
        """Add numeric spin box to the widget layout.

        :param value: Current (numeric) value to put in the spin box.
        :param font: Tuple specifying ('FontName', FontPointSize)
        :param width: The number of characters wide that this ttk.Spinbox should be.
        :param layout: Grid layout dict for the input ttk.Spinbox. Should have 'row', 'column' and 'sticky' keys.
        :param callback: (Optional) Default callback is self.handle_emitter; should take (self, event) as args.
        :param kwargs: (Optional) Keyword arguments for ttk.Spinbox.
        :type value: int or float
        :type font: tuple
        :type width: int
        :type layout: dict
        :type callback: None or function or () -> None
        :type kwargs: any
        :rtype: None
        :returns: None
        """
        if layout is None:
            layout = dict(row=0, column=0, sticky=(N, S, E, W))
        if callback is None:
            callback = self.handle_emitter
        self.input.Spin = ttk.Spinbox(self,
                                      font=font,
                                      width=width,  # Width is given in number of characters
                                      from_=self.bounds[0],
                                      to=self.bounds[1],
                                      increment=self.increment,
                                      **kwargs)
        myDecorations.addSpinBoxStyle()
        self.input.Spin.set(value)
        self.input.Spin.grid(**layout)
        self.input.Spin.bind("<Button>", callback)
        self.input.Spin.bind("<<Increment>>", callback)
        self.input.Spin.bind("<<Decrement>>", callback)
        self.input.Spin.bind("<FocusOut>", callback)

    def addTextEntry(self,
                     text: str = "",
                     font: tuple = ('Verdana', 12),
                     width: int = 30,
                     layout: dict = None,
                     callback=None,
                     **kwargs) -> None:
        """Add text entry box to the widget layout.

        :param text: String to put as default in textbox (default: "")
        :param font: Font tuple as ('FontName', FontPointSize)
        :param width: Number of characters wide the text entry box should be.
        :param layout: Grid layout dict for the input ttk.Entry. Should have 'row', 'column' and 'sticky' keys.
        :param callback: (Optional) Default callback is self.handle_emitter; should take (self, event) as args.
        :param kwargs: (Optional) Keyword arguments for ttk.Entry.
        :type text: str
        :type font: tuple
        :type width: int
        :type layout: dict
        :type callback: None or function or () -> None
        :type kwargs: any
        :returns: None
        :rtype: None
        """
        if layout is None:
            layout = dict(row=0, column=0, sticky=(N, S, E, W))
        if callback is None:
            callback = self.handle_emitter
        self.input.String = ttk.Entry(self, textvariable=self.input.StringValue, font=font, width=width, **kwargs)
        self.input.StringValue.set(text)
        self.input.String.grid(**layout)
        myDecorations.addEntryStyle()
        self.bind("<Key>", callback)

    # noinspection PyUnusedLocal
    def handle_emitter(self, event):
        """Handle changes to the parameter widget."""
        del event
        if self.emitter is not None:
            s = "parameter.updated.{p_type}.{p_name}".format(
                p_type=self.type.lower(),
                p_name=self.name
            )
            self.emitter.emit(s, self.to_dict())

    def to_dict(self) -> ParamJSONFormat:
        """Return value of the parameter as a dict.

        :returns: Value of this parameter widget as a dict (in input json format).
        :rtype: ParamJSONFormat
        """
        return ParamJSONFormat(Name=self.name,
                               Type=self.type,
                               Page=self.page,
                               Value=self.value,
                               Description=self.desc,
                               Options=self.opts,
                               Bounds=self.bounds,
                               Increment=self.increment)

    @staticmethod
    def compute_grid(n: int) -> (int, int):
        """Compute number of rows and columns in grid.

        :param n: Total number of elements to go in grid.
        :type n: int
        :rtype: (int, int)
        :returns: (n_rows, n_columns)
        """
        n_columns = floor(sqrt(n))
        n_rows = ceil(n / n_columns)
        return n_rows, n_columns

    def to_grid(self, n_rows: int = 1, n_columns: int = 1) -> None:
        """Configure the row and column grid layout of (main) widget.

        :param n_rows: Number of rows (ttk.LabelFrame) in widget grid layout.
        :param n_columns: Number of columns in widget (ttk.LabelFrame) grid layout.
        :returns: None
        :rtype: None
        """
        rows = gen_range(n_rows)
        columns = gen_range(n_columns)
        self.grid_rowconfigure(rows, weight=1)
        self.grid_columnconfigure(columns, weight=1)

    @staticmethod
    def to_args(arg_dict: dict, type_: str) -> dict:
        """Convert `locals` to arguments dict for this superclass.

        :param arg_dict: `locals()` called in subclass constructor.
        :param type_: 'Type' of the parameter (.type property).
        :type arg_dict: dict
        :type type_: str
        :returns: The converted arguments dict for superclass constructor.
        :rtype: dict

        Note:
            * This static method is used by subclasses in the superclass call in constructor.
            * `locals()` changes depending on where you call it within the function.
            * This static method simply removes `self` from the `locals()` dict keys.
        """
        if 'self' in arg_dict.keys():
            arg_dict.pop('self')
        if 'Value' in arg_dict.keys():
            arg_dict.pop('Value')
        if 'kwargs' in arg_dict.keys():
            kw = arg_dict.pop('kwargs')
            arg_dict.update(**kw)
        if arg_dict['layout'] is None:
            arg_dict['layout'] = dict(column=0, row=0, sticky=(N, S, E, W))
        args_out = {}
        for k in arg_dict.keys():
            if not str(k).startswith("_"):
                args_out[k] = arg_dict[k]
        args_out['Type'] = type_
        return args_out

    @staticmethod
    def str_2_list(txt: str or list) -> list or None:
        """Static method to convert comma-delimited string input to list.

        :param txt: Comma-delimited text (from input textbox). Each comma denotes a new list element.
        :type txt: str or list
        :returns: The "tags" list based on where the commas are.
        :rtype: list or None
        """
        if type(txt) is list:
            return txt
        out = []
        txt.strip(" ")
        if txt == "":
            return out
        if "," in txt:
            tokens = txt.split(sep=",")
        else:
            tokens = txt.split(sep="}")
            for i in range(len(tokens)):
                tokens[i] = tokens[i].strip(" {")
        for tag in tokens:
            out.append(tag.strip())
        return out

    @staticmethod
    def str_2_array(txt: str or list) -> list:
        """Convert comma-delimited string sequence of numbers to output list.

        :param txt: Comma-delimited string where each element is a numeric string value.
        :type txt: str or list
        :rtype: list
        :returns: An array (list) of float-converted values of the comma-delimited elements of input string.
        """
        if type(txt) is list:
            return txt
        txt.strip(" ")
        value = []
        if txt == "":
            return value
        tokens = txt.split(sep=",")
        for token in tokens:
            s = token.strip()
            value.append(float(s))
        return value

    @staticmethod
    def array_2_str(arr: list or str) -> str:
        """Static method to convert numeric array to comma-delimited string.

        :param arr: The numeric array (list) to convert.
        :type arr: list or str
        :rtype: str
        :returns: Comma-delimited text string representing numeric values in array.
        """
        if type(arr) is str:
            return arr
        str_values = [str(el) for el in arr]
        return ", ".join(str_values)

    @staticmethod
    def list_2_str(arr: list or str) -> str:
        """Static method to convert text array to comma-delimited string.

        :param arr: The text array (list) to convert.
        :type arr: list or str
        :rtype: str
        :returns: Comma-delimited text string representing numeric values in array.
        """
        if type(arr) is str:
            return arr
        str_values = [el for el in arr]
        return ", ".join(str_values)

    def updateDropdown(self, v: str, o: list) -> int:
        """Updates contents of dropdown box.

        :param v: Value (string) to set current list index to.
        :param o: Options (list) for available options.
        :type v: str
        :type o: list
        :rtype: int
        :returns: Index of list value that the current list string corresponds to.
        """
        if v not in o:
            o.append(v)
        if self.input.Dropdown is None:
            raise Exception("Cannot update Dropdown widget before it has been created!")
        self.input.Dropdown['values'] = o
        idx = o.index(v)
        self.input.Dropdown.current(idx)
        self.opts = o
        if self.input.String is not None:
            self.input.StringValue.set("")  # Clear the string Entry widget
        return idx

class ParamArray(ParamWidget):
    """Widget for parameters with 'Type'=='Array'"""
    def __init__(self,
                 master,
                 Name: str = "Untitled",
                 Value: list = None,
                 Description: str = "No description given.",
                 Units: str = "N/A",
                 layout: dict = None,
                 font: tuple = ('Verdana', 12),
                 emitter: EventEmitter = None,
                 **kwargs):
        """Constructor for `ParamArray` widget class.

        Args:
            master (Frame or ttk.Frame or ttk.LabelFrame or Page): (Optional) master container this widget goes in.
            Name (str): Name of parameter (str)
            Value (list): Default value of parameter (list of float values)
            Description (str): Description of this parameter (str)
            Units (str): Units for this numeric value (str)
            layout (dict): (Optional) Grid layout dict with `row` and `column` options.
            font (tuple): (Optional) Tuple ('Font', size),
            emitter (EventEmitter): (Optional) event emitter for handling updates.
            kwargs (any): Optional keyword arguments
        """
        if Value is None:
            Value = []
        args = self.to_args(locals(), type_="Array")
        super().__init__(**args)
        self.to_grid(n_rows=1, n_columns=1)
        self.addTextEntry(text=self.array_2_str(Value))

    @property
    def value(self) -> list:
        """Break apart input string using `,` and remove whitespace.
        :rtype: list
        :returns: Current value of Array-type parameter (list).
        Note:
            Elements are delimited by "," and are converted to float after
            tokens are found by splitting using "," delimiter.
        """
        return self.str_2_array(self.input.StringValue.get())

    @value.setter
    def value(self, v: dict or list = None) -> None:
        """Set the value of the parameter (and graphic).

        :param v: Dict with key 'Value' that is a list of float values.
        :type v: dict or list
        :returns: None
        :rtype: None
        """
        if v is None:
            self.input.StringValue.set("")
            return
        elif type(v) is dict:
            v = v['Value']
        self.input.StringValue.set(self.array_2_str(v))  # Concatenate the list using ", "


class ParamBoolean(ParamWidget):
    """Widget for parameters with 'Type'=='Label'"""
    def __init__(self,
                 master=None,
                 Name: str = "Untitled",
                 Value: bool = False,
                 Description: str = "No description given.",
                 layout: dict = None,
                 font: tuple = ('Verdana', 12),
                 emitter: EventEmitter = None,
                 **kwargs):
        """Constructor for `ParamBoolean` widget class.

        Args:
            master (Frame or ttk.Frame or ttk.LabelFrame or Page): master container (master) that this widget goes in.
            Name (str): Name of parameter.
            Value (bool): Value of parameter (True or False).
            Description (str): Description of parameter (string).
            layout (dict): Grid layout dict with `row` and `column` options.
            font (tuple): Tuple ('Font', size)
            emitter (EventEmitter): (Optional) event emitter for handling updates.
            kwargs (any): Optional keyword arguments
        """
        args = self.to_args(locals(), type_="Boolean")
        super().__init__(**args)
        self.to_grid(n_rows=1, n_columns=1)
        self.addCheckBox(checked=Value)

    @property
    def value(self) -> bool:
        """Break apart input string using `,` and remove whitespace.
        :rtype: bool
        """
        return bool(self.input.BoolValue.get())

    @value.setter
    def value(self, v: dict or bool = None) -> None:
        """Set the value of the parameter (and graphic).

        :param v: Dict with key 'Value' that is True or False
        :type v: dict
        """
        if v is None:
            self.input.BoolValue.set(False)
        elif type(v) is dict:
            v = v['Value']
        self.input.BoolValue.set(v)


class ParamDropdown(ParamWidget):
    """Widget for parameters with 'Type'=='Dropdown'"""
    def __init__(self,
                 master=None,
                 Name: str = "Untitled",
                 Value: str = "",
                 Description: str = "No description given.",
                 Options: list = None,
                 layout: dict = None,
                 font: tuple = ('Verdana', 12),
                 emitter: EventEmitter = None,
                 **kwargs):
        """Constructor for `ParamDropdown` widget class.

        Args:
            master (Frame or ttk.Frame or ttk.LabelFrame or Page): master container (master) that this widget goes in.
            Name (str): Name of parameter (str)
            Value (str): Default value (must match element of `p_options` ).
            Description (str): Description of this parameter (str)
            Options (list): List of allowable strings (list)
            layout (dict): Grid layout dict with `row` and `column` options.
            emitter (EventEmitter): (Optional) event emitter object.
            font (tuple): Tuple ('Font', size)
            kwargs (any): Optional keyword arguments
        Returns:
            __init__ should return None
        """
        if Options is None:
            Options = []
        args = self.to_args(arg_dict=locals(), type_='Dropdown')
        super().__init__(**args)
        self.addDropdown(text=Value, opts=Options)

    @property
    def opts(self) -> list:
        """The options available to the dropdown box.

        :rtype: list
        :returns: List of available options for dropdown box.
        """
        if self.input.Dropdown is None:
            return self._opts
        else:
            return self.input.Dropdown['values']

    @opts.setter
    def opts(self, value: list) -> None:
        """Set the available options of the dropdown box.

        :param value: The available options list for dropdown box.
        :type value: list
        :rtype: None
        :returns: None
        """
        if self.input.Dropdown is not None:
            self.input.Dropdown['values'] = value
        self._opts = value

    @property
    def value(self):
        return self.input.DropdownValue.get()

    @value.setter
    def value(self, v: dict = None) -> None:
        """Set the value of the widget using a dict.

        :param v: Value of property as dict with 'Value' and 'Options' keys, or as string 'Value'.
        :type v: dict or str
        :returns: None
        :rtype: None
        """
        if v is None:  # Then clear the current input box
            self.input.Dropdown.current()
            return
        self.updateDropdown(v=v['Value'], o=v['Options'])


class ParamDropdownTags(ParamWidget):
    """Widget for parameters with 'Type'=='DropdownTags'"""
    def __init__(self,
                 master=None,
                 Name: str = "Untitled",
                 Value: list = None,
                 Description: str = "No description given.",
                 Options: list = None,
                 layout: dict = None,
                 font: tuple = ('Verdana', 12),
                 emitter: EventEmitter = None,
                 **kwargs):
        """Constructor for `ParamDropdown` widget class.

        Args:
            master (Frame or ttk.Frame or ttk.LabelFrame or Page): master container (master) that this widget goes in.
            Name (str): Name of parameter (str)
            Value (list): Default value (must match element of `p_options` ).
            Description (str): Description of this parameter (str)
            Options (list): List of allowable strings (list)
            layout (dict): Grid layout dict with `row` and `column` options.
            emitter (EventEmitter): (Optional) event emitter object.
            font (tuple): Tuple ('Font', size)
            kwargs (any): Optional keyword arguments
        Returns:
            __init__ should return None
        """
        if Options is None:
            Options = []
        args = self.to_args(locals(), type_="DropdownTags")
        super().__init__(**args)
        self.addDropdown(text=self.list_2_str(Value), opts=Options)

    @property
    def value(self) -> list:
        """Break apart input string using `,` and remove whitespace.

        :rtype: list
        :returns: Converted version of ','-delimited string from input textbox.
        """
        return self.str_2_list(txt=self.input.DropdownValue.get())

    @value.setter
    def value(self, v: dict = None) -> None:
        """Set the value of the string displayed by the widget.
        :param v: Dict with key 'Value' that is a list of strings.
        :type v: dict
        :rtype: None
        :returns: None
        """
        if v is None:
            self.input.Dropdown.current()
            return
        v['Value'] = self.str_2_list(txt=v['Value'])
        self.updateDropdown(v=v['Value'], o=v['Options'])


class ParamLabel(ParamWidget):
    """Widget for parameters with 'Type'=='Label'"""
    def __init__(self,
                 master=None,
                 Name: str = "Untitled",
                 Value: str = "",
                 Description: str = "No description given.",
                 layout: dict = None,
                 font: tuple = ('Verdana', 12),
                 emitter: EventEmitter = None,
                 **kwargs):
        """Constructor for (basic) `ParamLabel` widget class.

        Args:
            master (Frame or ttk.Frame or ttk.LabelFrame or Page): Master container (master) that this widget goes in.
            Name (str): Name of parameter (str)
            Value (str): Default list with string values of parameter (list)
            Description (str): Description of this parameter (str)
            layout (dict): Grid layout dict with `row` and `column` options.
            emitter (EventEmitter): (Optional) event emitter for handling updates.
            font (tuple): Tuple ('Font', size)
            kwargs (any): Optional keyword arguments
        Returns:
            __init__ should return None
        """
        if Value is None:
            Value = []
        args = self.to_args(locals(), type_="Label")
        super().__init__(**args)
        self.to_grid(n_rows=1, n_columns=1)
        self.addTextEntry(text=Value)

    @property
    def value(self) -> str:
        """Return the string value of this widget.

        :returns: Value of text in the ttk.Entry string textbox widget.
        :rtype: str
        """
        return self.input.StringValue.get()

    @value.setter
    def value(self, v: dict = None) -> None:
        """Set the value of this widget to a string.

        :param v: Dict with key 'Value' that is a string.
        :type v: dict
        :returns: None
        :rtype: None
        """
        if v is None:
            self.input.StringValue.set("")
            return
        self.input.StringValue.set(v['Value'])

# TODO: Test ParamObject to see if it works.
class ParamObject(ParamWidget):
    """Widget for parameters with 'Type'=='Object'"""
    def __init__(self,
                 master=None,
                 Name: str = "Untitled",
                 Value: dict = None,
                 Description: str = "No description given.",
                 layout: dict = None,
                 font: tuple = ('Verdana', 10),
                 emitter: EventEmitter = None,
                 **kwargs):
        """Constructor for `ParamObject` widget class.

        Args:
            master (Frame or ttk.Frame or ttk.LabelFrame or Page): Master container (master) that this widget goes in.
            Name (str): Name of parameter (str)
            Value (dict): Values of nested parameter JSON objects
            Desc (str): Description of this parameter (str)
            layout (dict): Grid layout dict with `row` and `column` options.
            font (tuple): Tuple ('Font', size)
            emitter (EventEmitter): (Optional) event emitter for handling updates.
            kwargs (dict): (Optional) keyword arguments
        """
        args = self.to_args(locals(), type_="Object")
        super().__init__(**args)
        (n_rows, n_columns) = self.compute_grid(n=len(Value.keys()))
        self.to_grid(n_rows=n_rows, n_columns=n_columns)
        layout = dict(row=0, rowspan=1, column=0, columnspan=1, sticky=(N, S, E, W))
        for (name, value) in Value.items():
            if layout['column'] == n_columns:
                layout['column'] = 0
                layout['row'] += 1
            if value['Type'] in ('Dropdown', 'DropdownTags'):
                column_span = 2
            else:
                column_span = 1
            layout['columnspan'] = column_span
            sub_args = dict(name=name,
                            layout=layout,
                            emitter=self.emitter,
                            font=myDecorations.font['SMALL'],
                            **value)
            # Create the correct type of widget for this parameter.
            child_widget = parse_widget(master=self, tooltip=self.tooltip, **args)
            # Add the parameter widget to the dictionary of all such widgets.
            self.children[name] = child_widget
            layout['column'] += column_span

    @property
    def value(self) -> dict:
        """Return value of all child widgets as dict.

        :returns: Values dict of all child widgets.
        :rtype: dict
        """
        out = {}
        for k in self.children.keys():
            out[k] = self.children[k].value
        return out

    @value.setter
    def value(self, v: dict = None) -> None:
        """Set the value of the combobox using dict keys.

        :param v: Contains keys for each child widget, with recursive params JSON structure.
        :type v: dict
        :returns: None
        :rtype: None
        """
        for k in self.children.keys():
            if k in v.keys():
                self.children[k].value = v[k]
            else:
                print("Could not find key <" + str(k) + ">")
                self.children[k].value = None


class ParamScalar(ParamWidget):
    """Widget for parameters with 'Type'=='Scalar'"""
    def __init__(self,
                 master=None,
                 Name: str = "Untitled",
                 Value: float = 50.0,
                 Description: str = "No description given.",
                 Units: str = "N/A",
                 Bounds: list = None,
                 Increment: float = 1.0,
                 layout: dict = None,
                 font: tuple = ('Verdana', 10),
                 emitter: EventEmitter = None,
                 **kwargs):
        """Constructor for `ParamScalar` widget class.

        Args:
            master (Frame or ttk.Frame or ttk.LabelFrame or Page): Master container (master) that this widget goes in.
            Name (str): Name of parameter (str)
            Value (float): Default value of parameter (float)
            Description (str): Description of this parameter (str)
            Units (str): Units for this numeric value (str)
            Bounds (list): Two-element list with the min. and max. allowed values.
            Increment (float): Scalar indicating how much to increment spinbox on change.
            layout (dict): Grid layout dict with `row` and `column` options.
            font (tuple): Tuple ('Font', size)
            emitter (EventEmitter): (Optional) event emitter for handling updates.
            kwargs (dict): (Optional) keyword arguments
        """
        args = self.to_args(locals(), type_="Scalar")
        super().__init__(**args)
        self._type = type(Value)
        self.to_grid(n_rows=1, n_columns=1)
        self.addSpinBox(value=Value)

    @property
    def value(self) -> float or int:
        """Return value of spin box.

        :returns: Value in spin box, converted to float or int depending on input Value type.
        :rtype: float or int
        """
        return self._type(self.input.Spin.get())

    @value.setter
    def value(self, v: dict or float or int = None) -> None:
        """Set the value of the combobox using dict keys.

        :param v: Contains key 'Value' that is the float value of scalar.
        :type v: dict or float or int
        :returns: None
        :rtype: None
        """
        if type(v) is dict:
            v = v['Value']
        self._type = type(v)
        self.input.Spin.set(v)


class ParamTags(ParamWidget):
    """Widget for parameters with 'Type'=='Tags'"""
    def __init__(self,
                 master=None,
                 Name: str = "Untitled",
                 Value: list = None,
                 Description: str = "No description given.",
                 layout: dict = None,
                 font: tuple = ('Verdana', 12),
                 emitter: EventEmitter = None,
                 **kwargs):
        """Constructor for `ParamTags` widget class.

        Args:
            master (Frame or ttk.Frame or ttk.LabelFrame or Page): Master container (master) that this widget goes in.
            Name (str): Name of parameter (str)
            Value (list): Default list with string values of parameter (list)
            Description (str): Description of this parameter (str)
            layout (dict): Grid layout dict with `row` and `column` options.
            emitter (EventEmitter): (Optional) event emitter for handling updates.
            font (tuple): Tuple ('Font', size)

        Returns:
            __init__ should return None

        Note:
            Basic syntax translates ['Tag1', 'Tag2', 'Tag3'] value into "Tag1,
            Tag2, Tag3" in `Entry` and any modifications to the `Entry` are changed
            into additional List items if they are "," delimited.
        """
        if Value is None:
            Value = []
        args = self.to_args(locals(), type_="Tags")
        super().__init__(**args)
        self.to_grid(n_rows=1, n_columns=1)
        self.addTextEntry(text=self.array_2_str(Value))

    @property
    def value(self) -> list:
        """Break apart input string using `,` and remove whitespace.

        :returns: Comma-delimited list in ttk.Entry as list of string elements.
        :rtype: list
        """
        return self.str_2_list(self.input.StringValue.get())

    @value.setter
    def value(self, v: dict or str = None) -> None:
        """Set the value of the string displayed by the widget.

        :param v: Dict with key 'Value' that is a list of strings.
        :type v: dict or str
        :returns: None
        :rtype: None
        """
        if type(v) is dict:
            v = v['Value']
        self.input.StringValue.set(self.list_2_str(v))  # Concatenate the list using ", "
