import random
import time
from typing import Annotated, Literal

from pydantic import BaseModel, Field



Direction = Literal["front", "right", "back", "left"]



ItemType = Literal[
    "potion",
    "book",
    "food",
    "drink",
    "other",
    ]


class Item(BaseModel):
    name: str
    type: ItemType
    effect_value: Annotated[int, Field(gt=0)]


class Character(BaseModel):
    name: str

    class Config:
        validate_assignment = True


class Player(Character):
    inventory: list[Item] = []


def create_player(name: str) -> Player:
    return Player(
        name=name,
        inventory=[Item(name="Health Potion", type="potion", effect_value=30)]
    )
