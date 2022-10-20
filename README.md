# JSON Parameters Exporter
For building the parameters `json` files.

I made this in an attempt to avoid reinventing the wheel for each interface that requires some kind of a "parameter export." Currently (*2021-07-31*), it is lacking the functionality associated with the little `+` icon on each tab that would allow a nicer interface to specify types and values of different widgets and associate them to a corresponding tab.

## Setup ##

### Python Environment ###
The exporter interface was developed on `Windows 10` in `PyCharm` 2021.1 using `Python` 3.9. 

The machine **must have the GTK3 libraries installed**. I have only had a chance to test this on Windows 10 (64-bit), so if you try running on Linux or Mac there may be other dependencies and/or possible errors related to UNC path specifications (but hopefully not).

* `GTK3` ([Windows 64-bit](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer))

The following packages must be included in the `Python` environment (i.e. installed using `python pip3 install pymitter` etc.):

* `pymitter` (^0.3.0)
* `CairoSVG` (^2.5.2)
  * *Note:* installing `CairoSVG` (^2.5.2) requires the following dependencies:
    * `Pillow` (^8.2.0)
    * `cairocffi` (^1.2.0)
    * `cffi` (^1.14.5)
    * `cssselect2` (^0.4.1)
    * `defusedxml` (^0.7.1)
    * `pycparser` (^2.20)
    * `tinycss2` (^1.1.0)
    * `webencodings` (^0.5.1)
* `pycairo` (^1.20.0)
* `websockets` (^10.3)
* `asyncio` (^3.4.3)

### Interface ###

Main interface is accessed by running `main.py`.

## Use ##

### Standalone Version ###
1. Run `main.py`
2. Load `params-stim.json` from the user prompt.
   * The `params` file specifies the associated `layout.yaml` file that defines tabs.
   * Each parameter in the `params.json` file is associated to a tab by its `Page` field, which must match the `Title` field of a tab in the `layout.yaml` file.
3. Make changes to parameters as desired.
4. Click `save`. The filename is automatically generated based on a schema that I'd been using for collecting behavioral parameter metadata, but this could be adapted to suit an export for a `configuration.xml` output (and the `saveParameters` method of `component.ParametersUI.py` would be adjusted according to the `xml` specifications).

### Networked Version ###
1. Open a terminal in this repo.
2. In that terminal, run `python server.py`
3. Open a second terminal in this repo.
4. In that terminal, run `python main.py`
5. (Optional demo): In `docs`, open `index.html`. When you change any parameter in the `main.py` application, it should update the JSON string in the web interface via the server update.