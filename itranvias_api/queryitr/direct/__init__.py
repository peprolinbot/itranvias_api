"""
# Introduction

This submodule is a dumb python wrapper that just parses function arguments to API parameters and fixes some small things, but most of the time returns the exact response from the API.

Remeber to check https://tpgalicia.github.io/urban/coruna for more info about the API.

# Quick example

This will list the next buses for a stop (a simplified version of itranvias-cli):

``` python
import itranvias_api.queryitr.direct as api

stop_id = input("Enter a stop id: ")

buses_data = api.stops.get_stop_buses(stop_id)

print()

if buses_data:
    for line_data in buses_data:
        line_id = line_data["linea"]
        buses = line_data["buses"]

        print(f"Line {line_id}:")

        for bus in buses:
            print(f"{" "*4}- 🚍 {bus["bus"]:>3} | 📍 {bus["distancia"]:<6}m | ⌛ {bus["tiempo"]:>2} minutes")
else:
    print("It looks like there are no buses for this stop")

```
"""

from ..queryitr_adapter import QueryItrAdapter as _QueryItrAdapter
from ..known_servers import ITRANVIAS_WEB as _QUERYITR_URL

_queryitr_adapter = _QueryItrAdapter(_QUERYITR_URL)

from . import lines
from . import stops
from . import info


__all__ = ["lines", "stops", "info"]
