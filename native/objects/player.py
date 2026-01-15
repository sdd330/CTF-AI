"""
Player class - inherits from pygame.sprite.Sprite for collision detection
"""

import pygame
from ..utils import Team, Direction, PlayerState, PLAYER_SIZE, DEFAULT_PRISON_DURATION
from ..utils.assets import (
    get_character_frame_index, CHARACTERS_SPRITESHEET,
    CHARACTERS_RED_FLAG, CHARACTERS_YELLOW_FLAG, SPRITE_SIZE
)
from ..utils.status import PlayerStatus
from .player_movement import PlayerMovementController


class Player(pygame.sprite.Sprite):
    """Player class"""

    def __init__(self, name: str, team: Team, x: int, y: int):
        super().__init__()
        self.name = name
        self.team = team
        self._movement = PlayerMovementController(x, y)

        self.state = PlayerState.FREE
        self.has_flag = False
        self.in_prison = False
        self.prison_time_left = 0
        self.prison_duration = DEFAULT_PRISON_DURATION

        self.sprite_choice = 1 if team == Team.LEFT else 4
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 100

        self.rect = pygame.Rect(
            self._movement.pixel_x - PLAYER_SIZE // 2,
            self._movement.pixel_y - PLAYER_SIZE // 2,
            PLAYER_SIZE, PLAYER_SIZE
        )

    # Movement property proxies - required for external access and tests
    @property
    def grid_x(self): return self._movement.grid_x
    @grid_x.setter
    def grid_x(self, v): self._movement.grid_x = v
    @property
    def grid_y(self): return self._movement.grid_y
    @grid_y.setter
    def grid_y(self, v): self._movement.grid_y = v
    @property
    def pixel_x(self): return self._movement.pixel_x
    @pixel_x.setter
    def pixel_x(self, v): self._movement.pixel_x = v
    @property
    def pixel_y(self): return self._movement.pixel_y
    @pixel_y.setter
    def pixel_y(self, v): self._movement.pixel_y = v
    @property
    def target_grid_x(self): return self._movement.target_grid_x
    @target_grid_x.setter
    def target_grid_x(self, v): self._movement.target_grid_x = v
    @property
    def target_grid_y(self): return self._movement.target_grid_y
    @target_grid_y.setter
    def target_grid_y(self, v): self._movement.target_grid_y = v
    @property
    def target_pixel_x(self): return self._movement.target_pixel_x
    @target_pixel_x.setter
    def target_pixel_x(self, v): self._movement.target_pixel_x = v
    @property
    def target_pixel_y(self): return self._movement.target_pixel_y
    @target_pixel_y.setter
    def target_pixel_y(self, v): self._movement.target_pixel_y = v
    @property
    def current_direction(self): return self._movement.current_direction
    @property
    def move_speed(self): return self._movement.move_speed
    @move_speed.setter
    def move_speed(self, v): self._movement.move_speed = v

    def update(self, delta_time: int):
        """Update player state"""
        self._update_prison(delta_time)
        if not self.in_prison:
            self._update_movement(delta_time)
            self._update_animation(delta_time)

    def _update_prison(self, delta_time: int):
        if self.in_prison:
            self.prison_time_left = max(0, self.prison_time_left - delta_time)
            if self.prison_time_left <= 0:
                self.in_prison = False
                self.state = PlayerState.FREE
                self.prison_time_left = 0

    def _update_movement(self, delta_time: int):
        self._movement.move_towards_target(delta_time)
        self._movement.update_direction()
        self.rect.center = self._movement.get_rect_center()

    def _update_animation(self, delta_time: int):
        if self._movement.is_moving():
            self.animation_timer += delta_time
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 3
        else:
            self.animation_frame = 0
            self.animation_timer = 0

    def get_sprite_rect(self) -> tuple[int, int, int, int]:
        direction = "down" if self.in_prison else self.current_direction
        frame = 0 if self.in_prison else self.animation_frame
        x, y = get_character_frame_index(self.sprite_choice, direction, frame)
        return (x, y, SPRITE_SIZE, SPRITE_SIZE)

    def get_sprite_sheet_path(self) -> str:
        if self.has_flag:
            return str(CHARACTERS_YELLOW_FLAG if self.team == Team.LEFT else CHARACTERS_RED_FLAG)
        return str(CHARACTERS_SPRITESHEET)

    def set_direction(self, direction: Direction):
        if not self.in_prison:
            self._movement.set_direction(direction)

    def is_at_target(self) -> bool:
        return self._movement.is_at_target()

    def pick_up_flag(self):
        if not self.in_prison:
            self.has_flag = True
            self.state = PlayerState.CARRYING_FLAG

    def drop_flag(self):
        self.has_flag = False
        if self.state == PlayerState.CARRYING_FLAG:
            self.state = PlayerState.FREE

    def send_to_prison(self, prison_x: int, prison_y: int):
        self._movement.teleport_to(prison_x, prison_y)
        self.rect.center = self._movement.get_rect_center()
        self.in_prison = True
        self.state = PlayerState.IN_PRISON
        self.prison_time_left = self.prison_duration

    def get_position(self) -> tuple[int, int]:
        return self._movement.get_position()

    def get_pixel_position(self) -> tuple[float, float]:
        return self._movement.get_pixel_position()

    def get_status(self) -> PlayerStatus:
        return PlayerStatus(
            name=self.name, team=self.team.value,
            posX=self.grid_x, posY=self.grid_y,
            hasFlag=self.has_flag, inPrison=self.in_prison,
            inPrisonTimeLeft=self.prison_time_left,
            inPrisonDuration=self.prison_duration,
        )

    def __repr__(self) -> str:
        return (f"Player(name={self.name}, team={self.team.value}, "
                f"pos=({self.grid_x}, {self.grid_y}), state={self.state.value}, "
                f"has_flag={self.has_flag})")
