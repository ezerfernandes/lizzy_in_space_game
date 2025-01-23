import os

import pygame

__all__ = ["SpriteSheet", "get_named_images", "get_named_sprites"]

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class SpriteSheet:
    def __init__(self, filename: str, project_root: str = PROJECT_ROOT) -> None:
        self.sheet = pygame.image.load(
            os.path.join(project_root, "assets", "images", filename),
        ).convert_alpha()

    def get_image(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> pygame.Surface:
        """Extract a single image from a larger spritesheet."""
        image = pygame.Surface(
            (width, height),
            pygame.SRCALPHA,
        ).convert_alpha()
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image


def get_named_images[T](
    spritesheet: SpriteSheet,
    item_width: int,
    item_height: int,
    item_names: list[T],
) -> dict[T, pygame.Surface]:
    sheet_width: int = spritesheet.sheet.get_width()
    #sheet_height: int = self.sheet.get_height()

    columns = sheet_width // item_width
    named_sprites: dict[T, pygame.Surface] = {}

    for index, name in enumerate(item_names):
        # Compute row/col based on index
        row = index // columns
        col = index % columns

        # Top-left coordinate of this sub-image
        x = col * item_width
        y = row * item_height

        sub_image = spritesheet.get_image(x, y, item_width, item_height)
        named_sprites[name] = sub_image

    return named_sprites


def get_named_sprites[T](
    spritesheet: SpriteSheet,
    item_width: int,
    item_height: int,
    item_names: list[T],
    frame_count: int,
    start_at: int = 0,
) -> dict[T, list[pygame.Surface]]:
    named_sprites: dict[T, list[pygame.Surface]] = {}

    for row_index, name in enumerate(item_names):
        frames = []
        for col in range(frame_count):
            x = col * item_width + start_at
            y = row_index * item_height
            sub_image = spritesheet.get_image(x, y, item_width, item_height)
            frames.append(sub_image)
        named_sprites[name] = frames

    return named_sprites
