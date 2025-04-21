# itranvias_api 🚍

[![GitHub license](https://img.shields.io/github/license/peprolinbot/itranvias_api)](https://github.com/peprolinbot/itranvias_api)
[![PyPI version](https://img.shields.io/pypi/v/itranvias_api?label=pypi%20package)](https://pypi.org/project/itranvias_api)

Python API wrapper for the city of A Coruña public transport ran by *Cia. Tranvías de La Coruña, S.A.*.

## 📜 Documentation

Documentation can be found [here](https://peprolinbot.github.io/itranvias_api). 

For the time being there is only one submodule: `itranvias_api.queryitr` which implements all (that I know of) functionality in the [official iTranvías client](https://itranvias.com/), using the "queryitr" API used by it, found at `https://itranvias.com/queryitr_v3.php`.

## 🔧 Installation

Just run:

``` bash
pip install itranvias_api
```

## 🖥️ CLI client

I have written a very simple, very basic POC, CLI client using this library, it is avaliable as `itranvias-cli` once the package is installed.

### Usage:
```
usage: itranvias-cli [-h] {stop,line} ...

Get real-time bus information for the city of A Coruña.

positional arguments:
  {stop,line}
    stop       Get next buses for a specific stop.
    line       Get buses and stops 'diagram' for a specific line and route.

options:
  -h, --help   show this help message and exit
```

## ⚠️ Disclaimer

This project is **not** endorsed by, directly affiliated with, maintained by, sponsored by or in any way officially related with la *Xunta de Galicia*, *Concello da Coruña*, *Cia. Tranvías de La Coruña, S.A.*, *SISTEMAS OLTON, S.L.* or any of the companies and entities involved in the [official iTranvías app](https://itranvias.com/).

This software is provided 'as is' without any warranty of any kind. The user of this software assumes all responsibility and risk for its use. I shall not be liable for any damages or misuse of this software. Please use the code and information in this repo responsibly.
