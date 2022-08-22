#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module containing the parameter interface window and pages.

Note:
    - The main class to import from this module is ParametersWindow.
    - All the `Page` types are subclasses of `TypedParametersPage`.
    - Each "Type" of parameter has its own "Type" of widget from component.widgets.

Authors:
    - Jonathan Shulgach
    - Max Murphy
"""
import json
from time import strftime
from definitions import DEFAULT_PARAMETERS_DIR, DEFAULT_PARAMETERS_FILE, DEFAULT_LAYOUTS_DIR, SAVED_PARAMETERS_DIR
from pymitter import EventEmitter
from tkinter import N, S, E, W, StringVar, PhotoImage, messagebox
from tkinter.filedialog import askdirectory, askopenfile, askopenfilename
from component.arg_formats import arrayType, tagsType
from component.widgets import VALID_TYPES, parse_widget, raise_type_error
from component.utilities import add_image_button, check_for_file, get_photo_image, json_array_2_params_property
from component.interfaces import ParentWindow, Pane, Page, app, myDecorations


class TypedParameterPage(Page):
    """Generic Parameter page to use as superclass for specific types."""
    def __init__(self,
                 notebook: Pane = None,
                 title: str = "Unspecified Parameter Type",
                 subtitle: str = "Parameters",
                 p_type: tagsType or arrayType or str = None,
                 n_per_column: int = 4,
                 emitter: EventEmitter = None,
                 **kwargs):
        """Subclass of `Page` that specializes in handling task meta-parameters.

        :param notebook: The master Pane (notebook) holding this Page (tab).
        :param title: Serves as the "key" for this tab as well as the title in the tab.
        :param subtitle: Header at top of panel as a static label.
        :param p_type: Type of parameter ("Label" | "Dropdown" | "Scalar" | "Boolean" | "Array" | "Tags" | "Object")
        :param n_per_column: Number of parameter widgets per column (default: 4)
        :param emitter: (Optional) event emitter for handling updates.
        :param kwargs: (Optional) keyword argument dict for child widgets.
        :type notebook: Pane
        :type title: str
        :type subtitle: str
        :type p_type: tagsType or arrayType or str
        :type n_per_column: int
        :type emitter: EventEmitter or None
        :type kwargs: dict or None
        .. seealso:: component.layouts.Page, tkinter.Frame, ParametersParentWindow, tkinter.Toplevel
        """
        super().__init__(TypedParameterPage.init_key,
                         master=notebook,
                         title=title,
                         width=notebook.width,
                         height=notebook.height)
        self.type = p_type
        self.emitter = emitter
        self.parameters = dict()
        self.n_per_column = n_per_column
        self.grid_columnconfigure(0, weight=1, minsize=self.width)
        self.widgets = {}
        self._header_variable = StringVar()
        self.addTaskHeader(text=subtitle, textvariable=self._header_variable, anchor=E)

    def init_parameters(self, parameters: dict) -> None:
        """Initialize the page with correct widgets in grid.

        :param parameters: Full dict of (default) parameters.
        :type parameters: dict
        .. seealso:: self.addParameter,
        """
        self.parameters = parameters
        layout = dict(row=0, rowspan=1, column=0, columnspan=1, sticky=(N, S, E, W))
#         w = self.winfo_toplevel()
        w = self.master.master
        for name in parameters:
            value = parameters[name]
            if self.includes(p_page=value['Page']):
                if layout['column'] == self.n_per_column:
                    layout['column'] = 0
                    layout['row'] += 1
                n = self._increment_size[value['Type']](value)
                layout['columnspan'] = n
                # Add a mapping to associate this parameter to the correct page.
                w.setParameterPageIndex(k=name, idx=self.index())
                args = dict(name=name,
                            layout=layout,
                            emitter=self.emitter,
                            font=myDecorations.font['SMALL'],
                            **value)
                # Create the correct type of widget for this parameter.
                entry_widget = parse_widget(master=self.contents,
                                            tooltip=self.tooltip,
                                            **args)
                # Add the parameter widget to the dictionary of all such widgets.
                self.widgets[name] = entry_widget
                layout['column'] += n

    def includes(self, p_page: str) -> bool:
        """Check if typed parameter should be included on this page.

        :param p_page: The 'Page' value in the named parameter dict.
        :type p_page: str
        :returns: True if the page includes the parameter corresponding to p_page property.
        :rtype: Boolean
        """
        return p_page == self.title

    def index(self) -> int:
        """Index in master window array of pages.

        :returns: Page index.
        :rtype: int
        """
        w = self.winfo_toplevel()
        return w.pageIndex(self)

    def loadParameters(self, parameters: dict) -> None:
        """Load relevant parameter values for this page.

        :param parameters: Dict containing parameters of all Type values.
        :type parameters: dict
        :returns: None
        :rtype: None
        """
#         w = self.winfo_toplevel()
        w = self.master.master
        for k in parameters:
            v = parameters[k]
            if self.includes(p_page=v['Page']):
                self.parameters[k] = v
                self.setWidgetValue(k, v)
                w.setParameterPageIndex(k=k, idx=self.index())

    def setWidgetValue(self, k: str, v: dict) -> None:
        """Update an existing widget's value.

        :param k: Key (parameter 'Name' from json file, key in main parameters dict).
        :param v: Dict containing 'Value', 'Description', and 'Type', as well as possibly 'Units' or 'Options'
        :type k: str
        :type v: dict
        :returns: None
        :rtype: None
        .. seealso:: component.widgets
        """
        self.widgets[k].value = v

    def getParameter(self, k: str) -> list or float or str or bool and list or None:
        """Return the `dynamic` value of a named parameter.

        :param k: Key to dict entry for a given parameter ('Name' in *.json file).
        :type k: str
        :returns: The dynamic `Value` in named parameter dict related to key `k`.
        :rtype: list or float or str or bool and list or None
        """
        if self.widgets[k].type not in ("Dropdown", "DropdownTags"):
            opts = None
        else:
            opts = self.widgets[k].opts
        return self.widgets[k].value, opts

    @property
    def type(self) -> list:
        """List of property types allowed on this page.

        :returns: List of allowable parameter types.
        :rtype: list
        """
        return self._type

    @type.setter
    def type(self, v: tagsType or str = None) -> None:
        """Set the parameter type value, ensuring it is a list.

        :param v: The value to update Type to.
        :type v: str or list
        :returns: None
        :rtype: None
        """
        if v is None:
            self._type = VALID_TYPES
        elif type(v) is list:
            self._type = v
        elif type(v) is str:
            if v in VALID_TYPES:
                self._type = [v]
            else:
                raise_type_error(v=v)
        else:
            raise_type_error()

    @property
    def _increment_size(self) -> dict:
        """Return dict to map between Widget Type and grid step increment.

        :returns: Mapping between widget types and how grid should increment.
        :rtype: dict
        """
        return dict(Scalar=lambda x: 1,
                    Array=lambda x: 1,
                    Tags=lambda x: 2,
                    Dropdown=lambda x: 1,
                    Label=lambda x: 1,
                    Boolean=lambda x: 1,
                    DropdownTags=lambda x: 2,
                    Object=lambda x: 2)


class ParametersParentWindow(ParentWindow):
    """Main parameters window class."""
    def __init__(self,
                 master: app = None,
                 defaults_name: str = None,
                 title: str = "Parameters Exporter",
                 width: int = 1028,
                 height: int = 720,
                 **kwargs):
        """Constructor for new Parameter window.

        :param master: The master application (tkinter.Tcl())
        :param defaults_name: Name of `params.json` file to load by default.
        :param exit_command: Default is `self.on_closing` - what to do when Parameters UI is closed.
        :param width: Number of pixels wide the window should be.
        :param height: Number of pixels tall the window should be.
        :param kwargs: Optional keyword arguments dict for Window.
        :type master: app or None
        :type defaults_name: str
        :type width: int
        :type height: int
        :type kwargs: dict or str or int or None
        :returns: None
        :rtype: None

        .. seealso:: tkinter.Tcl, component.interfaces.Window, tkinter.Toplevel
        """
        files = [('JavaScript Object Notation', '*.json'),
                 ('Any File Type', '*.*')]
        if defaults_name is None:
            filename = askopenfilename(title="Select parameters json file.",
                                       initialdir=DEFAULT_PARAMETERS_DIR,
                                       initialfile=DEFAULT_PARAMETERS_FILE,
                                       multiple=False,
                                       filetypes=files,
                                       defaultextension=files)
        elif check_for_file(defaults_name):
            filename = defaults_name
        else:
            filename = askopenfilename(title="Select parameters json file.",
                                       initialdir=DEFAULT_PARAMETERS_DIR,
                                       initialfile=DEFAULT_PARAMETERS_FILE,
                                       multiple=False,
                                       filetypes=files,
                                       defaultextension=files)
        if master is None:
            master = app
        super(ParametersParentWindow, self).__init__(master=master,
                                                     title=title,
                                                     width=width,
                                                     height=height,
                                                     **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self._emitter = EventEmitter(wildcard=True)
        self._emitter.on(event="parameter.updated.*.*", func=self.updateParameter, ttl=-1)
        self._directory = SAVED_PARAMETERS_DIR
        self.task = None
        self.pgs = []
        self.notebooks = {}
        self.ready = False
        
        self._parameters, self._layout_file, self._icon_file = json_array_2_params_property(open(filename, 'rt'))
#         self._addNotebook(title="Parameters", width=round(self.width*0.9), height=round(self.height*0.95))
        
        self.task = self._parameters['Task']['Value']
        self._loadLayout(self._parameters, **kwargs)

    def updateParameter(self, p):
        """Callback for updating a given parameter based on widget changes."""
        print("Updated {0} to {1}.".format(p['Name'], p['Value']))
        self._parameters[p['Name']]['Value'] = p['Value']

    def pageIndex(self, page) -> int:
        """Return index of page in self.pgs array (or None if not in array).

        :param page: The page to "look-up" using .index() method of the array property.
        :type page: TypedParameterPage
        :returns: Index of page argument in .pgs array attribute.
        :rtype: int
        """
        return self.pgs.index(page)

    def loadParameters(self, parameters: dict or str = None) -> None:
        """Load parameters callback method.

        :param parameters: Dict with all parameters from *.json configuration file.
        :type parameters: dict or str or None
        """
        if parameters is None:
            files = [('JavaScript Object Notation', '*.json'),
                     ('Any File Type', '*.*')]
            file = askopenfile(mode='rt',
                               title="Select parameters json file.",
                               initialdir="/default_parameters/",
                               initialfile="params.json",
                               multiple=False,
                               filetypes=files,
                               defaultextension=files)
            if file is None:
                print("No file selected.")
                return
            parameters, self._layout_file, self._icon_file = json_array_2_params_property(file)
            if self._icon_file is not None:
                pass
                self.iconbitmap(self._icon_file)
                self.master.iconbitmap(self._icon_file)
        elif type(parameters) is str:
            if not check_for_file(filename=parameters):
                raise Exception("Could not find file <" + parameters + ">")
            file = open(parameters, mode='rt')
            parameters, self._layout_file, self._icon_file = json_array_2_params_property(file)
            if self._icon_file is not None:
                # pass
                self.iconbitmap(self._icon_file)
                self.master.iconbitmap(self._icon_file)
        self._dropTabs()
        self._parameters = parameters
        self._loadLayout(parameters)
        for p in self.pgs:
            print(f'Loading {p.title} parameters...')
            p.loadParameters(parameters)
        print("Loading complete!")
        
    def _dropTabs(self):
        """Drop existing tabs/notebooks."""
        # First, close any existing tabs
        page_list = self.pgs.copy()
        for individual_page in page_list:
            self.pgs.remove(individual_page)
            individual_page.destroy()
            
        # Remove existing notebooks
        nb = list(self.notebooks.keys())
        for key in nb:
            pgs = list(self.notebooks[key].pages.keys())
            for pg in pgs:
                self.notebooks[key].pages[pg].destroy()
                _ = self.notebooks[key].pages.pop(pg, None)
            self.notebooks[key].destroy()
            _ = self.notebooks.pop(key, None)
        
    def _loadLayout(self, parameters, **kwargs):
        """Load layout after loading new parameters file."""
            
        # self._addNotebook(title="Parameters", width=round(self.width*0.9), height=round(self.height*0.95))
        
        if self._layout_file is None:
            self._layout_file = askopenfilename(title="Select parameters json file.",
                                                initialdir=DEFAULT_LAYOUTS_DIR,
                                                initialfile="layout.json",
                                                multiple=False,
                                                filetypes=files,
                                                defaultextension=files)
        if self._icon_file is not None:
            self.master.iconphoto(False, PhotoImage(file=self._icon_file))
            self.iconphoto(False, PhotoImage(file=self._icon_file))
                    
        layout = json.load(open(self._layout_file, mode="rt"))
#         common_to_all_pages = dict(notebook=self.notebooks['Parameters'], emitter=self._emitter)
        common_to_all_pages = dict(notebook=self._addNotebook(title="Parameters", width=round(self.width*0.9), height=round(self.height*0.95)), emitter=self._emitter)
            
        # Populate list property with the new tabs
        page_index = 0
        for individual_page_layout in layout['pages']:
            p = TypedParameterPage(**individual_page_layout, **common_to_all_pages, **kwargs)
            p.addButton(text="Save",
                        desc="Save current parameters configuration. \nAn auto-named *.json is generated in selected "
                             "folder.",
                        command=self.saveParameters)
            p.addButton(text="Load",
                        desc="Load existing parameters from *.json file.",
                        command=self.loadParameters)
            p.buttons["Exit"].configure(command=self.on_closing)
            self.pgs.append(p)
            self.pgs[page_index].init_parameters(parameters=parameters)
            page_index += 1

    def saveParameters(self):
        """Save parameters callback method.

        :returns: None
        :rtype: None
        """
        self._directory = askdirectory(mustexist=True, initialdir=self._directory)
        if len(self._directory) == 0:
            print("Save canceled.")
            return
        filename = self.name
        f = open(filename, 'wt')
        out = dict(parameters=[])
        data = {}
        for k in self.parameters:
            data[k] = self.getParameter(k)
            out['parameters'].append(data[k])
        out['layout'] = self._layout_file
        out['icon'] = self._icon_file
        self._parameters.update(**data)
        json.dump(out, f, indent=2)
        self.ready = check_for_file(filename)
        if self.ready:
            print("Save successful!")

    def getParameter(self, name: str) -> dict:
        """Return the dynamic parameter object by name and type.

        :param name: Key in fully-enumerated parameters dict (self.parameters)
        :type name: str
        :returns: Dynamic value reflecting updates from parameters interface for that parameter.
        :rtype: dict

        .. seealso:: Page, Panel
        """
        if name not in self.parameters.keys():
            msg = "Bad reference to parameter <" + name + "> (not in parameters enumeration dict)"
            raise Exception(msg)
        value = self.parameters[name]
        if 'Options' in value.keys():
            value['Value'], value['Options'] = self.pgs[value['PageIndex']].getParameter(k=name)
        else:
            value['Value'], _ = self.pgs[value['PageIndex']].getParameter(k=name)
        self.parameters[name] = value
        return value

    def on_closing(self):
        """Callback that occurs when window close request is received."""
        if not self.ready:
            if messagebox.askokcancel("Quit", "Exit without saving parameters?"):
                self.master.destroy()
        else:
            self.master.destroy()

    def setParameterPageIndex(self, k: str, idx: int) -> None:
        """Set the `PageIndex` value for a given parameter.

        :parameter k: The key (string) corresponding to the parameter to update.
        :parameter idx: The page index corresponding to self.pgs array index of container page.
        :type k: str
        :type idx: int
        :returns: None
        :rtype: None
        """
        self._parameters[k]['PageIndex'] = idx

    @property
    def parameters(self) -> dict or None:
        """Parameters property holds all the parameter-related information.

        :returns: Parameters dict
        :rtype: dict or None
        """
        parameters = {}
        if self.task is not None:
            for (k, v) in self._parameters.items():
                if self.task in v['Task']:
                    parameters[k] = v
        return parameters

    @parameters.setter
    def parameters(self, value: dict = None) -> None:
        """Setting parameters property updates value of self._parameters.

        :param value: The new dict value of self._parameters.
        :type value: dict or None
        """
        if value is not None:
            self.task = value['Task']['Value']
            self._parameters.update(**value)

    @property
    def filename_delimiter(self) -> str:
        """CONSTANT: delimiter for filename metadata elements.

        :returns: "_"

        .. seealso:: self.name
        """
        return "_"

    @staticmethod
    def formatted_date() -> str:
        """Return ISO-861 formatted date.

        .. seealso:: self.name
        """
        return strftime("%Y-%m-%d")

    @property
    def name(self) -> str:
        """Auto-parsed filename for this session.

        .. note::
            See the params.json parameter entry for `Naming Variables`.
            If `Naming Variables` is missing, the following metadata parameters are required:
                + Task

        .. seealso:: self.loadParameters, self.saveParameters
        """
        value = self.formatted_date()
        delimiter = self.filename_delimiter
        if "Naming Variables" in self.parameters.keys():
            v = self.getParameter("Naming Variables")
            schema = v['Value']
        else:
            schema = ["Task"]
        for k in schema:  # For each element in schema list, add delimited metadata to name
            v = self.getParameter(k)
            value = value + delimiter + v['Value']
        file_index = 0
        filename = self._directory + "/" + value + delimiter + '{0:02d}'.format(file_index) + '.json'
        while check_for_file(filename):  # While a file of that name exists, increment the index variable.
            file_index += 1
            filename = self._directory + "/" + value + delimiter + '{0:02d}'.format(file_index) + '.json'
        return filename
