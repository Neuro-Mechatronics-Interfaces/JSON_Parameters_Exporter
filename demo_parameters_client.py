import asyncio, json, os, threading, websockets
from enum import Enum

PARAMETERS_IP = "128.2.244.29"
PARAMETERS_PORT = 6789
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
ICON_FILE = os.path.join(ASSETS_DIR, "CMU_Tartans.png")
DEFAULT_LAYOUTS_DIR = os.path.join(ROOT_DIR, "default_layouts")
LAYOUT_FILE = os.path.join(DEFAULT_LAYOUTS_DIR, "layout.json")
DEFAULT_PARAMETERS_DIR = os.path.join(ROOT_DIR, "default_parameters")
SAVED_PARAMETERS_DIR = os.path.join(ROOT_DIR, "saved_parameters")
CALIBRATION_FILE = os.path.join(ROOT_DIR, "calibrations.json")
TRIAL_DATA_DIR = os.path.join(ROOT_DIR, "trial_data")
TRIAL_DATA_NAME_EXPR = "{subj}_{date}_Trial-Data_{time}.txt"
ALLOWED_PARAMETER_FILE_TYPES =   [('JavaScript Object Notation', '*.json'),
                                  ('Any File Type', '*.*')]

class CalibrationState():
    """Calibration object that keeps current version of calibration info."""    
    def __init__(self, orientation: str = 'MID'):
        self.orientation = orientation
        self.file = CALIBRATION_FILE
        self.saved = False
        with open(self.file, 'rt') as f:
            tmp = json.load(f)
            f.close()
        self._cal = {
            'x_in': tmp[self.orientation]['x_in'],
            'y_in': tmp[self.orientation]['y_in'],
            'left_in': tmp[self.orientation]['left_in'],
            'top_in': tmp[self.orientation]['top_in'],
            'right_in': tmp[self.orientation]['right_in'],
            'bottom_in': tmp[self.orientation]['bottom_in'],
            'x_out': tmp[self.orientation]['x_out'],
            'y_out': tmp[self.orientation]['y_out'],
            'left_out': tmp[self.orientation]['left_out'],
            'top_out': tmp[self.orientation]['top_out'],
            'right_out': tmp[self.orientation]['right_out'],
            'bottom_out': tmp[self.orientation]['bottom_out']
        }
        self.state = {
                'left_in': CalibrationStatus.DEFAULT,
                'right_in': CalibrationStatus.DEFAULT,
                'top_in': CalibrationStatus.DEFAULT,
                'bottom_in': CalibrationStatus.DEFAULT,
                'x_in': CalibrationStatus.DEFAULT,
                'y_in': CalibrationStatus.DEFAULT,
                'left_out': CalibrationStatus.DEFAULT,
                'right_out': CalibrationStatus.DEFAULT,
                'top_out': CalibrationStatus.DEFAULT,
                'bottom_out': CalibrationStatus.DEFAULT,
                'x_out': CalibrationStatus.DEFAULT,
                'y_out': CalibrationStatus.DEFAULT
            }
        
    def __getitem__(self, key):
        if key == 'center_in':
            return self._cal['x_in'], self._cal['y_in']
        elif key == 'center_out':
            return self._cal['x_out'], self._cal['y_out']
        else:
            return self._cal[key]
        
    def __setitem__(self, key, value):
        if key == 'center_in':
            self._cal['x_in'] = value[0]
            self._cal['y_in'] = value[1]
            self.state['x_in'] = CalibrationStatus.ASSIGNED
            self.state['y_in'] = CalibrationStatus.ASSIGNED
        elif key == 'center_out':
            self._cal['x_out'] = value[0]
            self._cal['y_out'] = value[1]
            self.state['x_out'] = CalibrationStatus.ASSIGNED
            self.state['y_out'] = CalibrationStatus.ASSIGNED
        else:
            self._cal[key] = value
            self.state[key] = CalibrationStatus.ASSIGNED
        
    def summarize(self):
        """Returns (x_center, y_center, adc left, adc right, adc top, adc bottom) pixel coordinates of calibration."""
        return self._cal['x_out'], self._cal['y_out'], self._cal['left_in'], self._cal['left_out'], self._cal['right_in'], self._cal['right_out'], self._cal['top_in'], self._cal['top_out'], self._cal['bottom_in'], self._cal['bottom_out']
        
    def debug(self, msg: str) -> None:
        """Message logging to terminal.
        
        :param msg: The string to print.
        :type msg: str
        :param min_verbosity_level: The threshold for `verbose` to print this statement.
        :type int:
        """
        print("[CALIBRATION::DEBUG]    {s}".format(s=msg))
        
    def set_target(self, target, x, y) -> bool:
        """Sets or unsets the target location based on keypress and returns flag if new value set."""
        if target == 'left_in':  # Uses raw (INPUT)
            self._cal['left_in'] = x
        elif target == 'right_in':  # Uses raw (INPUT)
            self._cal['right_in'] = x
        elif target == 'top_in':  # Uses raw (INPUT)
            self._cal['top_in'] = y
        elif target == 'bottom_in':  # Uses raw (INPUT)
            self._cal['bottom_in'] = y
        elif target == 'center_in':  # Uses raw (INPUT)
            self._cal['center_in'] = (x, y)
            self._cal['x_in'] = x
            self._cal['y_in'] = y
        elif target == 'left_out':  # Uses processed (PIXELS)
            self._cal['left_out'] = x
        elif target == 'right_out':  # Uses processed (PIXELS)
            self._cal['right_out'] = x
        elif target == 'top_out':  # Uses processed (PIXELS)
            self._cal['top_out'] = y
        elif target == 'bottom_out':  # Uses processed (PIXELS)
            self._cal['bottom_out'] = y
        elif target == 'center_out':  # Uses processed (PIXELS)
            self._cal['center_out'] = (x, y)
            self._cal['x_out'] = x
            self._cal['y_out'] = y
            
    def save(self):
        """Save the calibrations to json file."""            
        with open(self.file, 'rt') as f:
            cal = json.load(f)
            f.close()
        o = self.orientation
        with open(self.file, 'wt') as f:
            for k in self.state.keys():
                cal[o][k] = round(self[k])
            json.dump(cal, f, indent=2)
            f.close()
        self.saved = True
        print("Saved {0} successfully!".format(self.file))


