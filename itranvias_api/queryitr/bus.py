from . import _queryitr_adapter
from .models import Bus, Stop
from .lines import get_all_lines
from time import sleep

def get_working_buses() -> dict[int, Bus]:
    """
    Get all buses that are working now

    :return: A dict of `Bus`es with keys the bus id
    """
    lines = get_all_lines()
    buses = {}
    count = 0 # count to sleep to avoid 429

    for line_id in lines:
        response = _queryitr_adapter.get(func=2, dato=line_id)
        data = response.data
        for route in data["paradas"]:
            count += 1
            for stop in route["paradas"]:
                for bus in stop["buses"]:
                    bus_id = bus["bus"]
                    if bus_id not in buses:
                        ob_bus = Bus(
                            id=bus_id,
                            state=bus["estado"],
                            route_progress=bus["distancia"],
                            last_stop=Stop(stop["parada"]),
                        )
                        buses[bus_id] = ob_bus
            print(buses)
            if count == 10:
                sleep(10)
                count = 0
            else:
                sleep(1)
    return sorted(buses.values(), key=lambda b: b.id)