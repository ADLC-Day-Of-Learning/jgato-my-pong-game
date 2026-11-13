"""Unit tests for the Ball class."""

import math

from src.ball import Ball
from src.constants import (
    BALL_ACCELERATION_INCREMENT,
    BALL_INITIAL_SPEED_X,
    BALL_INITIAL_SPEED_Y,
    BALL_MAX_SPEED,
)
from src.paddle import Paddle


def test_ball_initialization():
    ball = Ball(screen_width=800, screen_height=600, size=15)
    assert ball.screen_width == 800
    assert ball.screen_height == 600
    assert ball.size == 15
    assert ball.x == (800 - 15) / 2.0
    assert ball.y == (600 - 15) / 2.0
    assert ball.speed_x == BALL_INITIAL_SPEED_X
    assert ball.speed_y == BALL_INITIAL_SPEED_Y


def test_ball_movement():
    ball = Ball()
    start_x = ball.x
    start_y = ball.y
    ball.update()
    assert ball.x == start_x + ball.speed_x
    assert ball.y == start_y + ball.speed_y


def test_ball_wall_collision():
    ball = Ball(screen_height=600, size=15)

    # Top wall collision
    ball.y = -2.0
    ball.speed_y = -5.0
    assert ball.check_wall_collision() is True
    assert ball.y == 0.0
    assert ball.speed_y == 5.0  # Inverted

    # Bottom wall collision
    ball.y = 600.0
    ball.speed_y = 5.0
    assert ball.check_wall_collision() is True
    assert ball.y == 600.0 - 15.0
    assert ball.speed_y == -5.0  # Inverted

    # Middle of screen - no collision
    ball.y = 300.0
    ball.speed_y = 5.0
    assert ball.check_wall_collision() is False
    assert ball.speed_y == 5.0

    # At top boundary but moving downwards - no collision
    ball.y = 0.0
    ball.speed_y = 5.0
    assert ball.check_wall_collision() is False
    assert ball.speed_y == 5.0

    # At bottom boundary but moving upwards - no collision
    ball.y = 600.0 - 15.0
    ball.speed_y = -5.0
    assert ball.check_wall_collision() is False
    assert ball.speed_y == -5.0


def test_ball_paddle_collision_and_speedup():
    """Verify ball horizontal direction inverts on paddle contact.

    Verify ball speed increases by multiplier after paddle hit.
    """
    ball = Ball(
        screen_width=800,
        screen_height=600,
        size=15,
        initial_speed_x=5.0,
        speed_increment=1.1,
    )
    left_paddle = Paddle(x=30, y=250, width=15, height=100)

    # Position ball moving left, intersecting left paddle
    ball.x = 35
    ball.y = 280
    ball.speed_x = -5.0

    collided = ball.check_paddle_collision(left_paddle)
    assert collided is True
    # Verify horizontal direction inverted (now moving right)
    assert ball.speed_x > 0
    # Verify speed increased by multiplier
    expected_speed_x = 5.0 * 1.1
    assert abs(ball.speed_x - expected_speed_x) < 1e-5
    # Verify repositioned outside paddle
    assert ball.x == float(left_paddle.rect.right)

    # Now test right paddle collision
    right_paddle = Paddle(x=750, y=250, width=15, height=100)
    ball.x = 745
    ball.y = 280
    ball.speed_x = 6.0

    collided = ball.check_paddle_collision(right_paddle)
    assert collided is True
    # Verify horizontal direction inverted (now moving left)
    assert ball.speed_x < 0
    expected_speed_x_2 = 6.0 * 1.1
    assert abs(abs(ball.speed_x) - expected_speed_x_2) < 1e-5
    assert ball.x == float(right_paddle.rect.left - ball.size)

    # Ball already behind left paddle should not collide
    ball.x = 10
    ball.y = 280
    ball.speed_x = -5.0
    behind_paddle = Paddle(x=15, y=250, width=15, height=100)
    assert ball.check_paddle_collision(behind_paddle) is False

    # Ball already behind right paddle should not collide
    ball.x = 760
    ball.y = 280
    ball.speed_x = 5.0
    behind_right_paddle = Paddle(x=750, y=250, width=15, height=100)
    assert ball.check_paddle_collision(behind_right_paddle) is False


