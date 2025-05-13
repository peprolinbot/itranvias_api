def get_or_create(session, model, **kwargs):
    """Get or create the given model, in the given session, with the given arguments for search/creation"""

    instance = session.query(model).filter_by(**kwargs).first()
    if instance is not None:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True


def line_route_id_to_route_id(line_id: int, line_route_id: int) -> int:
    """
    Converts from a route id like `0` or `1` to a unique (beacause it is relative to the line) one

    :return: The line id plus one zero and the route id
    """

    # Note this might be actually adding two zeroes if the line_route_id >= 10? Idk
    return line_id * 100 + line_route_id
