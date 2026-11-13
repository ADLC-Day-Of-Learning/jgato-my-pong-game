"""Ball module handling movement, physics, and collisions."""

from __future__ import annotations

import math

import pygame

from src.constants import (
    BALL_ACCELERATION_INCREMENT,
    BALL_INITIAL_SPEED_X,
    BALL_INITIAL_SPEED_Y,
    BALL_MAX_SPEED,
    BALL_SIZE,
    BALL_SPEED_INCREMENT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)
from src.paddle import Paddle


class Ball:
    """Represents the game ball with physics, bouncing, and collision detection."""

    def __init__(
        self,
        screen_width: int = SCREEN_WIDTH,
        screen_height: int = SCREEN_HEIGHT,
        size: int = BALL_SIZE,
        initial_speed_x: float = BALL_INITIAL_SPEED_X,
        initial_speed_y: float = BALL_INITIAL_SPEED_Y,
        speed_increment: float = BALL_SPEED_INCREMENT,
        max_speed: float = BALL_MAX_SPEED,
        acceleration_enabled: bool = False,
        acceleration_increment: float = BALL_ACCELERATION_INCREMENT,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.size = size
        self.initial_speed_x = float(initial_speed_x)
        self.initial_speed_y = float(initial_speed_y)
        self.speed_increment = float(speed_increment)
        self.max_speed = float(max_speed)
        self.acceleration_enabled = bool(acceleration_enabled)
        self.acceleration_increment = float(acceleration_increment)

        self.x = (self.screen_width - self.size) / 2.0
        self.y = (self.screen_height - self.size) / 2.0
        self.speed_x = self.initial_speed_x
        self.speed_y = self.initial_speed_y

    @property
    def current_speed(self) -> float:
        """Return the current scalar speed magnitude of the ball."""
        return math.hypot(self.speed_x, self.speed_y)

    @property
    def max_scalar_speed(self) -> float:
        """Return the maximum achievable scalar speed of the ball."""
        return math.hypot(self.max_speed, self.max_speed)

    @property
    def rect(self) -> pygame.Rect:
        """Returns the current pygame.Rect bounding box for the ball."""
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)

    def reset(self, direction: int | None = None) -> None:
        """Reset the ball to the center of the screen with initial velocity.

        Args:
            direction: 1 for moving right, -1 for moving left. If None,
                defaults to 1.
        """
        self.x = (self.screen_width - self.size) / 2.0
        self.y = (self.screen_height - self.size) / 2.0

        dir_x = 1 if direction is None else (1 if direction >= 0 else -1)
        self.speed_x = dir_x * self.initial_speed_x
        self.speed_y = self.initial_speed_y

    def update(self) -> None:
        """Advance the ball position according to its current velocity."""
        self.x += self.speed_x
        self.y += self.speed_y

    def check_wall_collision(self) -> bool:
        """Check and handle bouncing against the top and bottom screen edges.

        Returns:
            True if a wall collision occurred, False otherwise.
        """
        collided = False
        if self.y <= 0 and self.speed_y < 0:
            self.y = 0.0
            self.speed_y = abs(self.speed_y)
            collided = True
        elif self.y + self.size >= self.screen_height and self.speed_y > 0:
            self.y = float(self.screen_height - self.size)
            self.speed_y = -abs(self.speed_y)
            collided = True
        return collided

    def check_paddle_collision(self, paddle: Paddle) -> bool:
        """Check and handle collision with a player's paddle.

        Inverts horizontal velocity, accelerates ball speed up to max_speed,
        and modifies vertical angle depending on paddle contact point.

        Returns:
            True if a collision occurred, False otherwise.
        """
        if not self.rect.colliderect(paddle.rect):
            return False

        is_left = paddle.rect.centerx < self.screen_width / 2

        speed_before = self.current_speed

        if is_left:
            if self.speed_x >= 0 or self.x < paddle.x:
                return False
            # Moving left, colliding with front face of left paddle
            self.x = float(paddle.rect.right)
            new_speed_x = min(abs(self.speed_x) * self.speed_increment, self.max_speed)
            self.speed_x = new_speed_x
        else:
            if self.speed_x <= 0 or (self.x + self.size) > paddle.rect.right:
                return False
            # Moving right, colliding with front face of right paddle
            self.x = float(paddle.rect.left - self.size)
            new_speed_x = min(abs(self.speed_x) * self.speed_increment, self.max_speed)
            self.speed_x = -new_speed_x

        # Calculate deflection angle based on contact offset from paddle center
        paddle_center_y = paddle.y + (paddle.height / 2.0)
        ball_center_y = self.y + (self.size / 2.0)
        offset = (ball_center_y - paddle_center_y) / (paddle.height / 2.0)
        # Clamped offset between -1.0 and 1.0
        offset = max(-1.0, min(1.0, offset))

        self.speed_y = offset * abs(self.speed_x)
        if abs(self.speed_y) < 1.0:
            self.speed_y = 1.0 if self.speed_y >= 0 else -1.0
        if abs(self.speed_y) > self.max_speed:
            self.speed_y = self.max_speed if self.speed_y > 0 else -self.max_speed

        if self.acceleration_enabled:
            post_deflection_speed = self.current_speed
            target_speed = max(post_deflection_speed, speed_before) + self.acceleration_increment
            target_speed = min(target_speed, self.max_scalar_speed)
            if post_deflection_speed > 0:
                scale = target_speed / post_deflection_speed
                self.speed_x *= scale
                self.speed_y *= scale

        return True

    def check_out_of_bounds(self) -> int:
        """Determine whether the ball has crossed the left or right screen boundary.

        Returns:
            -1 if ball went past the left boundary (player 2 scores),
             1 if ball went past the right boundary (player 1 scores),
             0 if the ball is still in play.
        """
        if self.x + self.size < 0:
            return -1
        elif self.x > self.screen_width:
            return 1
        return 0

    def draw(self, surface: pygame.Surface) -> None:
        """Render the ball onto the target surface."""
        pygame.draw.rect(surface, WHITE, self.rect)