def test_ball_max_speed_cap():
    ball = Ball(
        initial_speed_x=14.0,
        speed_increment=1.5,
        max_speed=15.0,
    )
    paddle = Paddle(x=30, y=250, width=15, height=100)
    ball.x = 35
    ball.y = 280
    ball.speed_x = -14.0

    ball.check_paddle_collision(paddle)
    assert ball.speed_x == 15.0  # Capped at max_speed


def test_ball_out_of_bounds():
    ball = Ball(screen_width=800, size=15)

    # In play
    ball.x = 400
    assert ball.check_out_of_bounds() == 0

    # Past left boundary
    ball.x = -20
    assert ball.check_out_of_bounds() == -1

    # Past right boundary
    ball.x = 805
    assert ball.check_out_of_bounds() == 1


def test_ball_reset():
    ball = Ball(
        screen_width=800,
        screen_height=600,
        size=15,
        initial_speed_x=5.0,
        initial_speed_y=5.0,
    )
    ball.x = 10
    ball.y = 20
    ball.speed_x = 12.0
    ball.speed_y = 12.0

    ball.reset(direction=1)
    assert ball.x == (800 - 15) / 2.0
    assert ball.y == (600 - 15) / 2.0
    assert ball.speed_x == 5.0
    assert ball.speed_y == 5.0

    ball.reset(direction=-1)
    assert ball.speed_x == -5.0


def test_ball_current_speed_calculation_and_acceleration():
    """Verify that Ball provides current speed and updates on velocity change."""
    ball = Ball(
        initial_speed_x=BALL_INITIAL_SPEED_X,
        initial_speed_y=BALL_INITIAL_SPEED_Y,
    )
    expected_initial = math.hypot(BALL_INITIAL_SPEED_X, BALL_INITIAL_SPEED_Y)

    # Ball exposes scalar speed
    assert hasattr(ball, "current_speed")
    assert not hasattr(ball, "speed")
    assert math.isclose(ball.current_speed, expected_initial, rel_tol=1e-2)

    # Accelerate velocity and verify current_speed reflects the increase
    ball.speed_x *= ball.speed_increment
    assert ball.current_speed > expected_initial


def test_ball_current_speed_paddle_collision_and_reset():
    """Verify that paddle collision accelerates ball horizontal speed and reset restores it."""
    ball = Ball(
        screen_width=800,
        screen_height=600,
        size=15,
        initial_speed_x=5.0,
        initial_speed_y=5.0,
        speed_increment=1.2,
    )
    expected_initial = math.hypot(5.0, 5.0)
    assert math.isclose(ball.current_speed, expected_initial, rel_tol=1e-5)

    paddle = Paddle(x=30, y=250, width=15, height=100)
    # Position ball near edge of paddle so both speed_x and speed_y result in higher current_speed
    ball.x = 35
    ball.y = 340  # near the bottom of paddle (y=250..350)
    ball.speed_x = -5.0

    collided = ball.check_paddle_collision(paddle)
    assert collided is True
    assert abs(ball.speed_x) > 5.0
    assert ball.current_speed > expected_initial

    # Resetting the ball restores the initial scalar speed
    ball.reset()
    assert math.isclose(ball.current_speed, expected_initial, rel_tol=1e-5)


def test_ball_gradual_acceleration_defaults_disabled():
    """Verify that gradual acceleration is disabled by default on Ball."""
    ball = Ball()
    assert ball.acceleration_enabled is False
    assert ball.acceleration_increment == BALL_ACCELERATION_INCREMENT


def test_ball_paddle_collision_acceleration_enabled_both_paddles():
    """Verify both paddles increase total scalar speed when acceleration is enabled."""
    # Test Left Paddle with center contact (shallow deflection would otherwise lower speed)
    ball_left = Ball(acceleration_enabled=True)
    left_paddle = Paddle(x=30, y=250, width=15, height=100)
    # Position ball moving left, hitting center of left paddle
    ball_left.x = 35
    ball_left.y = 250 + (100 - ball_left.size) / 2.0
    ball_left.speed_x = -5.0
    ball_left.speed_y = 5.0
    speed_before_left = ball_left.current_speed

    assert ball_left.check_paddle_collision(left_paddle) is True
    assert ball_left.speed_x > 0
    assert ball_left.current_speed > speed_before_left
    assert ball_left.current_speed <= BALL_MAX_SPEED

    # Test Right Paddle with center contact
    ball_right = Ball(acceleration_enabled=True)
    right_paddle = Paddle(x=750, y=250, width=15, height=100)
    # Position ball moving right, hitting center of right paddle
    ball_right.x = 745
    ball_right.y = 250 + (100 - ball_right.size) / 2.0
    ball_right.speed_x = 5.0
    ball_right.speed_y = 5.0
    speed_before_right = ball_right.current_speed

    assert ball_right.check_paddle_collision(right_paddle) is True
    assert ball_right.speed_x < 0
    assert ball_right.current_speed > speed_before_right
    assert ball_right.current_speed <= BALL_MAX_SPEED


