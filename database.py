from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///static/app.db")
sesh = scoped_session(sessionmaker(autocommit=True,autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = sesh.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    models.dropTable('event')
    print(models.Event.eventdate.server_default)
    Base.metadata.create_all(bind=engine)




