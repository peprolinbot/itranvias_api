from ..queryitr_adapter import QueryItrResponse

from . import _queryitr_adapter


def get_all_lines() -> QueryItrResponse:
    """
    Get information about all of the lines (`id`, `name`, `color`, `origin` & `destination` names)

    :return: A dict of `Line`s with keys the line ids.
    """

    response = _queryitr_adapter.get(func=1)

    return response


def get_line_buses(line_id: int) -> QueryItrResponse:
    """
    Fetch real-time information about about a line's buses

    :param line_id: The id of the line to consult

    :return: A dict with keys the route ids (usually 0 outbound/ida, 1 return/vuelta), each containig a route with buses in that line (`id`, `last_stop` (id), `state` and `route_progress`)
    """

    response = _queryitr_adapter.get(func=2, dato=line_id)

    return response


def get_line_maps(line_id: int, show: str = "PRB") -> QueryItrResponse:
    """
    Get "maps" for a line. Can show different map types, depending on the letters included in `show`.

    :param line_id: The id of the line to consult

    :param show: Which maps to show, can include the following letters
        - **B**: Buses
        - **P**: Stops (Paradas)
        - **R**: Path (Recorrido)

    :return: A dict with keys the route ids (usually 0 outbound/ida, 1 return/vuelta), each containig a route with `buses`, `stops` and `path` set as appropiate
    """

    response = _queryitr_adapter.get(func=99, dato=line_id, mostrar=show)

    return response


def get_line_stop_map(line_id: int) -> QueryItrResponse:
    """
    Calls `get_line_maps` but only gets the stops map
    """

    return get_line_maps(line_id=line_id, show="P")


def get_line_paths(line_id: int) -> QueryItrResponse:
    """
    Calls `get_line_maps` but only gets the paths map
    """

    return get_line_maps(line_id=line_id, show="R")


def get_line_bus_map(line_id: int) -> QueryItrResponse:
    """
    Calls `get_line_maps` but only gets the buses map
    """

    return get_line_maps(line_id=line_id, show="B")
