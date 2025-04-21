"""
Here are all the models (classes) used
"""

from datetime import datetime


class Location:
    """
    A location (latitude and longitude)
    """

    def __init__(self, lat: float, long: float) -> None:
        self.lat: float = float(lat)
        """
        Latitude
        """

        self.long: float = float(long)
        """
        Longitude
        """

    def __repr__(self):
        return f"Lat: {self.lat}, Long: {self.long}"


class Stop:
    """
    A bus stop
    """

    def __init__(
        self,
        id: int = None,
        name: str = None,
        connections: list["Line"] = [],
        location: Location = None,
        lat: float = None,
        long: float = None,
    ) -> None:
        self.id: int = id
        """
        Id of the stop. This is the one shown on the bus stop poles
        """

        self.name: str = name
        """
        Name of the stop
        """

        self.location: Location = location or (
            Location(lat, long) if lat and long else None
        )
        """
        Location of the stop
        """

        self.connections: list["Line"] = connections
        """
        List of lines which can be taken on the stop
        """

    def __repr__(self) -> str:
        return f"ID: {self.id} - Name: {self.name or "?"}"


class Bus:
    """
    A bus which is giving service to a certain line
    """

    def __init__(
        self,
        id: int,
        time: str = None,
        distance: int = None,
        route_progress: float = None,
        state: int = None,
        last_stop: Stop = None,
        location: Location = None,
        lat: float = None,
        long: float = None,
    ):
        self.id: int = id
        """
        Id of the bus (the number they have in real life)
        """

        self.time: str = time
        """
        Time left (in minutes) for the bus to arrive at the queried stop.
        
        **Note:** It will be "<1" when there is less than one minute left.
        """

        self.distance: int = distance
        """
        The distance left to the queried stop (in meters)
        """

        self.route_progress: float = route_progress
        """
        Number between 0 and 1 representing the distance between the percentage of the route that has already been travelled.
        E.g 0.287 means that the bus has travelled 28.7% of the route already
        """

        self.state: int = state
        """
        Bus state

        - **0:** At a stop
        - **1:** Moving
        - **17:** Incorporating into the route, in an extension or outside the normal round trip itinerary.
        """

        self.last_stop: Stop = last_stop
        """
        The last stop the bus was in
        """

        self.location: Location = location or (
            Location(lat, long) if lat and long else None
        )
        """
        Location (real-time position) of the bus
        """

    @property
    def at_stop(self) -> bool:
        """
        Wether the bus is at the stop (`last_stop`)
        """

        return self.state == 0

    def __repr__(self):
        return f"Bus {self.id}"


class Route:
    """
    A route for a bus line
    """

    def __init__(
        self,
        id: int,
        origin: Stop = None,
        destination: Stop = None,
        stops: list[Stop] = None,
        buses: dict[int, list[Bus]] = None,
        path: list[Location] = None,
    ):
        self.id: int = id
        """
        Id of the route

        **Usually:**
        - Direction 0 is the outbound (IDA)
        - Direction 1 is the return (VUELTA)
        - Directions 2-5 are variants or extensions,
        - irection 30 is the return to the depot
        """

        self.origin: Stop = origin
        """
        Origin stop
        """

        self.destination: Stop = destination
        """
        Destination stop
        """

        self.stops: list[Stop] = stops if stops is not None else []
        """
        List of stops for this route
        """

        self.buses: dict[int, list[Bus]] = buses if buses is not None else {}
        """
        Dictionary of buses giving service to this route, with keys their last stop
        """

        self.path: list[Location] = path if path is not None else []
        """
        List of points in the map forming this route's path
        """

    def __repr__(self):
        return f"Route {self.id} ({'IDA' if self.id==0 else "VUELTA" if self.id==1 else "?"})"


class Line:
    """
    A bus line
    """

    def __init__(
        self,
        id: int,
        name: str = None,
        origin: Stop = None,
        destination: Stop = None,
        color: str = None,
        routes: list[Route] = None,
    ):
        self.id: int = id
        """
        Id of the line. It usually is the name with two extra 0s, e.g. line 24's id is 2400 and line 1's is 100.
        But if it is a "variation" of the line, a number is added to the base line id, e.g. line 23A's id is 2301 and 1A's is 1900
        """

        self.name: str = name
        """
        Name of the line, e.g. 1A
        """

        self.origin: Stop = origin
        """
        Origin stop
        """

        self.destination: Stop = destination
        """
        Destination stop
        """

        self.color: str = color
        """
        Color of the line, in hexadecimal (RRGGBB), e.g. 982135 for L1
        """

        self.routes: str = routes if routes is not None else []
        """
        List of routes this line has
        """

    def __repr__(self):
        return f"Line - ID: {self.id} - Name: {self.name or "?"}"


class NewsMessage:
    """
    A news message of the *iTranvías* app
    """

    def __init__(
        self,
        id: int,
        date: datetime,
        version: str,
        title: str,
        text: str,
    ):
        self.id: int = id
        """
        Id of the message
        """

        self.date: datetime = date
        """
        The date when the message was created
        """

        self.version: str = version
        """
        The version of *iTranvías* this refers to
        """

        self.title: str = title
        """
        The message's notification title
        """

        self.text: str = text
        """
        The message's actual content. It usually is HTML
        """

    def __repr__(self) -> str:
        return self.title


class Fare:
    """
    A bus fare
    """

    def __init__(
        self,
        name: str,
        price: float,
    ):
        self.name: str = name
        """
        The fare name/description
        """

        self.price: float = price
        """
        The bus price in euros using this fare (same for all lines)
        """

    def __repr__(self) -> str:
        return f"{self.name} ({self.price}€)"