def test_ball_paddle_collision_acceleration_max_speed_cap():
    """Verify total scalar speed is capped at harmonized maximum speed when acceleration enabled."""
    ball = Ball(
        acceleration_enabled=True,
        initial_speed_x=15.0,
        initial_speed_y=15.0,
        max_speed=15.0,
    )
    paddle = Paddle(x=30, y=250, width=15, height=100)
    ball.x = 35
    # Position ball at paddle edge for maximum deflection (offset = 1.0)
    ball.y = paddle.y + paddle.height - (ball.size / 2.0)
    ball.speed_x = -15.0
    ball.speed_y = 15.0

    expected_max = ball.max_scalar_speed
    assert ball.check_paddle_collision(paddle) is True
    assert ball.current_speed <= expected_max
    assert math.isclose(ball.current_speed, expected_max, rel_tol=1e-5)


def test_ball_acceleration_disabled_preserves_existing_behavior():
    """Verify that disabled acceleration retains standard deflection without guaranteed speedup."""
    # With disabled mode and center paddle contact, vertical velocity drops to 1.0,
    # lowering total scalar speed below initial hypot(5, 5).
    ball = Ball(acceleration_enabled=False)
    paddle = Paddle(x=30, y=250, width=15, height=100)
    ball.x = 35
    ball.y = 250 + (100 - ball.size) / 2.0  # exact center hit -> offset = 0
    ball.speed_x = -5.0
    ball.speed_y = 5.0
    speed_before = ball.current_speed  # ~7.071

    assert ball.check_paddle_collision(paddle) is True
    # In disabled mode, horizontal speed = 5.0 * 1.05 = 5.25, vertical = 1.0 -> current ~5.34
    assert ball.current_speed < speed_before


def test_ball_reset_restores_speed_when_acceleration_enabled():
    """Verify scoring reset restores initial ball speed when acceleration is enabled."""
    ball = Ball(acceleration_enabled=True)
    initial_speed = ball.current_speed

    paddle = Paddle(x=30, y=250, width=15, height=100)
    ball.x = 35
    ball.y = 280
    ball.speed_x = -5.0
    ball.check_paddle_collision(paddle)
    assert ball.current_speed > initial_speed

    # Reset after scoring
    ball.reset(direction=1)
    assert math.isclose(ball.current_speed, initial_speed, rel_tol=1e-5)
    assert ball.acceleration_enabled is True


def test_ball_max_scalar_speed_property():
    """Verify Ball exposes max_scalar_speed calculated from max_speed."""
    ball = Ball(max_speed=15.0)
    expected = math.hypot(15.0, 15.0)
    assert math.isclose(ball.max_scalar_speed, expected, rel_tol=1e-5)


def test_ball_acceleration_strictly_faster_than_standard_across_offsets():
    """Verify acceleration mode produces higher speed than disabled mode across all offsets."""
    paddle = Paddle(x=30, y=250, width=15, height=100)
    for offset_ratio in [-1.0, -0.8, -0.5, -0.3, 0.0, 0.3, 0.5, 0.8, 1.0]:
        ball_disabled = Ball(acceleration_enabled=False, initial_speed_x=5.0, initial_speed_y=5.0)
        ball_disabled.x = 35
        ball_disabled.y = (
            paddle.y
            + (paddle.height / 2.0)
            + (offset_ratio * paddle.height / 2.0)
            - (ball_disabled.size / 2.0)
        )
        ball_disabled.speed_x = -5.0
        ball_disabled.speed_y = 5.0
        assert ball_disabled.check_paddle_collision(paddle) is True

        ball_enabled = Ball(acceleration_enabled=True, initial_speed_x=5.0, initial_speed_y=5.0)
        ball_enabled.x = 35
        ball_enabled.y = (
            paddle.y
            + (paddle.height / 2.0)
            + (offset_ratio * paddle.height / 2.0)
            - (ball_enabled.size / 2.0)
        )
        ball_enabled.speed_x = -5.0
        ball_enabled.speed_y = 5.0
        assert ball_enabled.check_paddle_collision(paddle) is True

        assert ball_enabled.current_speed > ball_disabled.current_speed


