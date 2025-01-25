import os
import sys
from typing import Self

import pygame
from pydantic import BaseModel, Field

from lizzy_in_space.models import Direction
from lizzy_in_space.utils.sprites import SpriteSheet
from lizzy_in_space.items.evolonline import get_evolonline_items
from lizzy_in_space.items.overworld import get_overworld_items

pygame.init()

# region Settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# endregion

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Adventure - Point & Click")

font = pygame.font.SysFont("arial", 18)


class Character(BaseModel):
    sprite_sheet: SpriteSheet = Field(default=SpriteSheet("characters/lizzy2.png"))
    pos: tuple[int, int]
    direction: Direction = Field(default="front")
    speed: int = Field(default=5)

    frames_by_direction: dict[str, list[pygame.Surface]] = Field(default_factory=dict)
    current_frames: list[pygame.Surface] = Field(default_factory=list)
    current_frame_index: int = Field(default=0)

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

    @property
    def rect(self) -> pygame.Rect:
        # 32x64 if that’s your scaled draw size
        return pygame.Rect(self.x, self.y, 32, 64)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self: Self, **data) -> None:
        super().__init__(**data)
        self._load_frames()
        # Ensure current frames align with initial direction:
        self.current_frames = self.frames_by_direction[self.direction]

    def _load_frames(self) -> None:
        """
        Load frames for each direction from the sprite sheet.
        Adjust the offsets/width/height to match your sprite sheet.
        """
        height_start = {
            "front": 0,
            "right": 32,
            "back": 64,
            "left": 96,
        }

        for dir_name, offset_y in height_start.items():
            # Extract 4 frames horizontally
            frames = [
                self.sprite_sheet.get_image(
                    x=16 * frame_idx,
                    y=offset_y,
                    width=16,
                    height=32
                )
                for frame_idx in range(4)
            ]
            self.frames_by_direction[dir_name] = frames


    def _move(
        self, new_direction: Direction, dx: int, dy: int) -> None:
        """
        Update direction, position, and current frames.
        """
        self.direction = new_direction
        self.x += dx
        self.y += dy
        self.current_frames = self.frames_by_direction[self.direction]

    def handle_input(self, keys_pressed: tuple[bool, ...], obstacles: list[pygame.Rect]) -> bool:
        """
        Check which movement keys are pressed; update position
        and direction accordingly.
        Returns:
            bool: True if character is moving, else False.
        """
        old_x, old_y = self.x, self.y
        moving = False
        # You could allow diagonal movement by splitting out these conditions
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self._move("back", dx=0, dy=-self.speed)
            moving = True
        elif keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self._move("front", dx=0, dy=self.speed)
            moving = True
        elif keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self._move("left", dx=-self.speed, dy=0)
            moving = True
        elif keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self._move("right", dx=self.speed, dy=0)
            moving = True

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                # If collision, revert position
                self.x, self.y = old_x, old_y
                break  # No need to check further obstacles once collided

        return moving

    def update(self, dt: float, moving: bool) -> None:
        """
        Update animation frame if moving, otherwise reset to first frame.
        """
        if moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)
        else:
            self.current_frame_index = 0  # Reset to first frame when not moving

    def draw(self, surface: pygame.Surface) -> None:
        frame = self.current_frames[self.current_frame_index]
        scaled = pygame.transform.scale(frame, (32, 64))
        surface.blit(scaled, (self.x, self.y))


items = get_evolonline_items()
overworld_items = get_overworld_items()

def main() -> None:
    clock = pygame.time.Clock()
    character = Character(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    book1 = items["old book"]
    wooden_box = overworld_items["wooden box"]
    wooden_box_rect = wooden_box.get_rect(topleft=(300, 300))

    lettuce_list: list[pygame.Rect] = []
    lettuce_image = items["lettuce"]
    for i in range(10):
        rect = lettuce_image.get_rect(topleft=(20 * i, 100))
        lettuce_list.append(rect)

    obstacles = [wooden_box_rect,]
    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys_pressed = pygame.key.get_pressed()
        moving = character.handle_input(keys_pressed, obstacles)
        character.update(dt, moving)
        screen.fill((50, 150, 50))

        screen.blit(book1, (200, 200))
        screen.blit(wooden_box, (300, 300))

        for rect in lettuce_list[:]:  # copy to avoid changing the list while iterating
            if character.rect.colliderect(rect):
                # Character touched this lettuce, so remove it
                lettuce_list.remove(rect)
            else:
                # Draw the lettuce if it's still in the list
                screen.blit(lettuce_image, rect.topleft)

        character.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
