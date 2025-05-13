import argparse
import itranvias_api.queryitr.cached as api

def display_stop_next_buses(stop_id:int) -> None:
    stop=api.models.Stop.get(stop_id)
    print(f"Buses for {stop.name} ({stop.id}):\n")
    
    data = stop.get_next_buses()
    if data:
        for line_data in data.values():
            line = line_data["line"]
            buses = line_data["buses"]
            print(f"Line {line.name}:")
            for bus in buses:
                print(
                    f"{" "*4}- 🚍 {bus.id:>3} | 📍 {bus.distance:<6} m | ⌛ {bus.time:>2} minutes"
                )
    else:
        print("It looks like there are no buses for this stop")


def display_line_stops_and_buses(line_id:int,route_id:int) -> None:
    line = api.models.Line.get(line_id)
    routes=line.get_buses()
    route_data = routes[route_id]
    route = route_data["route"]
    stops_data=route_data["stops"]

    def bus_str(bus: api.models.RTBus) -> str:
        """Get a bus' string representation"""
        return f"[🚍 {bus.id}]"

    def stop_str(stop: api.models.Stop) -> str:
        """Get a stop's string representation"""
        return f"[🚏 {stop.id} - {stop.name}]"

    def print_separator()->None:
        """Print the `|` between lines"""
        print(f"{" "*4}|")

    for stop in route.stops:
        stop_data = stops_data.get(stop.id)

        if stop_data is None:
            print(stop_str(stop))
            print_separator()
            continue

        stop = stop_data["stop"]
        buses = stop_data["buses"]

        for bus in buses["at_stop"]:
            print(f"{bus_str(bus)} - ", end="")

        print(stop_str(stop))
        print_separator()

        for bus in buses["moving"]:
            print(bus_str(bus))
            print_separator()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Get real-time bus information for the city of A Coruña."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand for querying by stop
    stop_parser = subparsers.add_parser(
        "stop", help="Get next buses for a specific stop."
    )
    stop_parser.add_argument("stop_id", type=int, help="The stop ID to query.")

    # Subcommand for querying by line
    line_parser = subparsers.add_parser(
        "line", help="Get buses and stops 'diagram' for a specific line and route."
    )
    line_parser.add_argument("line_id", type=int, help="The bus line id to query.")
    line_parser.add_argument(
        "route_id",
        type=int,
        help="The route id of the line to query (usually 0 outbound/ida, 1 return/vuelta).",
    )

    args = parser.parse_args()

    api.database.default_db.update() # It's fast after the first time

    if args.command == "stop":
        display_stop_next_buses(args.stop_id)
    elif args.command == "line":
        display_line_stops_and_buses(args.line_id, args.route_id)


if __name__ == "__main__":
    main()
