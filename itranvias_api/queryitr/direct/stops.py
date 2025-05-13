from ..queryitr_adapter import QueryItrResponse

from . import _queryitr_adapter


def get_stop_buses(stop_id: int) -> list[dict]:
    """
    Fetch information about a stop, including real-time info about buses

    :param stop_id: The id of the stop to consult

    :return: A list of dictionaries (ordered by the line that has the next bus sooner), each having a key `linea`, the line id those coming `buses` are for (a list of dicts)
    ```python
    [
        {
            "linea": 2400,
            "buses": [
                {
                    "bus": 367, # The bus identifier
                    "tiempo": "26", # The time remaining for it to arrive (minutes) or "<1"
                    "distancia": "9853", # The remaining distance in meters
                    "estado": 1, # The state, `0` is moving, `1` is at stop (not neccesarily the target one)
                    "ult_parada": 571, # The last stop this bus visited
                }
            ],
        },
        {
            "linea": 1700,
            "buses": [
                {
                    "bus": 427,
                    "tiempo": "41",
                    "distancia": "9084",
                    "estado": 1,
                    "ult_parada": 40,
                },
            ],
        },
    ]
    ```
    """

    response = _queryitr_adapter.get(func=0, dato=stop_id)

    return response.data["buses"].get("lineas", [])
