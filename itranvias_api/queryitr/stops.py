from . import _queryitr_adapter
from .models import Stop, Line, Bus


def get_stop_buses(stop_id: int) -> dict[int, list[Bus]]:
    """
    Fetch information about a stop, including real-time info about buses

    :param stop_id: The id of the stop to consult

    :return: A dictionary with keys the line ids that go trough that stop, each having a list of `Bus`es
    """

    response = _queryitr_adapter.get(func=0, dato=stop_id)
    data = response.data

    lines = {}
    for line in data["buses"].get("lineas", []):
        buses = []
        for bus in line["buses"]:
            buses.append(
                Bus(
                    id=bus["bus"],
                    time=bus["tiempo"],
                    distance=bus["distancia"],
                    state=bus["estado"],
                    last_stop=Stop(bus["ult_parada"]),
                )
            )

        lines[line["linea"]] = buses

    return lines
