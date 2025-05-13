from ..queryitr_adapter import QueryItrResponse

from . import _queryitr_adapter

from datetime import datetime


def get_general_info(
    last_request_date: datetime = datetime(2016, 1, 1),
    last_message_id: int = 0,
    last_message_date: datetime = datetime(2016, 1, 1),
    language: str = "en",
    fix_route_id: bool = True,
) -> dict:
    """
    Get general/"static" info about the iTranvías app news, lines, stops and fares. This is what the official client uses to update its database/cache of in-browser data

    Note that:
    - A news message is shown if its id is lower than `last_message_id` or its date previous to `last_message_date`
    - Other information is shown if it has changed since `last_request_date`

    :param last_request_date: The date of the last time lines, stops and fares info was consulted.

    :param last_message_id: The id of the last news message received

    :param last_message_date: The date of the last news message received

    :param language: The language to receive the information in

    :return: A dict with a lot of info (news,lines,stops,prices,...). Sample output here:
    ```python
    {
        "actualizacion": {
            "fecha": "20250509T143430",
            "lineas": [
                {
                    "id": 100,
                    "lin_comer": "1",
                    "nombre_orig": "Abente y Lago",
                    "nombre_dest": "Castrillón",
                    "color": "982135", # Hexadecimal
                    "rutas": [
                        {
                            "ruta": 10000,
                            "nombre_orig": "",
                            "nombre_dest": "",
                            "paradas": [523, 180, 1, 2, 3, 4, 5, 6, 7, 270, 271, 272, 416, 524, 525, 64, 65, 66, 67, 68]
                        },
                        {
                            "ruta": 10001,
                            "nombre_orig": "",
                            "nombre_dest": "",
                            "paradas": [68, 69, 70, 71, 72, 73, 74, 75, 41, 23, 24, 25, 26, 27, 28, 139, 140, 523],
                        },
                        # ...
                    ],
                }
                # ...
            ],
            "paradas": [
                {
                    "id": 1,
                    "nombre": "Puerta Real",
                    "posx": -8.39585,
                    "posy": 43.370115,
                    "enlaces": [100, 1900, 200, 800, 301, 1700, 2300, 2301],
                },
                # ...
                {
                    "id": 598,
                    "nombre": "Avenida Porto, A Terraza",
                    "posx": -8.402222,
                    "posy": 43.367285,
                    "enlaces": [],
                },
            ],
            "enlaces": {
                "origen": [
                    {
                        "linea": 100,
                        "sentidos": [
                            {
                                "sentido": 0,
                                "destinos": [{'linea': 200, 'sentidos': [0, 1]}, {'linea': 800, 'sentidos': [0, 1]}, {'linea': 1500, 'sentidos': [0, 1]}],
                            },
                            {
                                "sentido": 1,
                                "destinos": [{'linea': 200, 'sentidos': [0, 1]}, {'linea': 800, 'sentidos': [0]}, {'linea': 1500, 'sentidos': [0, 1]}],
                            },
                        ],
                    }
                    # ...
                ]
            },
            "precios": {
                "tarifas": [
                    {"tarifa": "Regular Rate(cash)", "precio": 1.3},
                    # ...
                    {"tarifa": "Transfer (card only)", "precio": 0},
                ],
                "observaciones": [
                    "Free transfer time limit is 45 minutes.",
                    # ...
                ],
            },
        },
        "novedades": [
            {
                "id": 3,
                "fecha": "20161114T093000",
                "version": "3.5",
                "titulo": "New in iTranvías V. 3.5",
                "texto": "<ul>\r\n\t\t\t\t\t\t\t\t\t<li>New Settings screen</li> (...)",
            }
        ]
    }
    ```
    """

    dato = f"{last_request_date.strftime('%Y%m%dT%H%M%S')}_{language}_{last_message_id}_{last_message_date.strftime('%Y%m%dT%H%M%S')}"
    response = _queryitr_adapter.get(func=7, dato=dato)

    return response.data["iTranvias"]
