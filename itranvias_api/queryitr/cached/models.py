from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Numeric,
    Table
)
from sqlalchemy.orm import relationship, declarative_base
import os

from .utils import get_or_create, line_route_id_to_route_id
from .. import _queryitr_adapter

Base = declarative_base()

# Association table for the many-to-many relationship
line_stop = Table(
    "line_stop",
    Base.metadata,
    Column("line_id", Integer, ForeignKey("lines.id"), primary_key=True),
    Column("stop_id", Integer, ForeignKey("stops.id"), primary_key=True),
)


class RouteStop(Base):
    __tablename__ = "route_stops"

    route_id = Column(Integer, ForeignKey("routes.id"), primary_key=True)
    stop_id = Column(Integer, ForeignKey("stops.id"), primary_key=True)
    position = Column(Integer, nullable=False)  # Position of the stop on this line

    route = relationship("Route", back_populates="stops")
    stop = relationship("Stop", back_populates="routes")


class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    route = relationship("Route", foreign_keys=[route_id])
    line_id = Column(Integer, ForeignKey("lines.id"))
    line = relationship("Line", foreign_keys=[line_id])

    def __init__(self, id: int, route: "Route" = None, line: "Line" = None):
        self.id = id
        self.line = line
        self.route = route

    def __repr__(self):
        return f"Bus - ID: {self.id}"


class RTBus(Bus):
    """
    A bus with real-time info (**not** stored in database)
    """

    def __init__(
        self,
        id: int,
        route: "Route" = None,
        line: "Line" = None,
        time: str = None,
        distance: int = None,
        route_progress: float = None,
        state: int = None,
        last_stop: "Stop" = None,
        lat: float = None,
        long: float = None,
    ):
        super().__init__(id=id, route=route, line=line)

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

        self.lat: float = lat
        """
        Location (latitute)
        """

        self.lat: float = long
        """
        Location (longitude)
        """

    @property
    def at_stop(self) -> bool:
        """
        Wether the bus is at the stop (`last_stop`)
        """

        return self.state == 0


class Stop(Base):
    __tablename__ = "stops"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    lat = Column(Float)
    long = Column(Float)

    connections = relationship("Line", secondary="line_stop", back_populates="stops")

    routes = relationship("RouteStop", back_populates="stop")

    def __init__(
        self, id: int, name: str = None, lat: float = None, long: float = None
    ):
        self.id = id
        self.name = name
        self.lat = lat
        self.long = long

    def __repr__(self) -> str:
        return f"ID: {self.id} - Name: {self.name or '?'}"

    def get_next_buses(self, session: "Session") -> dict[int, list[RTBus]]:
        """
        Fetch information about a stop, including real-time info about buses

        :param session: The database session

        :return: A dictionary with keys the line ids that go trough that stop, each having a list of `RTBus`es
        """

        response = _queryitr_adapter.get(func=0, dato=self.id)
        data = response.data

        lines = {}

        for line_data in data["buses"].get("lineas", []):
            line_id = line_data["linea"]
            line, _ = get_or_create(session, Line, id=line_id)

            buses = []
            for bus_data in line_data.get("buses", []):
                bus_id = bus_data["bus"]

                bus, _ = get_or_create(session, Bus, id=bus_id)

                if bus.line != line:
                    if bus.line is not None:
                        bus.route = None  # It is most likely wrong

                    bus.line = line

                rt_bus = RTBus(
                    id=bus.id,
                    line=bus.line,
                    route=bus.route,
                    time=bus_data["tiempo"],
                    distance=bus_data["distancia"],
                    state=bus_data["estado"],
                    last_stop=get_or_create(session, Stop, id=bus_data["ult_parada"])[
                        0
                    ],
                )

                buses.append(rt_bus)

            lines[line_id] = buses
            # lines[line_id] = {"line": line, "buses": buses}

        session.commit()
        return lines


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)  # Full route ID
    origin_id = Column(Integer, ForeignKey("stops.id"))
    destination_id = Column(Integer, ForeignKey("stops.id"))
    path = Column(String)  # You might want to use a different type for path
    line_id = Column(Integer, ForeignKey("lines.id"))
    line = relationship("Line", foreign_keys=[line_id])

    origin = relationship("Stop", foreign_keys=[origin_id])
    destination = relationship("Stop", foreign_keys=[destination_id])

    # stops = relationship(
    #     "Stop",
    #     secondary="route_stops",
    #     order_by="RouteStop.position",
    #     back_populates="routes",
    # )
    stops = relationship(
        "RouteStop",
        back_populates="route",
        order_by="RouteStop.position",
    )

    buses = relationship("Bus", back_populates="route")

    def __init__(self, id: int, origin: Stop = None, destination: Stop = None):
        self.id = id
        self.origin = origin
        self.destination = destination

    def __repr__(self):
        return f"Route {self.id} ({'IDA' if self.id == 0 else 'VUELTA' if self.id == 1 else '?'})"

    @property
    def line_route_id(self) -> bool:
        """
        The last two digits of the general one. This one is not unique, usually 0 is outbound/ida and 1 return/vuelta.
        """

        return self.id % 100


