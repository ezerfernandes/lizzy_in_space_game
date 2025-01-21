# https://opengameart.org/content/items
from typing import Literal

import pygame

from lizzy_in_space.utils.sprites import SpriteSheet, get_named_images

__all__ = ["get_evolonline_items"]

# EvolonlineItem = Literal[
#     "turtle shell",
#     "piberries",
#     "manana",
#     "aquada",
#     "old book",
#     "squirrel's fur",
#     "lettuce",
#     "squirrel's claws",
#     "chick' feathers",
#     "book",
#     "turtle'shell fragment",
#     "turtle'shell",
#     "liquid dyable icon",
#     "elixir",
#     "egg",
# ]


EvolonlineItem = Literal[
    "cotton",
    "peaches",
    "apple",
    "cake",
    "old book",
    "thing",
    "lettuce",
    "tusks",
    "chick feathers",
    "book",
    "dontknow",
    "turtle shell",
    "water_drops",
    "flask",
    "egg",
    "potion1",
    "potion2",
    "potion3",
    "potion4",
    "potion5",
]

def get_evolonline_items() -> dict[EvolonlineItem, pygame.Surface]:
    spritesheet = SpriteSheet("items/evolonline.png")
    evolonline_items: dict[EvolonlineItem, pygame.Surface] = get_named_images(
        spritesheet,
        32,
        32,
        list(EvolonlineItem.__args__),
    )
    return evolonline_items
