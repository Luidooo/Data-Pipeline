from api.config import Base, engine


def init_db():
    Base.metadata.create_all(bind=engine)


def drop_db():
    Base.metadata.drop_all(bind=engine)


def reset_db():
    drop_db()
    init_db()