class Line(Base):
    __tablename__ = "lines"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    origin_id = Column(Integer, ForeignKey("stops.id"))
    destination_id = Column(Integer, ForeignKey("stops.id"))
    color = Column(String)

    origin = relationship("Stop", foreign_keys=[origin_id])
    destination = relationship("Stop", foreign_keys=[destination_id])
    routes = relationship("Route", back_populates="line")
    stops = relationship(
        "Stop",
        secondary="line_stop",
        # Its generated from stops that have this line (not ordered)
        back_populates="connections",
    )

    def __init__(
        self,
        id: int,
        name: str = None,
        origin: Stop = None,
        destination: Stop = None,
        color: str = None,
    ):
        self.id = id
        self.name = name
        self.origin = origin
        self.destination = destination
        self.color = color

    def __repr__(self):
        return f"Line - ID: {self.id} - Name: {self.name or '?'}"

    def get_buses(self, session: "Session") -> dict:
        """
        Fetch real-time information about about a line's buses
        
        TODO DESCRIBE THE OUTPUT DICT

        :return: A dict with keys the route ids (usually 0 outbound/ida, 1 return/vuelta), each containig a route with buses in that line (`id`, `last_stop` (id), `state` and `route_progress`)
        """

        response = _queryitr_adapter.get(func=2, dato=self.id)
        data = response.data

        routes = {}
        for route_data in data["paradas"]:
            line_route_id = int(route_data["sentido"])
            route_id = line_route_id_to_route_id(self.id, line_route_id)
            route, _ = get_or_create(session, Route, id=route_id)

            stops = {}
            for stop_data in route_data["paradas"]:
                stop_id = stop_data["parada"]
                stop,_=get_or_create(session, Stop, id=stop_id)

                stops[stop_id] = {"stop":stop, "buses": {"at_stop": [], "moving":[]}}
                for bus_data in stop_data["buses"]:
                    bus_id = bus_data["bus"]

                    bus, _ = get_or_create(session, Bus, id=bus_id)

                    bus.line = self
                    bus.route = route

                    bus = RTBus(
                        id=bus.id,
                        line=bus.line,
                        route=bus.route,
                        route_progress=bus_data["distancia"],
                        state=bus_data["estado"],
                        last_stop=stop,
                    )

                    if bus.at_stop:
                        stops[stop_id]["buses"]["at_stop"].append(bus)
                    else:
                        stops[stop_id]["buses"]["moving"].append(bus)

            routes[line_route_id] = {"route": route, "stops": stops}

        session.commit()
        return routes


class NewsMessage(Base):
    __tablename__ = "news_messages"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    version = Column(String)
    title = Column(String)
    text = Column(String)

    def __init__(
        self,
        id: int,
        date: datetime,
        version: str,
        title: str,
        text: str,
    ):
        self.id = id
        self.date = date
        self.version = version
        self.title = title
        self.text = text

    def __repr__(self) -> str:
        return self.title


class Fare(Base):
    """
    A bus fare
    """

    __tablename__ = "fares"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Numeric(3, 2), nullable=False)

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
