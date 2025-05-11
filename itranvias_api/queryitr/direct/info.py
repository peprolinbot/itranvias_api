from ..queryitr_adapter import QueryItrResponse

from . import _queryitr_adapter

from datetime import datetime


def get_general_info(
    last_request_date: datetime = datetime(2016, 1, 1),
    last_message_id: int = 0,
    last_message_date: datetime = datetime(2016, 1, 1),
    language: str = "en",
    fix_route_id: bool = True,
) -> QueryItrResponse:
    """
    Get general/"static" info about the iTranvías app news, lines, stops and fares. This is what the official client uses to update its database/cache of in-browser data

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

    dato = f"{last_request_date.strftime('%Y%m%dT%H%M%S')}_{language}_{last_message_id}_{last_message_date.strftime('%Y%m%dT%H%M%S')}"
    response = _queryitr_adapter.get(func=7, dato=dato)

    return response
