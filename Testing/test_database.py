# Runs pytests on the database code

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .db_models_testing import User, RSS_Data, Tags, User_Website_Link, Base


# Database setup
def create_session():
    """This function is run to initialise a fresh database instance for every function"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


# Test functions
def test_create_user_website_link():
    # Creates temporary session
    session = create_session()

    # Creates a user, an rss data entry, and links them together
    user = User(email="testemail@example.com", password="password", username="testuser")
    rss_data = RSS_Data(title="Test Title", link="Test Link", tag=Tags(name="Test Tag"))
    session.add(user)
    session.add(rss_data)
    session.commit()

    user_website_link = User_Website_Link(user=user, rss_data=rss_data, clicks=0)
    session.add(user_website_link)
    session.commit()

    # Retrieves link from database
    retrieved_link = session.query(User_Website_Link).first()

    # Checks that the link parameters are as expected
    assert retrieved_link is not None
    assert retrieved_link.user == user
    assert retrieved_link.rss_data == rss_data
    assert retrieved_link.clicks == 0

    # Close temporary session
    session.close()


def test_delete_user():
    # Create temporary session
    session = create_session()

    # Creates a user instance and adds it to database
    user = User(email="testemail2@example.com", password="password", username="testuser")
    session.add(user)
    session.commit()

    # Then deletes the user instance from database
    session.delete(user)
    session.commit()

    # Checks if the user still exists
    user_existence = session.query(User).first()

    # Test case, expecting the user to be none
    assert user_existence is None

    # Close temporary session
    session.close()


def test_query():
    # Create temporary session
    session = create_session()

    # Creates a user and adds it to db
    user = User(email="testemail2@example.com", password="password", username="testuser")
    session.add(user)
    session.commit()

    #  Queries for the users
    users = session.query(User).all()

    # Test case to ensure the only user is as expected
    assert users[0].username == "testuser"

    # Close temporary session
    session.close()
