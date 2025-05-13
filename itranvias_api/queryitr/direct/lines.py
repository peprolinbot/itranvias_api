from ..queryitr_adapter import QueryItrResponse

from . import _queryitr_adapter


def get_all_lines() -> list[dict[str, str]]:
    """
    Get information about all of the lines (`id`, `name`, `color`, `origin` & `destination` names)

    :return: A list of line information dicts like:
    ```python
    [
        {
            'id': '100',
            'nom_comer': '1',
            'color_linea': '982135',
            'orig_linea': 'Abente y Lago',
            'dest_linea': 'Castrillón',
            'dest_ida': 'Pza. Pablo Iglesias',
            'dest_vuelta': 'Abente y Lago'
        },
        # ...
        {
            'id': '2451',
            'nom_comer': 'UDC',
            'color_linea': 'D61D3F',
            'orig_linea': 'San Pedro de Mezonzo',
            'dest_linea': 'UDC',
            'dest_ida': 'Campus Zapa.,Filolo.',
            'dest_vuelta': 'San Pedro de Mezonzo'
        }
    ]
    ```
    """

    response = _queryitr_adapter.get(func=1)

    return response.data["lineas"]


def get_line_buses(line_id: int) -> list[dict]:
    """
    Fetch real-time information about about a line's buses

    :param line_id: The id of the line to consult

    :return: A list with a dict for each route, each having the route id ()`sentido`) and a key `paradas` containing a list of dictionaries with a stop id (`parada`) and buses info (`buses`).
    Each bus dictionary has:
    - `bus`: The bus identifier
    - `estado`: The "state" of the bus. Known values are:
        - `0`: At the stop
        - `1`: In motion
        - `17`: Incorporating into the route, on an extension or outside the normal round-trip itinerary.
    - `distancia`: A fraction (0-1) representing how much of the route the bus has travelled (supposing the stops are equidistant)

    An example output is:
    ```python
    [
        {
            'sentido': '0',
            'paradas': [
                {'parada': 523, 'buses': [{'bus': 420, 'estado': 0, 'distancia': 0}]},
                {'parada': 525, 'buses': [{'bus': 421, 'estado': 0, 'distancia': 0.737}]}
            ]
        },
        {
            'sentido': '1',
            'paradas': [
                {'parada': 74, 'buses': [{'bus': 378, 'estado': 1, 'distancia': 0.397}]},
                {'parada': 523, 'buses': [{'bus': 420, 'estado': 0, 'distancia': 1}]}
            ]
        }
    ]
    ```
    """

    response = _queryitr_adapter.get(func=2, dato=line_id)

    return response.data["paradas"]


def get_line_maps(line_id: int, show: str = "PRB") -> list[dict[str, list[dict]]]:
    """
    Get "maps" for a line. Can show different map types, depending on the letters included in `show`.

    :param line_id: The id of the line to consult

    :param show: Which maps to show, can include the following letters
        - **B**: Buses
        - **P**: Stops (Paradas)
        - **R**: Path (Recorrido)

    :return: A list of dicts (of requested map types), each containing a single key: `paradas`, `recorridos` or `buses`. Sample output below:
    ```python
    [
        {
            'paradas': [
                {
                    'sentido': '0',
                    'paradas': [
                        {'id': '523', 'parada': 'Abente y Lago', 'posx': -8.390042, 'posy': 43.367915},
                        # ...
                        {'id': '68', 'parada': 'Pza. Pablo Iglesias', 'posx': -8.397493, 'posy': 43.347475}
                    ]
                },
                {
                    'sentido': '1',
                    'paradas': [
                        {'id': '68', 'parada': 'Pza. Pablo Iglesias', 'posx': -8.397493, 'posy': 43.347475},
                        # ...
                        {'id': '523', 'parada': 'Abente y Lago', 'posx': -8.390042, 'posy': 43.367915}
                    ]
                }
            ]
        },
        {
            'recorridos': [
                {
                    'sentido': '0',
                    'recorrido': '-8.390046954030453,43.3679249875959,0 -8.390134954623605,43.36793330946492,0 (...) -8.397495434412111,43.34748309224358,0'
                },
                {
                    'sentido': '1',
                    'recorrido': '-8.397495434412111,43.34748309224358,0 -8.397533107906783,43.34744003962236,0 (...) -8.390050333093303,43.36791955300642,0'
                }
            ]
        },
        {
            'buses': [
                {
                    'sentido': '0',
                    'buses': [{'bus': 378, 'posx': -8.390113, 'posy': 43.367958}, {'bus': 420, 'posx': -8.39504, 'posy': 43.354617}]
                },
                {
                    'sentido': '1',
                    'buses': [{'bus': 421, 'posx': -8.406, 'posy': 43.353555}]
                }
            ]
        }
    ]
    ```
    """

    response = _queryitr_adapter.get(func=99, dato=line_id, mostrar=show)

    return response.data["mapas"]


def get_line_stop_map(line_id: int) -> list[dict]:
    """
    Calls `get_line_maps` but only gets the stops map

    :return: Sample output:
    ```python
    [
        {
            'sentido': '0',
            'paradas': [
                {'id': '523', 'parada': 'Abente y Lago', 'posx': -8.390042, 'posy': 43.367915},
                # ...
                {'id': '68', 'parada': 'Pza. Pablo Iglesias', 'posx': -8.397493, 'posy': 43.347475}
            ]
        },
        {
            'sentido': '1',
            'paradas': [
                {'id': '68', 'parada': 'Pza. Pablo Iglesias', 'posx': -8.397493, 'posy': 43.347475},
                # ...
                {'id': '523', 'parada': 'Abente y Lago', 'posx': -8.390042, 'posy': 43.367915}
            ]
        }
    ]
    ```
    """

    return get_line_maps(line_id=line_id, show="P")[0]["paradas"]


def get_line_paths(line_id: int) -> list[dict]:
    """
    Calls `get_line_maps` but only gets the paths map

    :return: Sample output:
    ```python
    [
        {
            'sentido': '0',
            'recorrido': '-8.390046954030453,43.3679249875959,0 -8.390134954623605,43.36793330946492,0 (...) -8.397495434412111,43.34748309224358,0'
        },
        {
            'sentido': '1',
            'recorrido': '-8.397495434412111,43.34748309224358,0 -8.397533107906783,43.34744003962236,0 (...) -8.390050333093303,43.36791955300642,0'
        }
    ]
    ```
    """

    return get_line_maps(line_id=line_id, show="R")[0]["recorridos"]


def get_line_bus_map(line_id: int) -> list[dict]:
    """
    Calls `get_line_maps` but only gets the buses map

    :return: Sample output:
    ```python
    [
        {
            'sentido': '0',
            'buses': [{'bus': 378, 'posx': -8.390113, 'posy': 43.367958}, {'bus': 420, 'posx': -8.39504, 'posy': 43.354617}]
        },
        {
            'sentido': '1',
            'buses': [{'bus': 421, 'posx': -8.406, 'posy': 43.353555}]
        }
    ]
    ```
    """

    return get_line_maps(line_id=line_id, show="B")[0]["buses"]
