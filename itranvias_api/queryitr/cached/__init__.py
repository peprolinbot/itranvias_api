"""
# Introduction

This submodule uses SQLAlchmey and a SQLite database to store the static data, and wrap the `..direct` submodule.
Avoiding repeating requests, and allowing for a much more flexible approach to using the library, where all objects have all data.
Taking from the user the burden of programming all that caching system, now included in the library!! (batteries not included tho).

# General workings

There is a default `.database.Database`: `.database.default_db`, which makes it not neccesary for you to fiddle with it, 
although if you want you can (I hope, open an Issue if you have any problems).

# Quick example

Check [`itranvias-cli`](https://github.com/peprolinbot/itranvias_api/blob/master/itranvias_api/__main__.py).
"""

from . import updaters
from . import models
from . import database
