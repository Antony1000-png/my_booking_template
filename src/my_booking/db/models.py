from sqlalchemy import Column, Integer, String, Float, Date, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    bookings = relationship("Booking", back_populates="room", cascade="all, delete-orphan")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=False)

    room = relationship("Room", back_populates="bookings")