class CalibrationStatus(Enum):
    """Possible integer values results related to a single-trial outcome could take."""
    DEFAULT = 0
    PENDING = 1
    ASSIGNED = 2


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
    Task: list

    def __init__(self,
                 Name: str = None,
                 Type: str = None,
                 Page: str = None,
                 Value: any = None,
                 Description: str = None,
                 Options: list = None,
                 Bounds: list = None,
                 Increment: float or int = None,
                 Task: list = None):
        """Class constructor defines the structure of parameter JSON objects.

        :param Name: Name of the parameter
        :param Type: "Type" of parameter.
        :param Page: The name of the page the parameter goes on.
        :param Value: The actual parameter value.
        :param Description: Description of what parameter is (for tooltip hover-info box).
        :param Options: If a dropdown is involved, this is a list of options.
        :param Bounds: If numbers are involved, this represents bounds on the range of possible values.
        :param Increment: If numbers are involved, this represents the step-size for clicking on spinbox arrows.
        :param Task: The tasks that use this parameter.
        :type Name: str
        :type Type: str
        :type Page: str
        :type Value: any
        :type Description: str
        :type Options: list
        :type Bounds: list
        :type Increment: float or int
        :type Task: list
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
        

class GameParameters():
    def __init__(self, logging = None, parameters=None, session: str = None, ws_ip: str = PARAMETERS_IP, ws_port: int = PARAMETERS_PORT):
        """Game parameters object."""
        self._uri = f"ws://{ws_ip}:{ws_port}"
        self._thread = threading.Thread(target=self.pthread_target, daemon=True)
        self.logging = logging
        self.ws = None
        if session is None:
            session = "demo"
        self.paths = {'save': SAVED_PARAMETERS_DIR,
                      'load': DEFAULT_PARAMETERS_DIR,
                      'assets': ASSETS_DIR,
                      'layouts': DEFAULT_LAYOUTS_DIR, 
                      'trials': TRIAL_DATA_DIR, 
                      'allowed': ALLOWED_PARAMETER_FILE_TYPES}
        
        self._parameters = {}
        self._icon_file = 'CMU_Tartans.png'
        self._layout_file = 'layout.json'
        if parameters is None:
            self.load()
        elif type(parameters) is dict:
            if 'parameters' in parameters.keys():
                self._parameters = parameters['parameters']
            else:
                self._parameters = parameters
            if 'icon' in parameters.keys():
                self._icon_file = parameters['icon']
            else:
                self._icon_file = 'CMU_Tartans.png'
            if 'layout' in parameters.keys():
                self._layout_file = parameters['layout']
            else:
                self._layout_file = 'layout.json'
        if len(self._parameters.keys()) == 0:
            self.calibration = CalibrationState()
        else:
            self.calibration = CalibrationState(self._parameters['Orientation']['Value'])
        self.session = session
        self._index = -1
        self._thread.start()        
        
    def __getitem__(self, key):
        if key not in self._parameters.keys():
            raise IndexError("Invalid key ({key}).".format(key=key))
        return self._parameters[key]        
        
    def __rshift__(self, name: str) -> dict:
        """Shift 'out' a parameter. Use `get` to return only the value.
        
        :param name: Name of the parameter to return.
        :type name: str
        :returns: Parameter dict for some particular parameter name.
        :rtype: dict
        :example: ui._parameters['Subject'] = self >> 'Subject'
        """
        return self._parameters[name]
    
    def __lshift__(self, par) -> None:
        """Shift 'in' a parameter.

        :param par: Parameter dict to assign. MUST have 'Name' as a field.
        :type par: dict or ParamJSONFormat
        :example: self << ui._parameters['Subject']
        """
        self.debug("data.parameters.{0}={1}".format(par['Name'], par['Value']), 1)
        for k in self._parameters[par['Name']].keys():
            if k in par:
                self._parameters[par['Name']][k] = par[k]
        return None
    
    @property
    def icon_file(self) -> str:
        """Full filename of icon png image."""
        return os.path.join(os.path.abspath(self.paths['assets']), self._icon_file)
        
    @property
    def layout_file(self) -> str:
        """Full filenameof layout.json for parameters ui layout."""
        return os.path.join(os.path.abspath(self.paths['layouts']), self._layout_file)
    
    @property
    def save_name(self) -> str:
        """Auto-parsed filename for this session.

        .. note::
            See the params.json parameter entry for `Naming Variables`.
            If `Naming Variables` is missing, the following metadata parameters are required:
                + Task

        .. seealso:: self.loadParameters, self.saveParameters
        """
        value = self.formatted_date()
        delimiter = self.filename_delimiter
        if "Naming Variables" in self._parameters.keys():
            schema = self.get("Naming Variables")
        else:
            schema = ["Task"]
        for k in schema:  # For each element in schema list, add delimited metadata to name
            value = value + delimiter + self.get(k)
        file_index = 0
        file_name = os.path.join(os.path.abspath(self.paths['save']), self.get('Subject'), 'Behavior', value + delimiter + '{0:02d}'.format(file_index) + '.json')
        while check_for_file(file_name):  # While a file of that name exists, increment the index variable.
            file_index += 1
            file_name = os.path.join(os.path.abspath(self.paths['save']), self.get('Subject'), 'Behavior', value + delimiter + '{0:02d}'.format(file_index) + '.json')
        return file_name
    
    @property
    def verbose(self):
        if 'Verbose Output' not in self._parameters.keys():
            return 1
        else:
            return self._parameters['Verbose Output']['Value']
        
    def as_dict(self) -> dict:
        """Return parameters as dict."""
        return self._parameters
        
    def debug(self, msg, min_verbosity_level: int = 1):
        """Message logging to terminal."""
        if (self.verbose >= min_verbosity_level):
            if self.logging is None:
                print("[PARAMETERS::DEBUG]   {s}".format(s=msg))
            else:
                self.logging.info("[PARAMETERS] {s}".format(s=msg))
            
    @property
    def filename_delimiter(self) -> str:
        """CONSTANT: delimiter for filename metadata elements.

        :returns: "_"

        .. seealso:: self.save_name
        """
        return "_"
    
    @staticmethod
    def formatted_date() -> str:
        """Return ISO-861 formatted date.

        .. seealso:: self.save_name
        """
        return strftime("%Y-%m-%d")
    
    def keys(self):
        return self._parameters.keys()
    
    async def get(self, name):
        """Return the value of a specific parameter.

        :param name: The name (key) for a given parameter.
        :type name: str
        """
        # if name not in self.keys():
        #    self.debug("error.parameters.name={name} (Invalid parameter name)".format(name=name), 1)
        #    return None
        # else:
            # print("{name}:{value}".format(name=name, value=self._parameters[name]))
            # return self._parameters[name]['Value']
        async with websockets.connect(self._uri) as ws:
            if name not in self._parameters.keys():
                self._parameters[name] = {}
            await ws.send(json.dumps({"type": 'get_parameter', "name": name}))
            val = json.loads(await ws.recv())
            while not (val["type"] == "iparam"):
                val = json.loads(await ws.recv())
            self._parameters[name]['Value'] = val['value']
            return self._parameters[name]['Value']
            
    async def server_message_handler(self):
        """Returns the value from the parameter server."""
        async with websockets.connect(self._uri) as ws:
            try:
                await self._server_message_parser(ws)
            except websockets.ConnectionClosed:
                await asyncio.sleep(0.1)
            
    async def _server_message_parser(self, ws):
        data = json.loads(await ws.recv())
        while not (data["type"] == "parameters"):
            data = json.loads(await ws.recv())
        if data['has_data'] == True:
            p = json.loads(data['parameters'])
            for (k,v) in p.items():
                if k not in self._parameters.keys():
                    self._parameters[k] = {}
                self._parameters[k] = v
            self.debug("Parameters updated.")
        else:
            self.debug("Parameters not yet initialized.")
        
    def bounds(self, name):
        """Return the bounds of a specific parameter."""
        return self._parameters[name]['Bounds']
        
    def handle_new_calibration(self, value):
        """Update calibration according to type of event.

        :param value: The calibration object.
        """
        self.calibration = value
    
    def handle_new_value(self, value: ParamJSONFormat):
        """Set a parameter to a new specific value on update.
    
        :param value: Basically a dict with the standard expected values (from JSON file) of any parameter.
        :type value: ParamJSONFormat (defined in component.widgets.py)
        """
        self.debug("data.parameters.{0}={1}".format(value['Name'], value['Value']), 1)
        for k, v in value.items():
            self._parameters[value['Name']][k] = v
    
    @staticmethod
    def json_array_2_params_property(file) -> dict and str or None and str or None:
        """Convert array structure from params.json into property field value.

        :param file: The *.json parameters file.
        :type file: SupportsRead[Union[str, bytes]]
        :returns: Parameters dict as would be used in the Parameters UI main property field, and associated layout file name
        :rtype: dict and str or None and str or None
        """
        if type(file) is str:
            file = open(file, 'r')
        array_form = json.load(file)
        params = array_form['parameters']
        parameters = {}
        for p in params:
            parameters[p['Name']] = p
        if 'layout' in array_form.keys():
            layout = array_form['layout']
        else:
            layout = 'layout.json'
        if 'icon' in array_form.keys():
            icon_file = array_form['icon']
        else:
            icon_file = 'CMU_Tartans.png'
        return parameters, layout, icon_file
        
    def load(self, file_name: str = None) -> str:
        """Load parameters from file.
        
        :returns: file_name (Filename for parameters file).
        :rtype: str
        """
        if file_name is not None:
            self._parameters, self._layout_file, self._icon_file = GameParameters.json_array_2_params_property(file_name)
    
    def items(self):
        return self._parameters.items()
    
    def keys(self):
        return self._parameters.keys()
    
    def log(self) -> int:
        """Log parameters to file ("incomplete" version is saved)."""
        self._index = self._index + 1
        with open(self.log_file, 'w') as parameters_log:
            parameters_log.write('Parameter\tValue\tUnits\n')
            for k, v in self._parameters.items():
                if 'Units' not in v.keys():
                    v['Units'] = 'None'
                if type(v['Value']) is not list:
                    parameters_log.write('{name}\t{value}\t{units}\n'.format(name=k,
                                                                             value=v['Value'],
                                                                             units=v['Units']))
            parameters_log.close()
        return self._index
    
    @property 
    def log_file(self) -> str:
        return os.path.join(os.path.abspath(self.paths['trials']),
                            self.get('Subject'),
                            'Behavior',
                            '{subject}{delimiter}{session}{delimiter}params-{index}.txt'.format(
                                subject=self.get('Subject'),
                                delimiter=self.filename_delimiter,
                                session=self.session,
                                index=self._index))
    
    def save(self) -> bool:
        """Save parameters callback method.

        :returns: True if save was successful, otherwise False.
        :rtype: bool
        """
        tmp = askdirectory(mustexist=True, initialdir=self.paths['save'])
        if len(tmp) == 0:
            return False
        else:
            self.paths['save'] = tmp
        # Format output
        out = dict(parameters=[])
        data = {}
        for k in self._parameters.keys():
            data[k] = self >> k
            out['parameters'].append(data[k])
        out['icon'] = self._icon_file
        out['layout'] = self._layout_file
        # print(out);
        with open(self.save_name, 'wt') as f:
            json.dump(out, f, indent=2)
            f.close()
        # Update defaults file for this subject as well.
        updated_default_file = os.path.join(os.path.abspath(self.paths['load']),
                                            'params_{subj}.json'.format(subj=self.get('Subject')))
        with open(updated_default_file, 'wt') as ud:
            json.dump(out, ud, indent=2)
            ud.close()
        return True        
    
    def setPageIndex(self, name: str, index: int) -> None:
        """Set the page index for a specific parameter."""
        self._parameters[name]['PageIndex'] = index
    
    def update(self, parameters) -> None:
        """Update a specific parameter value."""
        for name, value in parameters.items():
            if type(value) in (dict, object):
                formatted_name = name.replace(' ', '_')
                self.debug("data.parameters.{name}={value}".format(name=formatted_name, value=value['Value']), 1)
                self._parameters[name]['Value'] = value['Value']
            else:
                formatted_name = name.replace(' ', '_')
                self.debug("data.parameters.{name}={value}".format(name=formatted_name, value=value), 1)
                self._parameters[name]['Value'] = value
        
    def update_all(self, parameters: dict) -> None:
        """Update all parameters using the main parameters_ui dict."""
        self._parameters = parameters
        if self.logging is not None:
            for name, value in parameters.items():
                formatted_name = name.replace(' ', '_')
                self.debug("data.parameters.{name}={value}".format(name=formatted_name, value=value), 1)

    def pthread_target(self):
        asyncio.run(self.parameter_thread())
                                        
    async def parameter_thread(self):
        print("GameParameters initialized!")
        while True:
            await self.server_message_handler()
            print(self.as_dict())
 
async def main():
    parameters = GameParameters()
    while True:
        await asyncio.sleep(0.25)
 

if __name__ == "__main__":
    asyncio.run(main())
