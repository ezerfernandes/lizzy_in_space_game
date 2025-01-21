import pygame

__all__ = ["render_text"]

def render_text(
    text: str,
    pos: tuple[int, int],
    surface: pygame.Surface,
    font: pygame.font.Font,
    color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    label = font.render(text, True, color)
    surface.blit(label, pos)