def test_ball_acceleration_strictly_faster_on_shallow_and_steep_returns():
    """Verify shallow (0.0) and steep (1.0) returns are strictly faster with acceleration."""
    paddle = Paddle(x=30, y=250, width=15, height=100)
    for offset_ratio in [0.0, 1.0]:
        ball_disabled = Ball(acceleration_enabled=False, initial_speed_x=6.0, initial_speed_y=4.0)
        ball_disabled.x = 35
        ball_disabled.y = (
            paddle.y
            + (paddle.height / 2.0)
            + (offset_ratio * paddle.height / 2.0)
            - (ball_disabled.size / 2.0)
        )
        ball_disabled.speed_x = -6.0
        ball_disabled.speed_y = 4.0
        assert ball_disabled.check_paddle_collision(paddle) is True

        ball_enabled = Ball(acceleration_enabled=True, initial_speed_x=6.0, initial_speed_y=4.0)
        ball_enabled.x = 35
        ball_enabled.y = (
            paddle.y
            + (paddle.height / 2.0)
            + (offset_ratio * paddle.height / 2.0)
            - (ball_enabled.size / 2.0)
        )
        ball_enabled.speed_x = -6.0
        ball_enabled.speed_y = 4.0
        assert ball_enabled.check_paddle_collision(paddle) is True

        assert ball_enabled.current_speed > ball_disabled.current_speed


def test_ball_acceleration_top_speed_ceiling_not_inverted():
    """Verify maximum speed ceiling in acceleration mode is >= disabled mode."""
    paddle = Paddle(x=30, y=250, width=15, height=100)
    ball_disabled = Ball(acceleration_enabled=False, initial_speed_x=15.0, initial_speed_y=15.0)
    ball_disabled.x = 35
    ball_disabled.y = paddle.y + paddle.height - ball_disabled.size
    ball_disabled.speed_x = -15.0
    ball_disabled.speed_y = 15.0
    ball_disabled.check_paddle_collision(paddle)

    ball_enabled = Ball(acceleration_enabled=True, initial_speed_x=15.0, initial_speed_y=15.0)
    ball_enabled.x = 35
    ball_enabled.y = paddle.y + paddle.height - ball_enabled.size
    ball_enabled.speed_x = -15.0
    ball_enabled.speed_y = 15.0
    ball_enabled.check_paddle_collision(paddle)

    assert ball_enabled.current_speed >= ball_disabled.current_speed
    assert abs(ball_enabled.speed_x) >= abs(ball_disabled.speed_x)
    assert abs(ball_enabled.speed_x) <= ball_enabled.max_speed


def test_ball_acceleration_no_paddle_tunneling_at_max_speed():
    """Verify ball does not tunnel through paddle when approaching at max speed."""
    left_paddle = Paddle(x=30, y=250, width=15, height=100)
    ball_left = Ball(acceleration_enabled=True, max_speed=15.0)
    ball_left.x = float(left_paddle.rect.right) + 1.0
    ball_left.y = left_paddle.y + (left_paddle.height - ball_left.size) / 2.0
    ball_left.speed_x = -ball_left.max_speed
    ball_left.speed_y = 0.0

    assert not ball_left.rect.colliderect(left_paddle.rect)

    ball_left.update()

    assert ball_left.check_paddle_collision(left_paddle) is True
    assert ball_left.speed_x > 0
    assert ball_left.x == float(left_paddle.rect.right)
    assert abs(ball_left.speed_x) <= ball_left.max_speed

    right_paddle = Paddle(x=755, y=250, width=15, height=100)
    ball_right = Ball(acceleration_enabled=True, max_speed=15.0)
    ball_right.x = float(right_paddle.rect.left - ball_right.size) - 1.0
    ball_right.y = right_paddle.y + (right_paddle.height - ball_right.size) / 2.0
    ball_right.speed_x = ball_right.max_speed
    ball_right.speed_y = 0.0

    assert not ball_right.rect.colliderect(right_paddle.rect)

    ball_right.update()

    assert ball_right.check_paddle_collision(right_paddle) is True
    assert ball_right.speed_x < 0
    assert ball_right.x == float(right_paddle.rect.left - ball_right.size)
    assert abs(ball_right.speed_x) <= ball_right.max_speed
