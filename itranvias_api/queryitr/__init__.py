"""
# Introduction

This submodule wraps around the "queryitr" API used in the [official iTranvías web client](https://itranvias.com), found at `https://itranvias.com/queryitr_v3.php`

# Quick example

This is a snippet of [`itranvias-cli`](https://github.com/peprolinbot/itranvias_api/blob/master/itranvias_api/__main__.py):

``` python
buses_data = api.stops.get_stop_buses(args.stop_id)

if buses_data:
    for line_id, buses in buses_data.items():
        print(f"Line {line_id_to_name(line_id)}:")
        for bus in buses:
            print(
                f"{" "*4}- 🚍 {bus.id} | 📍 {bus.distance}m | ⌛ {bus.time} minutes"
            )
else:
    print("It looks like there are no buses for this stop")
```
"""

from .queryitr_adapter import QueryItrAdapter as _QueryItrAdapter
from .known_servers import ITRANVIAS_WEB as _QUERYITR_URL

_queryitr_adapter = _QueryItrAdapter(_QUERYITR_URL)

from . import lines
from . import stops
from . import info
from . import models
from . import bus


__all__ = ["lines", "stops", "info", "models", "bus"]
