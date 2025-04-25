from . import _queryitr_adapter
from .models import Bus, Stop
from .lines import get_all_lines
from time import sleep

def get_working_buses():
    lines = get_all_lines()
    buses = []
    count = 0

    for line_id in lines:
        response = _queryitr_adapter.get(func=2, dato=line_id)
        data = response.data
        for route in data["paradas"]:
            count += 1
            for stop in route["paradas"]:
                for bus in stop["buses"]:
                    buses.append(
                        Bus(
                            id=bus["bus"],
                            state=bus["estado"],
                            route_progress=bus["distancia"],
                            last_stop=Stop(stop["parada"]),
                        )
                    )
            if count == 10:
                sleep(10)
                count = 0
            else:
                sleep(1)
    
        

        
    return buses