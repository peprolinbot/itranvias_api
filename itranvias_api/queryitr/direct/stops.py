from ..queryitr_adapter import QueryItrResponse

from . import _queryitr_adapter


def get_stop_buses(stop_id: int) -> QueryItrResponse:
    """
    Fetch information about a stop, including real-time info about buses

    :param stop_id: The id of the stop to consult

    :return: A dictionary with keys the line ids that go trough that stop, each having a list of `Bus`es
    """

    response = _queryitr_adapter.get(func=0, dato=stop_id)

    return response
