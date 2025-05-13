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
    Table,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Session

from ..direct.stops import get_stop_buses
from ..direct.lines import get_line_buses
from .utils import get_or_create, line_route_id_to_route_id
from .database import default_db, default_session, Base


class AppModelBase(Base):
    """
    The Base model for things which are user-facing, with some useful functions
    """

    __abstract__ = True  # This makes sure this is not mapped to a table

    @classmethod
    def get(cls, id, session: Session = default_session):
        """Retrieve by primary key"""

        return session.query(cls).get(id)

    @classmethod
    def get_all(cls, session: Session = default_session):
        """Get all elements, ordered by id"""

        return session.query(cls).order_by(cls.id)


line_stop: Table = Table(
    "line_stop",
    Base.metadata,
    Column("line_id", Integer, ForeignKey("lines.id"), primary_key=True),
    Column("stop_id", Integer, ForeignKey("stops.id"), primary_key=True),
)
"""
@private

Association table for the many-to-many relationship for stop and line connections
"""


class RouteStop(Base):
    """
    @private

    Association table the many-to-many relationship between a route and its stops (ordered)
    """

    __tablename__ = "route_stops"

    route_id = Column(Integer, ForeignKey("routes.id"), primary_key=True)
    stop_id = Column(Integer, ForeignKey("stops.id"), primary_key=True)
    position = Column(Integer, nullable=False)
    """Position of the stop on this line"""

    route = relationship("Route", back_populates="_route_stops")
    stop = relationship("Stop", back_populates="_route_stops")


