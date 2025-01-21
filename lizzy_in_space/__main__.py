import os
import sys
from typing import Self

import pygame
from pydantic import BaseModel, Field

from lizzy_in_space.models import Direction
from lizzy_in_space.utils.sprites import SpriteSheet

pygame.init()

# region Settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# endregion

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Adventure - Point & Click")

font = pygame.font.SysFont("arial", 18)


HEIGHT_START = {
    "front": 0,
    "right": 32,
    "back": 64,
    "left": 96,
}

class Character(BaseModel):
    sprite_sheet: SpriteSheet = Field(default=SpriteSheet("characters/test.png", PROJECT_ROOT))
    pos: tuple[int, int]
    direction: Direction = Field(default="front")
    speed: int = Field(default=5)
    front_frames: list[pygame.Surface] = Field(default_factory=list)
    back_frames: list[pygame.Surface] = Field(default_factory=list)
    left_frames: list[pygame.Surface] = Field(default_factory=list)
    right_frames: list[pygame.Surface] = Field(default_factory=list)
    frames: list[pygame.Surface] = Field(default_factory=list)
    current_frame: int = Field(default=0)
    animation_timer: float = Field(default=0.)
    animation_speed: float = Field(default=200.)

    @property
    def x(self) -> int:
        return self.pos[0]
    @x.setter
    def x(self, value: int) -> None:
        self.pos = (value, self.pos[1])

    @property
    def y(self) -> int:
        return self.pos[1]
    @y.setter
    def y(self, value: int) -> None:
        self.pos = (self.pos[0], value)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self: Self, **kwargs) -> None:
        if "pos" not in kwargs:
            kwargs["pos"] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(**kwargs)

        self.front_frames: list[pygame.Surface] = [
            self.sprite_sheet.get_image(
                16*i,
                HEIGHT_START["front"],
                16,
                32,
            ) for i in range(4)
        ]
        self.back_frames: list[pygame.Surface] = [
            self.sprite_sheet.get_image(
                16*i,
                HEIGHT_START["back"],
                16,
                32,
            ) for i in range(4)
        ]
        self.left_frames: list[pygame.Surface] = [
            self.sprite_sheet.get_image(
                16*i,
                HEIGHT_START["left"],
                16,
                32,
            ) for i in range(4)
        ]
        self.right_frames: list[pygame.Surface] = [
            self.sprite_sheet.get_image(
                16*i,
                HEIGHT_START["right"],
                16,
                32,
            ) for i in range(4)
        ]
        self.frames: list[pygame.Surface] = self.front_frames

    def handle_input(self, keys_pressed: tuple[bool, ...]) -> bool:
        moving = False
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.direction = "back"
            self.y -= self.speed
            moving = True
            self.frames = self.back_frames
        elif keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.direction = "front"
            self.y += self.speed
            moving = True
            self.frames = self.front_frames
        elif keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.direction = "left"
            self.x -= self.speed
            moving = True
            self.frames = self.left_frames
        elif keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.direction = "right"
            self.x += self.speed
            moving = True
            self.frames = self.right_frames

        return moving

    def update(self, dt: float, moving: bool) -> None:
        if moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
        else:
            self.current_frame = 0  # Reset to first frame when not moving

    def draw(self, surface: pygame.Surface) -> None:
        scaled_image = pygame.transform.scale(self.frames[self.current_frame], (32, 64))
        surface.blit(scaled_image, (self.x, self.y))



items_spritesheet = SpriteSheet("items/evolonline.png", PROJECT_ROOT)
items: dict[str, pygame.Surface] = items_spritesheet.get_named_images(
    32,
    32,
    [
        "cotton",
        "peaches",
        "apple",
        "cake",
        "brown_book",
        "thing",
        "leaf",
        "tusks",
        "golden_leaves",
        "purple_book",
        "dontknow",
        "turtle_shell",
        "water_drops",
        "flask",
        "ball",
        "potion1",
        "potion2",
        "potion3",
        "potion4",
        "potion5",
    ]
)

def main() -> None:
    clock = pygame.time.Clock()
    character = Character(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    book1 = items["brown_book"]

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys_pressed = pygame.key.get_pressed()
        moving = character.handle_input(keys_pressed)
        character.update(dt, moving)
        screen.fill((50, 150, 50))

        screen.blit(book1, (200, 200))
        character.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
