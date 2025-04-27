import itranvias_api.queryitr.cached as api

api.db.initialize_database()

session = api.db.get_session()
# api.updaters.get_general_info(session)

line = session.query(api.models.Line).filter_by(id=100).first()
print(line)
print(line.stops)
print([x.stop for x in line.routes[0].stops])
