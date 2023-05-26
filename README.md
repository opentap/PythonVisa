## PythonVisa

Use PyVISA and PyVISA-py to supply VISA instrument communication to [Keysight OpenTAP](https://opentap.io/) when a vendor implementation is not available.

## Dependencies / Pre-requisites

- [.NET 6](https://dotnet.microsoft.com/en-us/download/dotnet/6.0)
- [Python 3.7+](https://www.python.org/downloads/)
- [OpenTAP 9.20.0+ _(needed for dynamic VISA loading)_](https://packages.opentap.io/#name=%2FPackages%2FOpenTAP&version=9.20.0)
- [OpenTAP Python plugin 3.0.0+](https://packages.opentap.io/#name=%2FPackages%2FPython)
- [PyVISA](https://github.com/pyvisa/pyvisa), [PyVISA-py](https://github.com/pyvisa/pyvisa-py), [PyVISA-sim (optional)](https://github.com/pyvisa/pyvisa-sim)

## Build

```
# build a release version of the plugin
dotnet build -c Release

# package the plugin into a .TapPackage
./bin/tap package create -v --project-directory ./ ./package.xml

# install the package into the local copy of OpenTAP
cd ./bin
./tap package install -v ../*.TapPackage

# install the Python pre-requisites for the plugin
./tap python install-requirements -v
```

## Test with pyvisa-sim instrument simulation

To test basic functionality, you can use the included ```idn.TapPlan``` from ```./test-files``` and [pyvisa-sim](https://github.com/pyvisa/pyvisa-sim) to test sending a SCPI commmand from OpenTAP to a virtual instrument. 

Further tests could be developed by creating more test plans and adding virtual commands to ```./test-files/simulation_instrument.yaml```

```
cp -R ./test_files/* ./bin/
cd ./bin

# run from the commandline
./tap run --non-interactive -v idn.TapPlan

# run from the TUI
./tap tui
```

## Connect to a real instrument

When the PythonVisa plugin is installed in OpenTAP, and no standard VISA vendor implementation is available, the plugin will automatically provide VISA connections for supported instrument communication types:
- Serial
- USB-TMC
- LAN VXI-11 (::INSTR) 
- LAN SOCKET (::SOCKET)

For more information about PyVISA-py's capabilities, see their website at https://pyvisa.readthedocs.io/projects/pyvisa-py
