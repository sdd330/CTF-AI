"""
Player movement controller
Handles movement logic, direction updates, and position management
"""

from ..utils import Direction, TILE_SIZE


class PlayerMovementController:
    """Handles player movement logic"""

    EPSILON = 0.1  # Tolerance for position comparison

    def __init__(self, grid_x: int, grid_y: int, move_speed: float = 300.0):
        """
        Initialize movement controller

        Args:
            grid_x: Initial X coordinate (grid)
            grid_y: Initial Y coordinate (grid)
            move_speed: Movement speed (pixels/second)
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = grid_y * TILE_SIZE + TILE_SIZE // 2

        self.target_grid_x = grid_x
        self.target_grid_y = grid_y
        self.target_pixel_x = self.pixel_x
        self.target_pixel_y = self.pixel_y

        self.move_speed = move_speed
        self.current_direction = "down"

    def move_towards_target(self, delta_time: int) -> bool:
        """
        Move towards target position

        Args:
            delta_time: Time delta (milliseconds)

        Returns:
            True if still moving, False if at target
        """
        dx = self.target_pixel_x - self.pixel_x
        dy = self.target_pixel_y - self.pixel_y

        if abs(dx) < self.EPSILON and abs(dy) < self.EPSILON:
            self._snap_to_target()
            return False

        move_distance = (self.move_speed * delta_time) / 1000.0
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > 0:
            move_x = (dx / distance) * min(move_distance, abs(dx))
            move_y = (dy / distance) * min(move_distance, abs(dy))
            self.pixel_x += move_x
            self.pixel_y += move_y

        return True

    def _snap_to_target(self):
        """Snap to exact target position"""
        self.pixel_x = self.target_pixel_x
        self.pixel_y = self.target_pixel_y
        self.grid_x = self.target_grid_x
        self.grid_y = self.target_grid_y

    def update_direction(self):
        """Update movement direction based on target"""
        dx = self.target_pixel_x - self.pixel_x
        dy = self.target_pixel_y - self.pixel_y

        if abs(dx) > abs(dy):
            self.current_direction = "right" if dx > 0 else "left"
        elif abs(dy) > 0:
            self.current_direction = "down" if dy > 0 else "up"

    def set_direction(self, direction: Direction) -> bool:
        """
        Set movement direction

        Args:
            direction: Movement direction

        Returns:
            True if direction was set, False if no movement
        """
        dx, dy = direction.to_vector()
        if dx == 0 and dy == 0:
            return False

        self.target_grid_x = self.grid_x + dx
        self.target_grid_y = self.grid_y + dy
        self.target_pixel_x = self.target_grid_x * TILE_SIZE + TILE_SIZE // 2
        self.target_pixel_y = self.target_grid_y * TILE_SIZE + TILE_SIZE // 2
        return True

    def is_at_target(self) -> bool:
        """Check if at target position"""
        dx = abs(self.target_pixel_x - self.pixel_x)
        dy = abs(self.target_pixel_y - self.pixel_y)
        return dx < self.EPSILON and dy < self.EPSILON

    def is_moving(self) -> bool:
        """Check if currently moving"""
        grid_moving = (self.target_grid_x != self.grid_x or
                      self.target_grid_y != self.grid_y)
        pixel_moving = not self.is_at_target()
        return grid_moving or pixel_moving

    def teleport_to(self, grid_x: int, grid_y: int):
        """
        Instantly teleport to position

        Args:
            grid_x: Target X coordinate (grid)
            grid_y: Target Y coordinate (grid)
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = grid_y * TILE_SIZE + TILE_SIZE // 2
        self.target_grid_x = grid_x
        self.target_grid_y = grid_y
        self.target_pixel_x = self.pixel_x
        self.target_pixel_y = self.pixel_y

    def get_position(self) -> tuple[int, int]:
        """Get grid position"""
        return (self.grid_x, self.grid_y)

    def get_pixel_position(self) -> tuple[float, float]:
        """Get pixel position"""
        return (self.pixel_x, self.pixel_y)

    def get_rect_center(self) -> tuple[float, float]:
        """Get center position for rect update"""
        return (self.pixel_x, self.pixel_y)
