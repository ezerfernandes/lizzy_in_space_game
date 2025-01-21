import os

import pygame


class SpriteSheet:
    def __init__(self, filename: str, project_root: str) -> None:
        self.sheet = pygame.image.load(
            os.path.join(project_root, "assets", "images", filename),
        ).convert_alpha()

    def get_image(self, x: int, y: int, width: int, height: int) -> pygame.Surface:
        """Extract a single image from a larger spritesheet."""
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image

    def get_named_images(
        self,
        item_width: int,
        item_height: int,
        item_names: list[str],
    ) -> dict[str, pygame.Surface]:
        sheet_width: int = self.sheet.get_width()
        #sheet_height: int = self.sheet.get_height()

        columns = sheet_width // item_width
        named_sprites: dict[str, pygame.Surface] = {}

        for index, name in enumerate(item_names):
            # Compute row/col based on index
            row = index // columns
            col = index % columns

            # Top-left coordinate of this sub-image
            x = col * item_width
            y = row * item_height

            sub_image = self.get_image(x, y, item_width, item_height)
            named_sprites[name] = sub_image

        return named_sprites
