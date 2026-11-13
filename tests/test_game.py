"""Unit tests for the PongGame loop and mechanics."""

from collections import defaultdict

import pygame

from src.constants import BLUE, GREEN, RED
from src.main import PongGame


def test_game_initialization_headless():
    game = PongGame(headless=True, sound_enabled=False)
    assert game.running is True
    assert game.paused is False
    assert game.state == "menu"
    assert game.menu is not None
    assert game.paddle1 is not None
    assert game.paddle2 is not None
    assert game.ball is not None
    assert game.score is not None


def test_game_step_and_pause():
    game = PongGame(headless=True, sound_enabled=False)
    game.start_game()

    # Initial step
    initial_ball_x = game.ball.x
    game.step()
    # Ball should have moved
    assert game.ball.x != initial_ball_x

    # Pause the game
    game.paused = True
    paused_ball_x = game.ball.x
    game.step()
    # Ball should not have moved while paused
    assert game.ball.x == paused_ball_x

    # Unpause
    game.paused = False
    game.step()
    assert game.ball.x != paused_ball_x


def test_game_scoring_updates():
    game = PongGame(headless=True, sound_enabled=False)
    game.start_game()

    # Move ball past right boundary -> Player 1 scores
    game.ball.x = game.screen_width + 10
    game.update()

    # Player 1 should have scored
    assert game.score.player1_score == 1
    # Ball should have reset to center
    assert game.ball.x == (game.screen_width - game.ball.size) / 2.0

    # Move ball past left boundary -> Player 2 scores
    game.ball.x = -20
    game.update()

    # Player 2 should have scored
    assert game.score.player2_score == 1
    # Ball should have reset to center with rightward direction
    assert game.ball.x == (game.screen_width - game.ball.size) / 2.0
    assert game.ball.speed_x > 0


def test_game_restart():
    game = PongGame(headless=True, sound_enabled=False)
    game.start_game()
    game.score.player1_score = 11
    game.paused = True
    game.restart()

    assert game.score.player1_score == 0
    assert game.score.player2_score == 0
    assert game.paused is False


def test_game_handle_input_quit_events():
    """Verify handle_input handles QUIT and ESCAPE events."""
    game = PongGame(headless=True, sound_enabled=False)

    # QUIT event
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    game.handle_input()
    assert game.running is False

    # ESCAPE key event
    game.running = True
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    game.handle_input()
    assert game.running is False


def test_game_handle_input_pause_and_restart():
    """Verify handle_input toggles pause and restarts game over."""
    game = PongGame(headless=True, sound_enabled=False)
    game.start_game()

    # Toggle pause with 'P'
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
    game.handle_input()
    assert game.paused is True

    # Toggle pause with SPACE
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.handle_input()
    assert game.paused is False

    # Restart game on SPACE when game over
    game.score.player1_score = 11
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.handle_input()
    assert game.score.player1_score == 0
    assert game.paused is False


def test_game_handle_input_paddle_movement(monkeypatch):
    """Verify handle_input moves paddles based on key state."""
    game = PongGame(headless=True, sound_enabled=False)
    game.start_game()

    initial_p1_y = game.paddle1.y
    initial_p2_y = game.paddle2.y

    # Move Player 1 up (W) and Player 2 down (DOWN)
    monkeypatch.setattr(
        pygame.key,
        "get_pressed",
        lambda: defaultdict(bool, {pygame.K_w: True, pygame.K_DOWN: True}),
    )
    game.handle_input()
    assert game.paddle1.y < initial_p1_y
    assert game.paddle2.y > initial_p2_y

    # Move Player 1 down (S) and Player 2 up (UP)
    p1_current_y = game.paddle1.y
    p2_current_y = game.paddle2.y
    monkeypatch.setattr(
        pygame.key,
        "get_pressed",
        lambda: defaultdict(bool, {pygame.K_s: True, pygame.K_UP: True}),
    )
    game.handle_input()
    assert game.paddle1.y > p1_current_y
    assert game.paddle2.y < p2_current_y


def test_game_step_stops_when_not_running():
    """Verify step immediately returns without updating or drawing if running is False."""
    game = PongGame(headless=True, sound_enabled=False)
    pygame.event.post(pygame.event.Event(pygame.QUIT))

    initial_ball_x = game.ball.x
    game.step()
    assert game.running is False
    # Ball should not have moved because step returned early
    assert game.ball.x == initial_ball_x


def test_start_menu_configuration_and_paddle_colors():
    """Verify start menu state transitions, name configuration, and RGB paddle colors."""
    game = PongGame(headless=True)
    assert game.state == "menu"

    # Configure custom names and RGB colors
    game.set_player_name(player=1, name="Alice")
    game.set_player_name(player=2, name="Bob")
    game.set_paddle_color(player=1, color=RED)
    game.set_paddle_color(player=2, color=BLUE)

    # Transition to playing state
    game.start_game()
    assert game.state == "playing"
    assert game.score.player1_name == "Alice"
    assert game.score.player2_name == "Bob"
    assert game.paddle1.color == RED
    assert game.paddle2.color == BLUE


def test_start_menu_string_color_configuration():
    """Verify setting paddle colors by string names."""
    game = PongGame(headless=True)
    game.set_paddle_color(player=1, color="Green")
    game.set_paddle_color(player=2, color="Red")
    game.start_game()
    assert game.paddle1.color == GREEN
    assert game.paddle2.color == RED


def test_start_menu_step_does_not_advance_ball():
    """Verify that in menu state, step() does not advance ball physics."""
    game = PongGame(headless=True, sound_enabled=False)
    assert game.state == "menu"
    initial_ball_x = game.ball.x
    game.step()
    assert game.ball.x == initial_ball_x
    assert game.state == "menu"


