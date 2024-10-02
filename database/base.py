"""Модуль для работы с базой данных.

Модуль содержит в себе классы для инициализации таблиц базы данных и
создания объекта сессии и соединения с базой данных.
"""
import os

import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()
DSN = os.getenv('DSN')

Base = declarative_base()

engine = create_engine(DSN)
Session = sessionmaker(bind=engine)


class Users(Base):
    """Инициализация таблицы пользователей, которые взаимодействуют с ботом."""
    __tablename__ = "users"

    user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    gender = sq.Column(sq.String)
    city = sq.Column(sq.String)

    matches = relationship(
        "Matches",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    favorites = relationship(
        "Favorites",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    blacklist = relationship(
        "BlackList",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Matches(Base):
    """Инициализация таблицы совпавших пользователей (мэтчи)."""
    __tablename__ = "matches"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    matched_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    profile_link = sq.Column(sq.String, nullable=False)
    photo_id_1 = sq.Column(sq.String)
    photo_id_2 = sq.Column(sq.String)
    photo_id_3 = sq.Column(sq.String)

    user = relationship("Users", back_populates="matches")


class Favorites(Base):
    """Инициализация таблицы избранных пользователей."""
    __tablename__ = "favorites"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    favorite_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    profile_link = sq.Column(sq.String, nullable=False)

    user = relationship("Users", back_populates="favorites")


class BlackList(Base):
    """Инициализация таблицы черного списка."""
    __tablename__ = "blacklist"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, ForeignKey("users.user_id"), nullable=False)
    blocked_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    profile_link = sq.Column(sq.String, nullable=False)

    user = relationship("Users", back_populates="blacklist")
