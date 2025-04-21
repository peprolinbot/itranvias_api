from . import _queryitr_adapter
from .models import Stop, Line, Route, Bus, Location


def get_all_lines() -> dict[int, Line]:
    """
    Get information about all of the lines (`id`, `name`, `color`, `origin` & `destination` names)

    :return: A dict of `Line`s with keys the line ids.
    """

    response = _queryitr_adapter.get(func=1)
    data = response.data

    lines = {}
    for line in data["lineas"]:
        line_id = int(line["id"])
        lines[line_id] = Line(
            id=line_id,
            name=line["nom_comer"],
            color=line["color_linea"],
            origin=Stop(name=line["orig_linea"]),
            destination=Stop(name=line["dest_linea"]),
        )

    return lines


def get_line_buses(line_id: int) -> dict[int, Route]:
    """
    Fetch real-time information about about a line's buses

    :param line_id: The id of the line to consult

    :return: A dict with keys the route ids (usually 0 outbound/ida, 1 return/vuelta), each containig a route with buses in that line (`id`, `last_stop` (id), `state` and `route_progress`)
    """

    response = _queryitr_adapter.get(func=2, dato=line_id)
    data = response.data

    routes = {}
    for route in data["paradas"]:
        route_id = int(route["sentido"])

        buses = {}
        for stop in route["paradas"]:
            buses[stop["parada"]] = []
            for bus in stop["buses"]:
                buses[stop["parada"]].append(
                    Bus(
                        id=bus["bus"],
                        state=bus["estado"],
                        route_progress=bus["distancia"],
                        last_stop=Stop(stop["parada"]),
                    )
                )

        routes[route_id] = Route(id=route_id, buses=buses)

    return routes


def get_line_maps(line_id: int, show: str = "PRB") -> dict[int, Route]:
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
    data = response.data["mapas"]

    routes = {}

    def _create_route_if_missing(id: int) -> None:
        if routes.get(id) is None:
            routes[id] = Route(id=id)

    def _parse_stops(routes_data: list[dict]) -> None:
        for route in routes_data:
            route_id = int(route["sentido"])

            _create_route_if_missing(route_id)
            for stop in route["paradas"]:
                routes[route_id].stops.append(
                    Stop(
                        id=stop["id"],
                        name=stop["parada"],
                        lat=stop["posx"],
                        long=stop["posy"],
                    )
                )

    def _parse_paths(routes_data: list[dict]) -> None:
        for route in routes_data:
            route_id = int(route["sentido"])

            _create_route_if_missing(route_id)
            # String is "{lat},{long},0 {lat},{long},0 ..."
            for point in route["recorrido"].split():
                lat, long, idk = point.split(",")  # Idk what the 0 is for
                routes[route_id].path.append(
                    Location(
                        lat=lat,
                        long=long,
                    )
                )

    def _parse_buses(routes_data: list[dict]) -> None:
        print(routes_data)
        for route in routes_data:
            route_id = int(route["sentido"])

            _create_route_if_missing(route_id)
            for bus in route["buses"]:
                routes[route_id].buses.append(
                    Bus(id=bus["bus"], lat=bus["posx"], long=bus["posy"])
                )

    for map_dict in data:
        for key, function in {
            "paradas": _parse_stops,
            "recorridos": _parse_paths,
            "buses": _parse_buses,
        }.items():
            routes_data = map_dict.get(key)
            if routes_data is not None:
                function(routes_data)
                break

    return routes


def get_line_stop_map(line_id: int) -> dict[int, Route]:
    """
    Calls `get_line_maps` but only gets the stops map
    """

    return get_line_maps(line_id=line_id, show="P")


def get_line_paths(line_id: int) -> dict[int, Route]:
    """
    Calls `get_line_maps` but only gets the paths map
    """

    return get_line_maps(line_id=line_id, show="R")


def get_line_bus_map(line_id: int) -> dict[int, Route]:
    """
    Calls `get_line_maps` but only gets the buses map
    """

    return get_line_maps(line_id=line_id, show="B")
