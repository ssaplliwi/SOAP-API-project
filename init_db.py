from db import Base, engine
from db_models import User, Account, Session

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("SQLite database initialized -> soap_demo.db")
