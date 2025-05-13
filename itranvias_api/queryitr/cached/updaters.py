from sqlalchemy.orm import Session
from datetime import datetime

from ..direct.info import get_general_info
from .models import Line, Route, Stop, NewsMessage, Fare, RouteStop, UpdaterMetadata
from .utils import get_or_create
from .database import default_db


def update_general_info(session: Session, *args, language: str, **kwargs) -> dict:
    """
    Calls `itranvias_api.queryitr.direct.info.get_general_info` (all parameters are forwarded)
    and the output is used to update the database. The returned output is reestructutred as explained below.

    :return: A dict with 5 keys:
    - `news`: A list of new (in respect to the given parameters) `itranvias_api.queryitr.models.NewsMessage`s
    - `last_update`: The last time the data (not including news) was updated on the server
    - `lines`: A dict of `itranvias_api.queryitr.models.Line`s with keys the line ids.
    - `stops`: A dict of `itranvias_api.queryitr.models.Stop`s with keys the stop ids.
    - `prices`: A dict with two keys:
        - `fares`: A list of `itranvias_api.queryitr.models.Fare`s
        - `observations`: A list of strings with some observations about the pricing, like transfers and special price for children
    """

    data = get_general_info(*args, **kwargs)

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
        metadata = UpdaterMetadata.get_default()
        metadata.last_updated = datetime.now()
        metadata.language = language

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

        for priority, line_data in enumerate(data["actualizacion"]["lineas"]):
            routes = []
            for route_data in line_data["rutas"]:
                route_id = route_data["ruta"]

                route, _ = get_or_create(session, Route, id=route_id)

                route.id = route_id

                with session.no_autoflush:
                    for position, stop_id in enumerate(route_data["paradas"]):
                        stop = (
                            session.query(Stop).filter_by(id=stop_id).first()
                        )  # It has to exist, we created all of them before
                        new_route_stop = get_or_create(
                            session,
                            RouteStop,
                            route=route,
                            stop=stop,
                            position=position,
                        )

                route.origin_name = route_data["nombre_orig"]
                route.destination_name = route_data["nombre_dest"]

                routes.append(route)

            line_id = line_data["id"]
            line, _ = get_or_create(session, Line, id=line_id)

            line.name = line_data["lin_comer"]
            line.priority = priority

            line.origin_name = line_data["nombre_orig"]
            line.destination_name = line_data["nombre_dest"]

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


def update_latest_general_info(session: Session, language: str):
    """
    Calls `update_general_info` with the `last_updated` parameter taken from the database,
    but forcing an update if the language changed since the last update
    """

    last_message = NewsMessage.get_last()
    last_message_id = None if last_message is None else last_message.id

    last_update_metadata = UpdaterMetadata.get_default()
    if last_update_metadata.language != language:
        last_updated = datetime(2016, 1, 1)
    else:
        last_updated = last_update_metadata.last_updated

    return update_general_info(
        session=session,
        last_request_date=last_updated,
        last_message_id=last_message_id,
        language=language,
    )


default_db.updater = update_latest_general_info


# TODO: Get line info thingys here
