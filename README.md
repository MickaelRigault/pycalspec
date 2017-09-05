# pycalspec
Simple python library to access (download, store,...) CalSpec spectrum

Details about calspec: http://www.stsci.edu/hst/observatory/crds/calspec.html

## Installation

using pip

[![PyPI](https://img.shields.io/pypi/v/pycalspec.svg?style=flat-square)](https://pypi.python.org/pypi/pycalspec)
```
sudo pip install pycalspec
```
or using git:
```
git clone https://github.com/MickaelRigault/pycalspec/
cd pycalspec
python setup.py install
```


## Usage

Have access to the coordinate of a CalSpec standard star:
```python
import pycalspec
print(pycalspec.std_radec("HZ2"))
>>>('04:12:43.551', '+11:51:48.75')
```

Get the standard star spectrum
```python
import pycalspec
hz2_spec = pycalspec.std_spectrum("HZ2")
```
To see the spectrum
```
hz2_spec.show()
```

Get the dictionary containing the list of standard stars and their coordinates:
```python
import pycalspec
print(pycalspec.io.calspec_data())
>>>{'10Lac': {'dec': '+39:03:00.97', 'ra': '22:39:15.679'},
>>> '1732526': {'dec': '+71:04:42.74', 'ra': '17:32:52.574'},
>>> '1740346': {'dec': '+65:27:14.97', 'ra': '17:40:34.684'},
>>> '1743045': {'dec': '+66:55:01.6', 'ra': '17:43:04.48'},
>>> ...}
```
