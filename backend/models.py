import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

# ── ORM Models ────────────────────────────────────────────────────────────────


class Week(Base):
    __tablename__ = "weeks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    week_start: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")

    meals: Mapped[list["Meal"]] = relationship(
        "Meal", back_populates="week", cascade="all, delete-orphan"
    )
    ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient", back_populates="week", cascade="all, delete-orphan"
    )


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    week_id: Mapped[str] = mapped_column(String(36), ForeignKey("weeks.id", ondelete="CASCADE"))
    day: Mapped[str] = mapped_column(String(10), nullable=False)
    meal_type: Mapped[str] = mapped_column(String(10), nullable=False)
    dish1: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    dish2: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    optional_dish: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    soup: Mapped[Any | None] = mapped_column(JSON, nullable=True)

    week: Mapped["Week"] = relationship("Week", back_populates="meals")

    __table_args__ = (
        UniqueConstraint("week_id", "day", "meal_type"),
        Index("idx_meals_week_id", "week_id"),
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    week_id: Mapped[str] = mapped_column(String(36), ForeignKey("weeks.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[str | None] = mapped_column(Text, nullable=True)
    store: Mapped[str] = mapped_column(String(20), default="tnt")
    category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    checked: Mapped[bool] = mapped_column(Boolean, default=False)
    overridden: Mapped[bool] = mapped_column(Boolean, default=False)

    week: Mapped["Week"] = relationship("Week", back_populates="ingredients")

    __table_args__ = (Index("idx_ingredients_week_id", "week_id"),)


# ── Pydantic Schemas ──────────────────────────────────────────────────────────


class DishSchema(BaseModel):
    name: str
    tag: str
    style: str
    diff: int
    ingredients: str
    steps: list[str]
    search_query: str

    model_config = ConfigDict(from_attributes=True)


class MealSchema(BaseModel):
    id: str
    day: str
    meal_type: str
    dish1: dict | None = None
    dish2: dict | None = None
    optional_dish: dict | None = None
    soup: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class WeekSchema(BaseModel):
    id: str
    week_start: date
    generated_at: datetime | None = None
    status: str
    meals: list[MealSchema] = []

    model_config = ConfigDict(from_attributes=True)


class WeekSummarySchema(BaseModel):
    id: str
    week_start: date
    generated_at: datetime | None = None
    status: str
    dish_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class IngredientSchema(BaseModel):
    id: str
    name: str
    quantity: str | None = None
    store: str
    category: str | None = None
    checked: bool
    overridden: bool

    model_config = ConfigDict(from_attributes=True)


class MealUpdateRequest(BaseModel):
    dish_slot: str  # dish1 | dish2 | optional_dish | soup
    dish: dict


class IngredientUpdateRequest(BaseModel):
    checked: bool | None = None
    store: str | None = None
