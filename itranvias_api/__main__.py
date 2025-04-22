"""
@public
hi
"""

import argparse
import itranvias_api.queryitr as api

STATIC_DATA = api.info.get_general_info()


def line_id_to_name(line_id: int) -> str:
    return STATIC_DATA["lines"][line_id].name


def stop_id_to_name(stop_id: int) -> str:
    return STATIC_DATA["stops"][stop_id].name


def display_next_buses(buses_data: dict) -> None:
    if buses_data:
        for line_id, buses in buses_data.items():
            print(f"Line {line_id_to_name(line_id)}:")
            for bus in buses:
                print(
                    f"{" "*4}- 🚍 {bus.id:>3} | 📍 {bus.distance:<6} m | ⌛ {bus.time:>2} minutes"
                )
    else:
        print("It looks like there are no buses for this stop")


def display_route_stops_and_buses(route: api.models.Route) -> None:
    for stop in route.stops:
        stop_str = f"[🚏 {stop.id} - {stop_id_to_name(stop.id)}]"
        buses_str = ""

        # Check for buses at this stop or have this as last stop
        buses_for_stop = route.buses.get(stop.id, [])

        for bus in buses_for_stop:
            bus_str = f"[🚍 {bus.id}]"

            if bus.at_stop:
                # We add the bus to the left of the stop string
                stop_str = f"{bus_str} - {stop_str}"
            else:
                buses_str += f"{bus_str}\n{" "*4}|"

        print(f"{stop_str}\n{" "*4}|")
        if buses_str != "":
            print(buses_str)


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
    line_parser.add_argument(
        "line_id", type=int, help="The bus line id to query.")
    line_parser.add_argument(
        "route_id",
        type=int,
        help="The route id of the line to query (usually 0 outbound/ida, 1 return/vuelta).",
    )

    args = parser.parse_args()

    if args.command == "stop":
        print(f"Buses for stop {args.stop_id} ({
              stop_id_to_name(args.stop_id)}):\n")
        next_buses = api.stops.get_stop_buses(args.stop_id)
        display_next_buses(next_buses)
    elif args.command == "line":
        routes = api.lines.get_line_buses(args.line_id)
        route = routes[args.route_id]
        route.stops = STATIC_DATA["lines"][args.line_id].routes[args.route_id].stops
        display_route_stops_and_buses(route)


if __name__ == "__main__":
    main()
