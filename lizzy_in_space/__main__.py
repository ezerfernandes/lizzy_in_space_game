import os
import sys
from typing import Optional, TypedDict, Literal

import pygame

from pydantic import BaseModel, Field


pygame.init()


SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

Direction = Literal["front", "right", "back", "left"]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Adventure - Point & Click")

font = pygame.font.SysFont("arial", 18)


def render_text(
    text: str,
    pos: tuple[int, int],
    surface: pygame.Surface,
    color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    label = font.render(text, True, color)
    surface.blit(label, pos)


class SpriteSheet:
    def __init__(self, filename: str) -> None:
        self.sheet = pygame.image.load(
            os.path.join(PROJECT_ROOT, "assets", "images", filename),
        ).convert_alpha()

    def get_image(self, x: int, y: int, width: int, height: int) -> pygame.Surface:
        """Extract a single image from a larger spritesheet."""
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image


HEIGHT_START = {
    "front": 0,
    "right": 32,
    "back": 64,
    "left": 96,
}

class Character(BaseModel):
    sprite_sheet: SpriteSheet = Field(default=SpriteSheet("characters/test.png"))
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

    def __init__(self, **kwargs) -> None:
        if "pos" not in kwargs:
            kwargs["pos"] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        super().__init__(**kwargs)
        self.front_frames: list[pygame.Surface] = [
            self.sprite_sheet.get_image(
                0,
                HEIGHT_START["front"],
                16,
                32,
            ),
            self.sprite_sheet.get_image(
                16,
                HEIGHT_START["front"],
                16,
                32,
            ),
        ]
        self.back_frames: list[pygame.Surface] = [
            self.sprite_sheet.get_image(
                0,
                HEIGHT_START["back"],
                16,
                32,
            ),
            self.sprite_sheet.get_image(
                16,
                HEIGHT_START["back"],
                16,
                32,
            ),
        ]
        self.left_frames: list[pygame.Surface] = [
            self.sprite_sheet.get_image(
                0,
                HEIGHT_START["left"],
                16,
                32,
            ),
            self.sprite_sheet.get_image(
                16,
                HEIGHT_START["left"],
                16,
                32,
            ),
        ]
        self.right_frames: list[pygame.Surface] = [
            self.sprite_sheet.get_image(
                0,
                HEIGHT_START["right"],
                16,
                32,
            ),
            self.sprite_sheet.get_image(
                16,
                HEIGHT_START["right"],
                16,
                32,
            ),
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


class PuzzleState(BaseModel):
    """
    Manages puzzle states and inventory items.
    """
    collected_items: set[str] = Field(default_factory=set)
    puzzle_flags: dict[str, bool] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def collect_item(self, item_name: str) -> None:
        self.collected_items.add(item_name)

    def has_item(self, item_name: str) -> bool:
        return item_name in self.collected_items

    def set_flag(self, flag: str, value: bool = True) -> None:
        self.puzzle_flags[flag] = value

    def get_flag(self, flag: str) -> bool:
        return self.puzzle_flags.get(flag, False)


class Scene:
    def __init__(self, puzzle_state: PuzzleState):
        self.puzzle_state = puzzle_state
        # The name or instance of the next scene if a transition is required
        self.next_scene: Optional[str] = None

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle events such as MOUSEBUTTONDOWN, KEYDOWN, etc.
        Must be overridden by subclasses to implement unique scene logic.
        """
        pass

    def update(self, dt: float) -> None:
        """
        Update the scene state (animations, puzzle triggers, etc.)
        """
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the scene. Must be overridden.
        """
        pass


class IntroScene(Scene):
    def __init__(self, puzzle_state: PuzzleState) -> None:
        super().__init__(puzzle_state)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Transition to the corridor scene on click
            self.next_scene = "corridor"

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))  # Black background
        render_text(
            "SPACE ADVENTURE",
            (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 30),
            surface,
        )
        render_text(
            "Click anywhere to start...",
            (SCREEN_WIDTH//2 - 110, SCREEN_HEIGHT//2),
            surface,
        )



class ItemDict(TypedDict):
    name: str
    rect: pygame.Rect
    collected: bool

class CorridorScene(Scene):
    def __init__(self, puzzle_state: PuzzleState) -> None:
        super().__init__(puzzle_state)
        # Create some interactive areas
        self.items: list[ItemDict] = [
            {
                "name": "KeyCard",
                "rect": pygame.Rect(600, 400, 50, 50),
                "collected": False,
            },
        ]
        # Door to the control room
        self.control_door_rect = pygame.Rect(100, 200, 100, 200)
        self.door_locked = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Check if user clicks on the KeyCard
            for item in self.items:
                if item["rect"].collidepoint(mouse_pos) and not item["collected"]:
                    item["collected"] = True
                    self.puzzle_state.collect_item(item["name"])
                    print(f"Collected {item['name']}")

            # Check door interaction
            if self.control_door_rect.collidepoint(mouse_pos):
                # If the door is locked, check if we have the KeyCard
                if self.door_locked:
                    if self.puzzle_state.has_item("KeyCard"):
                        self.door_locked = False
                        print("Door unlocked using KeyCard!")
                    else:
                        print("The door is locked. You need a keycard.")
                else:
                    # Door is unlocked, transition to next scene
                    self.next_scene = "control_room"

    def update(self, dt):
        pass

    def draw(self, surface):
        # Draw background
        surface.fill((20, 20, 60))  # a dark, space-like color

        # Corridor environment (placeholder)
        render_text("Corridor Scene", (10, 10), surface)

        # Door (placeholder)
        pygame.draw.rect(surface, (100, 50, 50), self.control_door_rect)
        if self.door_locked:
            render_text("Locked Door", (self.control_door_rect.x, self.control_door_rect.y - 20), surface)

        # Draw KeyCard if it hasn't been collected
        for item in self.items:
            if not item["collected"]:
                pygame.draw.rect(surface, (200, 200, 0), item["rect"])
                render_text(item["name"], (item["rect"].x, item["rect"].y - 20), surface)


# --- Control Room Scene Example ---
class ControlRoomScene(Scene):
    def __init__(self, puzzle_state):
        super().__init__(puzzle_state)
        self.console_rect = pygame.Rect(300, 250, 200, 100)
        self.console_activated = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if self.console_rect.collidepoint(mouse_pos):
                # Activate the console
                self.console_activated = True
                print("Console activated! The spaceship's engines are now online.")
                self.puzzle_state.set_flag("engine_fixed", True)

    def update(self, dt):
        # If the console has been activated, maybe we can transition to another scene
        if self.console_activated:
            # This could lead to more scenes or a victory state. For now, let's do a simple message.
            pass

    def draw(self, surface):
        surface.fill((0, 0, 80))
        render_text("Control Room", (10, 10), surface)
        pygame.draw.rect(surface, (120, 120, 120), self.console_rect)
        render_text("Console", (self.console_rect.x + 50, self.console_rect.y - 20), surface)
        if self.console_activated:
            render_text("Engines Online!", (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2), surface)


# --- Scene Manager ---
class SceneManager:
    def __init__(self):
        self.puzzle_state = PuzzleState()
        self.scenes = {
            "intro": IntroScene(self.puzzle_state),
            "corridor": CorridorScene(self.puzzle_state),
            "control_room": ControlRoomScene(self.puzzle_state),
        }
        self.active_scene_key = "intro"

    def get_active_scene(self):
        return self.scenes[self.active_scene_key]

    def update(self, dt):
        scene = self.get_active_scene()
        scene.update(dt)

        # Check for scene transitions
        if scene.next_scene is not None:
            next_scene_key = scene.next_scene
            scene.next_scene = None
            self.active_scene_key = next_scene_key

    def draw(self, surface):
        scene = self.get_active_scene()
        scene.draw(surface)

    def handle_event(self, event):
        scene = self.get_active_scene()
        scene.handle_event(event)


# --- Main Game Loop ---
def main():
    clock = pygame.time.Clock()
    #manager = SceneManager()
    character = Character(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

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
        character.draw(screen)
        pygame.display.flip()


        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         running = False
        #     #manager.handle_event(event)

        # manager.update(dt)

        # manager.draw(screen)
        #pygame.display.flip()


    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
