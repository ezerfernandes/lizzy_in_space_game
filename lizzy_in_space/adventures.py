
# class PuzzleState(BaseModel):
#     """
#     Manages puzzle states and inventory items.
#     """
#     collected_items: set[str] = Field(default_factory=set)
#     puzzle_flags: dict[str, bool] = Field(default_factory=dict)

#     class Config:
#         arbitrary_types_allowed = True

#     def collect_item(self, item_name: str) -> None:
#         self.collected_items.add(item_name)

#     def has_item(self, item_name: str) -> bool:
#         return item_name in self.collected_items

#     def set_flag(self, flag: str, value: bool = True) -> None:
#         self.puzzle_flags[flag] = value

#     def get_flag(self, flag: str) -> bool:
#         return self.puzzle_flags.get(flag, False)

# # region Old adventure ideas

# class Scene:
#     def __init__(self, puzzle_state: PuzzleState):
#         self.puzzle_state = puzzle_state
#         # The name or instance of the next scene if a transition is required
#         self.next_scene: Optional[str] = None

#     def handle_event(self, event: pygame.event.Event) -> None:
#         """
#         Handle events such as MOUSEBUTTONDOWN, KEYDOWN, etc.
#         Must be overridden by subclasses to implement unique scene logic.
#         """

#     def update(self, dt: float) -> None:
#         """
#         Update the scene state (animations, puzzle triggers, etc.)
#         """

#     def draw(self, surface: pygame.Surface) -> None:
#         """
#         Draw the scene. Must be overridden.
#         """


# class IntroScene(Scene):
#     def __init__(self, puzzle_state: PuzzleState) -> None:
#         super().__init__(puzzle_state)

#     def handle_event(self, event: pygame.event.Event) -> None:
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             # Transition to the corridor scene on click
#             self.next_scene = "corridor"

#     def draw(self, surface: pygame.Surface) -> None:
#         surface.fill((0, 0, 0))  # Black background
#         render_text(
#             "SPACE ADVENTURE",
#             (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 30),
#             surface,
#         )
#         render_text(
#             "Click anywhere to start...",
#             (SCREEN_WIDTH//2 - 110, SCREEN_HEIGHT//2),
#             surface,
#         )


# class ItemDict(TypedDict):
#     name: str
#     rect: pygame.Rect
#     collected: bool


# class CorridorScene(Scene):
#     def __init__(self, puzzle_state: PuzzleState) -> None:
#         super().__init__(puzzle_state)
#         # Create some interactive areas
#         self.items: list[ItemDict] = [
#             {
#                 "name": "KeyCard",
#                 "rect": pygame.Rect(600, 400, 50, 50),
#                 "collected": False,
#             },
#         ]
#         # Door to the control room
#         self.control_door_rect = pygame.Rect(100, 200, 100, 200)
#         self.door_locked = True

#     def handle_event(self, event: pygame.event.Event) -> None:
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             mouse_pos = event.pos

#             # Check if user clicks on the KeyCard
#             for item in self.items:
#                 if item["rect"].collidepoint(mouse_pos) and not item["collected"]:
#                     item["collected"] = True
#                     self.puzzle_state.collect_item(item["name"])
#                     print(f"Collected {item['name']}")

#             # Check door interaction
#             if self.control_door_rect.collidepoint(mouse_pos):
#                 # If the door is locked, check if we have the KeyCard
#                 if self.door_locked:
#                     if self.puzzle_state.has_item("KeyCard"):
#                         self.door_locked = False
#                         print("Door unlocked using KeyCard!")
#                     else:
#                         print("The door is locked. You need a keycard.")
#                 else:
#                     # Door is unlocked, transition to next scene
#                     self.next_scene = "control_room"

#     def update(self, dt):
#         pass

#     def draw(self, surface):
#         # Draw background
#         surface.fill((20, 20, 60))  # a dark, space-like color

#         # Corridor environment (placeholder)
#         render_text("Corridor Scene", (10, 10), surface)

#         # Door (placeholder)
#         pygame.draw.rect(surface, (100, 50, 50), self.control_door_rect)
#         if self.door_locked:
#             render_text("Locked Door", (self.control_door_rect.x, self.control_door_rect.y - 20), surface)

#         # Draw KeyCard if it hasn't been collected
#         for item in self.items:
#             if not item["collected"]:
#                 pygame.draw.rect(surface, (200, 200, 0), item["rect"])
#                 render_text(item["name"], (item["rect"].x, item["rect"].y - 20), surface)


# class ControlRoomScene(Scene):
#     def __init__(self, puzzle_state):
#         super().__init__(puzzle_state)
#         self.console_rect = pygame.Rect(300, 250, 200, 100)
#         self.console_activated = False

#     def handle_event(self, event):
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             mouse_pos = event.pos
#             if self.console_rect.collidepoint(mouse_pos):
#                 # Activate the console
#                 self.console_activated = True
#                 print("Console activated! The spaceship's engines are now online.")
#                 self.puzzle_state.set_flag("engine_fixed", True)

#     def update(self, dt):
#         # If the console has been activated, maybe we can transition to another scene
#         if self.console_activated:
#             # This could lead to more scenes or a victory state. For now, let's do a simple message.
#             pass

#     def draw(self, surface):
#         surface.fill((0, 0, 80))
#         render_text("Control Room", (10, 10), surface)
#         pygame.draw.rect(surface, (120, 120, 120), self.console_rect)
#         render_text("Console", (self.console_rect.x + 50, self.console_rect.y - 20), surface)
#         if self.console_activated:
#             render_text("Engines Online!", (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2), surface)


# # --- Scene Manager ---
# class SceneManager:
#     def __init__(self):
#         self.puzzle_state = PuzzleState()
#         self.scenes = {
#             "intro": IntroScene(self.puzzle_state),
#             "corridor": CorridorScene(self.puzzle_state),
#             "control_room": ControlRoomScene(self.puzzle_state),
#         }
#         self.active_scene_key = "intro"

#     def get_active_scene(self):
#         return self.scenes[self.active_scene_key]

#     def update(self, dt):
#         scene = self.get_active_scene()
#         scene.update(dt)

#         # Check for scene transitions
#         if scene.next_scene is not None:
#             next_scene_key = scene.next_scene
#             scene.next_scene = None
#             self.active_scene_key = next_scene_key

#     def draw(self, surface):
#         scene = self.get_active_scene()
#         scene.draw(surface)

#     def handle_event(self, event):
#         scene = self.get_active_scene()
#         scene.handle_event(event)

# # endregion

