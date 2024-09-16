import os
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()
DSN = os.getenv('DSN')
Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)

    age = sq.Column(sq.Integer)
    gender = sq.Column(sq.String)
    city = sq.Column(sq.String)

    matches = relationship("Matches", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorites", back_populates="user", cascade="all, delete-orphan")
    blacklist = relationship("BlackList", back_populates="user", cascade="all, delete-orphan")


class Matches(Base):
    __tablename__ = "matches"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    matched_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    profile_link = sq.Column(sq.String, nullable=False)

    photo_url_1 = sq.Column(sq.String)
    photo_url_2 = sq.Column(sq.String)
    photo_url_3 = sq.Column(sq.String)

    user = relationship("Users", back_populates="matches")


class Favorites(Base):
    __tablename__ = "favorites"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    favorite_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    profile_link = sq.Column(sq.String, nullable=False)

    user = relationship("Users", back_populates="favorites")


class BlackList(Base):
    __tablename__ = "blacklist"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    blocked_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)

    user = relationship("Users", back_populates="blacklist")


def add_to_blacklist(user_id, blocked_vk_id, first_name, last_name, session):
    """Добавляет пользователя в черный список"""
    existing_blacklist_entry = session.query(BlackList).filter_by(user_id=user_id, blocked_vk_id=blocked_vk_id).first()

    if existing_blacklist_entry:
        return True

    new_blacklist_entry = BlackList(
        user_id=user_id,
        blocked_vk_id=blocked_vk_id,
        first_name=first_name,
        last_name=last_name
    )

    session.add(new_blacklist_entry)
    session.commit()
    print(f"Пользователь {first_name} {last_name} добавлен в черный список.")


try:
    engine = create_engine(DSN)
    Base.metadata.create_all(engine)
    print("Таблицы успешно созданы.")
except SQLAlchemyError as e:
    print(f"Произошла ошибка при создании таблиц: {e}")

Session = sessionmaker(bind=engine)
session = Session()
