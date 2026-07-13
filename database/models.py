"""
models.py

Normalized schema:

  countries (1) --- (N) destinations (1) --- (N) attractions
  users (N) --- (N) destinations   via  favorites
  destinations (1) --- (N) weather_snapshots
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database.database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    iso_code = Column(String(3), unique=True, nullable=True)
    currency = Column(String(10), nullable=True)
    language = Column(String(60), nullable=True)

    destinations = relationship("Destination", back_populates="country")


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=False)
    short_description = Column(String(300), nullable=True)
    category = Column(String(60), index=True, nullable=True)
    popularity_score = Column(Float, default=0.0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    source_url = Column(String(300), nullable=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    country = relationship("Country", back_populates="destinations")
    attractions = relationship(
        "Attraction", back_populates="destination", cascade="all, delete-orphan"
    )
    weather_snapshots = relationship(
        "WeatherSnapshot", back_populates="destination", cascade="all, delete-orphan"
    )
    favorited_by = relationship(
        "Favorite", back_populates="destination", cascade="all, delete-orphan"
    )


class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(
        Integer, ForeignKey("destinations.id"), nullable=False, index=True
    )
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(60), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    source_url = Column(String(300), nullable=True)

    destination = relationship("Destination", back_populates="attractions")


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(
        Integer, ForeignKey("destinations.id"), nullable=False, index=True
    )
    temperature_c = Column(Float, nullable=True)
    condition = Column(String(80), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    destination = relationship("Destination", back_populates="weather_snapshots")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    favorites = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "destination_id", name="uq_user_destination"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    destination_id = Column(
        Integer, ForeignKey("destinations.id"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    destination = relationship("Destination", back_populates="favorited_by")
