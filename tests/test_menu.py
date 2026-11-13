"""Unit tests for the Start Menu interface and customization."""

import pygame
import pytest

from src.constants import BLUE, GREEN, RED, WHITE
from src.menu import Menu


def test_menu_initialization_defaults():
    menu = Menu(screen_width=800, screen_height=600)
    assert menu.screen_width == 800
    assert menu.screen_height == 600
    assert menu.player1_name == ""
    assert menu.player2_name == ""
    assert menu.get_player_name(1) == "Player 1"
    assert menu.get_player_name(2) == "Player 2"
    assert menu.player1_color == RED
    assert menu.player2_color == BLUE
    assert menu.active_field is None
    assert menu.start_requested is False


def test_menu_get_and_set_player_names():
    menu = Menu()
    menu.set_player_name(1, "Alice")
    menu.set_player_name(2, "Bob")
    assert menu.get_player_name(1) == "Alice"
    assert menu.get_player_name(2) == "Bob"

    # Whitespace and empty fallback
    menu.set_player_name(1, "   ")
    menu.set_player_name(2, "")
    assert menu.get_player_name(1) == "Player 1"
    assert menu.get_player_name(2) == "Player 2"

    with pytest.raises(ValueError):
        menu.set_player_name(3, "Invalid")
    with pytest.raises(ValueError):
        menu.get_player_name(0)


def test_menu_get_and_set_paddle_colors():
    menu = Menu()
    menu.set_paddle_color(1, GREEN)
    menu.set_paddle_color(2, RED)
    assert menu.get_paddle_color(1) == GREEN
    assert menu.get_paddle_color(2) == RED

    # String color parsing
    menu.set_paddle_color(1, "blue")
    menu.set_paddle_color(2, "Green")
    assert menu.get_paddle_color(1) == BLUE
    assert menu.get_paddle_color(2) == GREEN

    # White support
    menu.set_paddle_color(1, "white")
    assert menu.get_paddle_color(1) == WHITE

    with pytest.raises(ValueError):
        menu.set_paddle_color(1, "yellow")
    with pytest.raises(ValueError):
        menu.set_paddle_color(3, RED)
    with pytest.raises(ValueError):
        menu.get_paddle_color(4)


def test_menu_mouse_interaction_focus_and_buttons():
    menu = Menu()

    # Click Player 1 input box
    p1_pos = (menu.p1_input_rect.x + 5, menu.p1_input_rect.y + 5)
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=p1_pos))
    assert menu.active_field == "player1_name"

    # Click Player 2 input box
    p2_pos = (menu.p2_input_rect.x + 5, menu.p2_input_rect.y + 5)
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=p2_pos))
    assert menu.active_field == "player2_name"

    # Click outside to blur
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(10, 10)))
    assert menu.active_field is None

    # Click Player 1 Blue button
    p1_blue_rect = menu.p1_color_rects["Blue"]
    blue_pos = (p1_blue_rect.centerx, p1_blue_rect.centery)
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=blue_pos))
    assert menu.player1_color == BLUE

    # Click Player 2 Green button
    p2_green_rect = menu.p2_color_rects["Green"]
    green_pos = (p2_green_rect.centerx, p2_green_rect.centery)
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=green_pos))
    assert menu.player2_color == GREEN

    # Click Start Game button
    start_pos = (menu.start_button_rect.centerx, menu.start_button_rect.centery)
    started = menu.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=start_pos)
    )
    assert started is True
    assert menu.start_requested is True


def test_menu_keyboard_interaction_typing_and_navigation():
    menu = Menu(player1_name="", player2_name="")

    # TAB key cycles focus
    menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
    assert menu.active_field == "player1_name"

    # Type "Ada" into Player 1 name
    for ch in "Ada":
        menu.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=ord(ch), unicode=ch)
        )
    assert menu.player1_name == "Ada"

    # Backspace
    menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE))
    assert menu.player1_name == "Ad"

    # TAB to Player 2
    menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
    assert menu.active_field == "player2_name"

    # Type "Grace" into Player 2 name
    for ch in "Grace":
        menu.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=ord(ch), unicode=ch)
        )
    assert menu.player2_name == "Grace"

    # ENTER starts game
    started = menu.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    )
    assert started is True
    assert menu.start_requested is True


