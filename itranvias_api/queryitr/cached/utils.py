def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance is not None:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True

def line_route_id_to_route_id(line_id:int,route_line_id:int)->int:
    return line_id * 10000 + route_line_id