class Bus(AppModelBase):
    """
    A bus which is giving service to a certain line
    """

    __tablename__ = "buses"

    id = Column(Integer, primary_key=True)
    """
    Id of the bus (the number they have in real life)
    """

    _route_id = Column(Integer, ForeignKey("routes.id"))
    route = relationship("Route", foreign_keys=[_route_id])
    """
    The `Route` this bus is giving service to
    """
    _line_id = Column(Integer, ForeignKey("lines.id"))
    line = relationship("Line", foreign_keys=[_line_id])
    """
    The `Line` this bus is giving service to
    """

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
        The last stop the bus was (or is) in
        """

        self.lat: float = lat
        """
        Location (latitute)
        """

        self.long: float = long
        """
        Location (longitude)
        """

    @property
    def at_stop(self) -> bool:
        """
        Wether the bus is at the stop `last_stop`
        """

        return self.state == 0


class Stop(AppModelBase):
    """
    A bus stop
    """

    __tablename__ = "stops"

    id = Column(Integer, primary_key=True)
    """
    Id of the stop. This is the one shown on the bus stop poles
    """
    name = Column(String)
    """
    Name of the stop
    """
    lat = Column(Float)
    """
    Location (latitute)
    """
    long = Column(Float)
    """
    Location (longitute)
    """

    connections = relationship("Line", secondary="line_stop", back_populates="stops")
    """
    Which `Line`s can be taken from this stop
    """

    _route_stops = relationship("RouteStop", back_populates="stop")

    @hybrid_property
    def routes(self):
        """
        `Route`s passing through this stop
        """

        return [route_stop.route for route_stop in self._route_stops]

    def __repr__(self) -> str:
        return f"ID: {self.id} - Name: {self.name or '?'}"

    @classmethod
    def search(cls, name, session: Session = default_session):
        """
        Search for a stop by name (uses SQL `LIKE %{name}%`)

        :param name: The name to search for
        """

        return session.query(cls).filter(cls.name.like(f"%{name}%")).all()

    def get_next_buses(self, session: Session = default_session) -> dict[int, dict]:
        """
        Fetch information about a stop, including real-time info about buses

        :return: A dictionary with keys the line ids that go trough that stop, each having a dict with `line`, the corresponding `Line`, and `buses`, a list of `RTBus`.
        """

        data = get_stop_buses(self.id)

        lines = {}

        for line_data in data:
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

            lines[line_id] = {"line": line, "buses": buses}

        session.commit()
        return lines


class Route(AppModelBase):
    """
    A route for a bus line
    """

    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)
    """
    The full route ID (used in GTFS and func 7 of queryitr). See `.utils.line_route_id_to_route_id`
    """
    path = Column(String)  # TODO: You might want to use a different type for path
    """
    List of points in the map forming this route's path
    """

    _line_id = Column(Integer, ForeignKey("lines.id"))
    line = relationship("Line", foreign_keys=[_line_id])
    """
    The `Line` this route belongs to
    """

    origin_name = Column(String)
    """
    The name of the oirigin of this route, e.g. "Abente y Lago"
    """
    destination_name = Column(String)
    """
    The name of the oirigin of this route, e.g. "Carrillón"
    """

    _route_stops = relationship(
        "RouteStop",
        back_populates="route",
        order_by="RouteStop.position",
    )  # list[RouteStop]

    buses = relationship("Bus", back_populates="route")
    """
    List of `Bus`es giving service to this route. TODO: might move this to RTBus
    """

    @hybrid_property
    def stops(self):
        """
        `Stop`s (in order) of this route
        """
        return [route_stop.stop for route_stop in self._route_stops]

    def __repr__(self):
        return f"Route {self.id} ({'IDA' if self.id == 0 else 'VUELTA' if self.id == 1 else '?'})"

    @property
    def line_route_id(self) -> int:
        """
        The last two digits of the general one. This one is not unique.

        **Known values:**
        - Direction 0 is the outbound (IDA)
        - Direction 1 is the return (VUELTA)
        - Directions 2-5 are variants or extensions,
        - irection 30 is the return to the depot
        """

        return self.id % 100


class Line(AppModelBase):
    """
    A bus line
    """

    __tablename__ = "lines"

    id = Column(Integer, primary_key=True)
    """
    Id of the line. It usually is the name with two extra 0s, e.g. line 24's id is 2400 and line 1's is 100.
    But if it is a "variation" of the line, a number is added to the base line id, e.g. line 23A's id is 2301 and 1A's is 1900
    """
    name = Column(String)
    """
    Name of the line, e.g. 1A
    """
    priority = Column(Integer, unique=True)
    """
    Where this line would be in a list of all lines (lower value means higher priority)
    """
    color = Column(String)
    """
    Color of the line, in hexadecimal (RRGGBB), e.g. 982135 for L1
    """
    origin_name = Column(String)
    """
    The name of the oirigin of this line, e.g. "Abente y Lago"
    """
    destination_name = Column(String)
    """
    The name of the oirigin of this line, e.g. "Carrillón"
    """

    routes = relationship("Route", back_populates="line")
    """
    List of `Route`s this line has
    """
    stops = relationship(
        "Stop",
        secondary="line_stop",
        # Its generated from stops that have this line (not ordered)
        back_populates="connections",
    )
    """
    List of `Stop`s (**not** ordered) this line has
    """

    buses = relationship("Bus", back_populates="line")
    """
    List of `Bus`es giving service to this line
    """

    def __repr__(self):
        return f"Line - ID: {self.id} - Name: {self.name or '?'}"

    @classmethod
    def get_all(cls, session: Session = default_session):
        """
        We override this method to show the lines in their "natural order" (1,1A,2,...,UDC)
        """

        return session.query(cls).order_by(cls.priority)

    def get_buses(self, session: Session = default_session) -> dict[int, dict]:
        """
        Fetch real-time information about about this line's buses

        :return: A dict with keys the route ids (usually 0 outbound/ida, 1 return/vuelta), each containig a route and stops with buses for which that was their last or actual stop.
            An example output is:
            ```python
            {
                0: {
                    'route': <Route>,
                    'stops': {
                        523: {
                            'stop': <Stop>,
                            'buses': {
                                'at_stop': [<Bus>],
                                'moving': [<Bus>]
                            }
                        },
                        361: {
                            'stop': <Stop>,
                            'buses': {
                                'at_stop': [],
                                'moving': [<Bus>, <Bus>]
                            }
                        }
                    }
                },
                1: {
                    'route': <Route>,
                    'stops': {
                        371: {
                            'stop': <Stop>,
                            'buses': {
                                'at_stop': [<Bus>],
                                'moving': []
                            }
                        }
                    }
                }
            }
            ```
        """

        data = get_line_buses(self.id)

        routes = {}
        for route_data in data:
            line_route_id = int(route_data["sentido"])
            route_id = line_route_id_to_route_id(self.id, line_route_id)
            route, _ = get_or_create(session, Route, id=route_id)

            stops = {}
            for stop_data in route_data["paradas"]:
                stop_id = stop_data["parada"]
                stop, _ = get_or_create(session, Stop, id=stop_id)

                stops[stop_id] = {"stop": stop, "buses": {"at_stop": [], "moving": []}}
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


class NewsMessage(AppModelBase):
    """
    A news message of the *iTranvías* app
    """

    __tablename__ = "news_messages"

    id = Column(Integer, primary_key=True)
    """
    Id of the message
    """
    date = Column(DateTime)
    """
    The date when the message was created
    """
    version = Column(String)
    """
    The version of *iTranvías* this refers to
    """
    title = Column(String)
    """
    The message's notification title
    """
    text = Column(String)
    """
    The message's actual content. It usually is HTML
    """

    @classmethod
    def get_last(cls, session: Session = default_session):
        """
        Get the last message (highest id)
        """

        return session.query(cls).order_by(cls.id.desc()).first()

    def __repr__(self) -> str:
        return self.title


class Fare(AppModelBase):
    """
    A bus fare
    """

    __tablename__ = "fares"

    _id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    """
    The fare name/description
    """
    price = Column(Numeric(3, 2), nullable=False)
    """
    The bus price in euros using this fare (same for all lines)
    """

    def __repr__(self) -> str:
        return f"{self.name} ({self.price}€)"


class UpdaterMetadata(Base):
    """
    Metadata about an updater's updates to the database
    """

    __tablename__ = "updater_metadata"

    id = Column(Integer, primary_key=True)
    """
    Id of the updater source
    """
    last_updated = Column(DateTime, default=datetime(2016, 1, 1))
    """
    Last time the updater checked for updates
    """
    language = Column(String)
    """
    Language of the last downloaded data
    """

    @classmethod
    def get_default(cls, session: Session = default_session):
        """
        Get or create the default updater's metadata (id=0)
        """

        return get_or_create(session, cls, id=0)[0]

    def reset(cls, session: Session = default_session) -> None:
        """
        Reset the last_updated value to 01/01/2016
        """

        self.last_updated = datetime(2016, 1, 1)
        session.commit()

    def __repr__(self):
        return f"ID: {self.id} | Last updated: {self.last_updated}"


default_db.initialize_database()
