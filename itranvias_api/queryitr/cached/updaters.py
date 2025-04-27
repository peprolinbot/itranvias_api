from .. import _queryitr_adapter
from .models import Line, Route, Stop, NewsMessage, Fare, RouteStop
from .utils import get_or_create

from datetime import datetime


def get_general_info(
    session,
    last_request_date: datetime = datetime(2016, 1, 1),
    last_message_id: int = 0,
    last_message_date: datetime = datetime(2016, 1, 1),
    language: str = "en",
    fix_route_id: bool = True,
) -> dict:
    """
    Get general/"static" info about th iTranvías app news, lines, stops and fares. This is what the official client uses to update its database/cache of in-browser data

    Note that:
    - A news message is shown if its id is lower than `last_message_id` or its date previous to `last_message_date`
    - Other information is shown if it has changed since `last_request_date`

    :param last_request_date: The date of the last time lines, stops and fares info was consulted.

    :param last_message_id: The id of the last news message received

    :param last_message_date: The date of the last news message received

    :param language: The language to receive the information in

    :param fix_route_id: Wether to fix the route ids the API gives in this endpoints, since the id used everywhere else is the last two digits of this one

    :return: A dict with 5 keys:
    - `news`: A list of new (in respect to the given parameters) `itranvias_api.queryitr.models.NewsMessage`s
    - `last_update`: The last time the data (not including news) was updated on the server
    - `lines`: A dict of `itranvias_api.queryitr.models.Line`s with keys the line ids.
    - `stops`: A dict of `itranvias_api.queryitr.models.Stop`s with keys the stop ids.
    - `prices`: A dict with two keys:
        - `fares`: A list of `itranvias_api.queryitr.models.Fare`s
        - `observations`: A list of strings with some observations about the pricing, like transfers and special price for children
    """

    dato = f"{last_request_date.strftime('%Y%m%dT%H%M%S')}_{language}_{last_message_id}_{
        last_message_date.strftime('%Y%m%dT%H%M%S')}"
    response = _queryitr_adapter.get(func=7, dato=dato)
    data = response.data["iTranvias"]

    output = {
        "news": [],
        "last_update": None,
        "lines": {},
        "stops": {},
        "prices": {"fares": [], "observations": []},
    }

    for message_data in data["novedades"]:
        news_message_id = message_data["id"]

        news_message = session.query(NewsMessage).filter_by(id=news_message_id).first()

        if news_message is None:
            news_message = NewsMessage(
                id=message_data["id"],
                date=datetime.strptime(message_data["fecha"], "%Y%m%dT%H%M%S"),
                version=message_data["version"],
                title=message_data["titulo"],
                text=message_data["texto"],
            )

        output["news"].append(news_message)

    if data.get("actualizacion") is not None:

        output["last_update"] = datetime.strptime(
            data["actualizacion"]["fecha"], "%Y%m%dT%H%M%S"
        )

        for stop_data in data["actualizacion"]["paradas"]:
            stop_id = stop_data["id"]
            stop, _ = get_or_create(session, Stop, id=stop_id)

            stop.id = stop_id
            stop.name = stop_data["nombre"]
            stop.lat = stop_data["posx"]
            stop.long = stop_data["posy"]
            stop.connections = [
                get_or_create(session, Line, id=line_id)[0]
                for line_id in stop_data["enlaces"]
            ]

            output["stops"][stop_id] = stop

        for line_data in data["actualizacion"]["lineas"]:
            routes = []
            for route_data in line_data["rutas"]:
                route_id = route_data["ruta"]

                route, _ = get_or_create(session, Route, id=route_id)

                route.id = route_id

                with session.no_autoflush:
                    for position, stop_id in enumerate(route_data["paradas"]):
                        stop=session.query(Stop).filter_by(id=stop_id).first() # It has to exist, we created all of them before
                        new_route_stop = get_or_create(session, RouteStop, route=route, stop=stop, position=position)

                route.origin = (
                    session.query(Stop)
                    .filter_by(name=route_data["nombre_orig"])
                    .first()
                )
                route.destination = (
                    session.query(Stop)
                    .filter_by(name=route_data["nombre_dest"])
                    .first()
                )

                routes.append(route)

            line_id = line_data["id"]
            line, _ = get_or_create(session, Line, id=line_id)

            line.name = line_data["lin_comer"]

            route.origin = (
                session.query(Stop).filter_by(name=line_data["nombre_orig"]).first()
            )
            route.destination = (
                session.query(Stop).filter_by(name=line_data["nombre_dest"]).first()
            )

            line.color = line_data["color"]
            line.routes = routes

            output["lines"][line_id] = line

        for fare_data in data["actualizacion"]["precios"]["tarifas"]:
            fare_name = fare_data["tarifa"]
            fare_price = fare_data["precio"]
            fare = session.query(Fare).filter_by(name=fare_name).first()
            if fare is None:
                fare = Fare(name=fare_data["tarifa"], price=fare_data["precio"])
                session.add(fare)
            else:
                fare.price = fare_price
            output["prices"]["fares"].append(fare)

        output["prices"]["observations"] = data["actualizacion"]["precios"][
            "observaciones"
        ]

    session.commit()

    return output