def test_start_menu_enter_starts_game():
    """Verify pressing ENTER in menu state transitions to playing state."""
    game = PongGame(headless=True, sound_enabled=False)
    assert game.state == "menu"
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    game.handle_input()
    assert game.state == "playing"


def test_return_to_menu_from_game_over():
    """Verify pressing 'M' when game is over returns to the main menu."""
    game = PongGame(headless=True, sound_enabled=False)
    game.start_game()
    game.score.player1_score = 11  # Game over
    assert game.score.is_game_over() is True

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
    game.handle_input()
    assert game.state == "menu"
    assert game.score.player1_score == 0


def test_return_to_menu_resets_menu_focus():
    """Verify returning to menu clears active_field and allows SPACE to start."""
    game = PongGame(headless=True, sound_enabled=False)
    # Focus active field before starting game
    game.menu.active_field = "player1_name"
    game.start_game()
    assert game.menu.active_field is None

    # Focus active field and trigger game over
    game.menu.active_field = "player2_name"
    game.score.player1_score = 11
    game.return_to_menu()
    assert game.state == "menu"
    assert game.menu.active_field is None
    assert game.menu.start_requested is False

    # SPACE key should start the game since active_field is None
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.handle_input()
    assert game.state == "playing"


def test_game_speedometer_rendering_and_state_resets():
    """Verify speedometer is rendered during playing state and resets on point and restart."""
    game = PongGame(headless=True, sound_enabled=False)
    initial_speed = game.ball.current_speed

    # In menu state, speedometer should not be rendered
    game.draw()
    has_menu_speed_pixels = any(
        game.screen.get_at((x, 30))[:3] != (0, 0, 0) for x in range(360, 440)
    )
    assert not has_menu_speed_pixels

    # In playing state, draw() renders speedometer
    game.start_game()
    game.draw()
    has_playing_speed_pixels = any(
        game.screen.get_at((x, 30))[:3] != (0, 0, 0)
        and game.screen.get_at((x, 30))[:3] != (128, 128, 128)
        for x in range(360, 440)
    )
    assert has_playing_speed_pixels

    # Accelerate ball and verify current_speed updates
    game.ball.speed_x *= 1.5
    assert game.ball.current_speed > initial_speed

    # Score point -> ball resets to initial speed
    game.ball.x = game.screen_width + 10
    game.update()
    assert abs(game.ball.current_speed - initial_speed) < 1e-5

    # Accelerate again and restart match -> ball resets to initial speed
    game.ball.speed_x *= 2.0
    assert game.ball.current_speed > initial_speed
    game.restart()
    assert abs(game.ball.current_speed - initial_speed) < 1e-5


def test_game_paddle1_collision():
    """Verify ball deflects off paddle1 in game update loop."""
    game = PongGame(headless=True, sound_enabled=False)
    game.start_game()

    # Position ball moving left and intersecting paddle1
    game.ball.x = game.paddle1.rect.right - 2
    game.ball.y = game.paddle1.y + 10
    game.ball.speed_x = -5.0

    game.update()

    # Ball horizontal velocity should be inverted and repositioned to paddle face
    assert game.ball.speed_x > 0
    assert game.ball.x >= float(game.paddle1.rect.right)


def test_game_paddle2_collision():
    """Verify ball deflects off paddle2 in game update loop."""
    game = PongGame(headless=True, sound_enabled=False)
    game.start_game()

    # Position ball moving right and intersecting paddle2
    game.ball.x = game.paddle2.x - game.ball.size + 2
    game.ball.y = game.paddle2.y + 10
    game.ball.speed_x = 5.0

    game.update()

    # Ball horizontal velocity should be inverted and repositioned to paddle face
    assert game.ball.speed_x < 0
    assert game.ball.x <= float(game.paddle2.rect.left - game.ball.size)


def test_game_start_game_propagates_acceleration_mode():
    """Verify start_game propagates acceleration toggle from menu to ball."""
    # Disabled by default
    game = PongGame(headless=True, sound_enabled=False)
    assert game.ball.acceleration_enabled is False
    game.start_game()
    assert game.ball.acceleration_enabled is False

    # Enabled
    game_enabled = PongGame(headless=True, sound_enabled=False)
    game_enabled.menu.acceleration_enabled = True
    game_enabled.start_game()
    assert game_enabled.ball.acceleration_enabled is True


def test_game_acceleration_scoring_resets_speed_and_preserves_mode():
    """Verify scoring resets ball speed while maintaining acceleration mode for next rally."""
    game = PongGame(headless=True, sound_enabled=False)
    game.menu.acceleration_enabled = True
    game.start_game()
    assert game.ball.acceleration_enabled is True
    initial_speed = game.ball.current_speed

    # Ball hits paddle1 in game loop
    game.ball.x = game.paddle1.rect.right - 2
    game.ball.y = game.paddle1.y + (game.paddle1.height - game.ball.size) / 2.0
    game.ball.speed_x = -5.0
    game.ball.speed_y = 5.0
    game.update()
    assert game.ball.current_speed > initial_speed

    # Player 1 scores point -> ball resets
    game.ball.x = game.screen_width + 10
    game.update()
    assert game.score.player1_score == 1
    assert abs(game.ball.current_speed - initial_speed) < 1e-5
    assert game.ball.acceleration_enabled is True

    # Next rally return accelerates ball again
    game.ball.x = game.paddle2.x - game.ball.size + 2
    game.ball.y = game.paddle2.y + (game.paddle2.height - game.ball.size) / 2.0
    game.ball.speed_x = 5.0
    game.ball.speed_y = 5.0
    speed_before = game.ball.current_speed
    game.update()
    assert game.ball.current_speed > speed_before