def test_menu_draw_rendering():
    surface = pygame.Surface((800, 600))
    menu = Menu(screen_width=800, screen_height=600)
    assert menu.title_font is None

    # Draw menu
    menu.draw(surface)
    assert menu.title_font is not None
    assert menu.heading_font is not None
    assert menu.font is not None
    assert menu.small_font is not None

    # Verify pixels drawn on surface (title text area and preview paddles)
    # Check start button area has non-black pixels
    has_start_pixels = any(
        surface.get_at((x, menu.start_button_rect.centery))[:3] != (0, 0, 0)
        for x in range(
            menu.start_button_rect.left, menu.start_button_rect.right
        )
    )
    assert has_start_pixels


def test_menu_default_keyboard_interaction_typing():
    """Verify typing into default Menu() does not append to 'Player 1'."""
    menu = Menu()
    assert menu.player1_name == ""
    assert menu.player2_name == ""

    # TAB key cycles focus to player1_name
    menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
    assert menu.active_field == "player1_name"

    # Type "Alice" into Player 1 name
    for ch in "Alice":
        menu.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=ord(ch), unicode=ch)
        )
    assert menu.player1_name == "Alice"
    assert menu.get_player_name(1) == "Alice"


def test_menu_reset():
    """Verify menu reset clears active input field and start flag."""
    menu = Menu()
    menu.active_field = "player1_name"
    menu.start_requested = True
    menu.reset()
    assert menu.active_field is None
    assert menu.start_requested is False


def test_menu_acceleration_toggle_defaults_off():
    """Verify gradual acceleration toggle is off by default."""
    menu = Menu()
    assert menu.acceleration_enabled is False


def test_menu_acceleration_toggle_mouse_click():
    """Verify clicking the acceleration toggle button flips its state."""
    menu = Menu()
    assert menu.acceleration_enabled is False

    click_pos = (
        menu.acceleration_toggle_rect.centerx,
        menu.acceleration_toggle_rect.centery,
    )
    # First click enables acceleration
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=click_pos))
    assert menu.acceleration_enabled is True

    # Second click disables acceleration
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=click_pos))
    assert menu.acceleration_enabled is False


def test_menu_acceleration_toggle_keyboard_shortcut():
    """Verify pressing 'A' toggles acceleration only when no text field is focused."""
    menu = Menu()
    assert menu.acceleration_enabled is False

    # Press 'A' with no active field -> toggles to True
    menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
    assert menu.acceleration_enabled is True

    # Press 'A' again -> toggles to False
    menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
    assert menu.acceleration_enabled is False

    # Focus player1_name field and press 'A' -> types 'A', does not toggle
    menu.active_field = "player1_name"
    menu.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, unicode="A")
    )
    assert menu.acceleration_enabled is False
    assert menu.player1_name == "A"


def test_menu_acceleration_toggle_rendering():
    """Verify acceleration toggle button renders with visual status text."""
    surface = pygame.Surface((800, 600))
    menu = Menu(acceleration_enabled=False)
    menu.draw(surface)

    # Check that toggle button area contains non-black pixels
    has_toggle_pixels = any(
        surface.get_at((x, menu.acceleration_toggle_rect.centery))[:3] != (0, 0, 0)
        for x in range(
            menu.acceleration_toggle_rect.left, menu.acceleration_toggle_rect.right
        )
    )
    assert has_toggle_pixels

    # Draw in enabled state
    menu.toggle_acceleration()
    menu.draw(surface)
    has_enabled_pixels = any(
        surface.get_at((x, menu.acceleration_toggle_rect.centery))[:3] != (0, 0, 0)
        for x in range(
            menu.acceleration_toggle_rect.left, menu.acceleration_toggle_rect.right
        )
    )
    assert has_enabled_pixels


def test_menu_reset_preserves_acceleration_choice():
    """Verify menu reset preserves user acceleration preference."""
    menu = Menu()
    menu.toggle_acceleration()
    assert menu.acceleration_enabled is True

    menu.reset()
    assert menu.acceleration_enabled is True
