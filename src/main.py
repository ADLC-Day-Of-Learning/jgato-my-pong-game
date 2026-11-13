"""Main game entry point and game loop for Pygame Pong."""

from __future__ import annotations

import os
import sys

# Ensure project root is on sys.path when executed directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pygame  # noqa: E402

from src.ball import Ball  # noqa: E402
from src.constants import (  # noqa: E402
    BLACK,
    FPS,
    PADDLE_HEIGHT,
    PADDLE_MARGIN,
    PADDLE_SPEED,
    PADDLE_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WINDOW_TITLE,
)
from src.menu import Menu  # noqa: E402
from src.paddle import Paddle  # noqa: E402
from src.score import Score  # noqa: E402
from src.sound import SoundManager  # noqa: E402


class PongGame:
    """Encapsulates the Pong game state, event handling, physics, and rendering."""

    def __init__(
        self,
        screen_width: int = SCREEN_WIDTH,
        screen_height: int = SCREEN_HEIGHT,
        sound_enabled: bool = True,
        headless: bool = False,
        state: str = "menu",
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.headless = headless
        self.running = True
        self.paused = False
        self.state = state

        if not pygame.get_init():
            pygame.init()

        if not headless:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
            pygame.display.set_caption(WINDOW_TITLE)
        else:
            self.screen = pygame.Surface((self.screen_width, self.screen_height))

        self.clock = pygame.time.Clock()
        self.sound = SoundManager(enabled=sound_enabled)

        # Initialize main menu
        self.menu = Menu(
            screen_width=self.screen_width,
            screen_height=self.screen_height,
        )

        # Initialize paddles (vertically centered)
        p1_x = PADDLE_MARGIN
        p1_y = (self.screen_height - PADDLE_HEIGHT) / 2.0
        self.paddle1 = Paddle(
            p1_x,
            p1_y,
            screen_height=self.screen_height,
            color=self.menu.player1_color,
        )

        p2_x = self.screen_width - PADDLE_MARGIN - PADDLE_WIDTH
        p2_y = (self.screen_height - PADDLE_HEIGHT) / 2.0
        self.paddle2 = Paddle(
            p2_x,
            p2_y,
            screen_height=self.screen_height,
            speed=PADDLE_SPEED * 0.6,
            color=self.menu.player2_color,
        )

        # Initialize ball and scoreboard
        self.ball = Ball(
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            acceleration_enabled=self.menu.acceleration_enabled,
        )
        self.score = Score(
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            player1_name=self.menu.get_player_name(1),
            player2_name=self.menu.get_player_name(2),
        )

    def set_player_name(self, player: int, name: str) -> None:
        """Set custom player name for player 1 or 2."""
        self.menu.set_player_name(player, name)
        clean_name = self.menu.get_player_name(player)
        self.score.set_player_name(player, clean_name)

    def set_paddle_color(
        self, player: int, color: tuple[int, int, int] | str
    ) -> None:
        """Set custom paddle color for player 1 or 2."""
        self.menu.set_paddle_color(player, color)
        selected_color = self.menu.get_paddle_color(player)
        if player == 1:
            self.paddle1.color = selected_color
        elif player == 2:
            self.paddle2.color = selected_color
        else:
            raise ValueError(f"Invalid player index: {player}. Must be 1 or 2.")

    def start_game(self) -> None:
        """Apply player customizations and transition state from menu to playing."""
        self.score.set_player_name(1, self.menu.get_player_name(1))
        self.score.set_player_name(2, self.menu.get_player_name(2))
        self.paddle1.color = self.menu.get_paddle_color(1)
        self.paddle2.color = self.menu.get_paddle_color(2)
        self.ball.acceleration_enabled = self.menu.acceleration_enabled
        self.menu.reset()
        self.state = "playing"

    def return_to_menu(self) -> None:
        """Reset the match and return to the main menu."""
        self.restart()
        self.menu.reset()
        self.state = "menu"

    def handle_input(self) -> None:
        """Process keyboard events, mouse events, and continuous user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                self.running = False
                return

            if self.state == "menu":
                if self.menu.handle_event(event):
                    self.start_game()
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_p, pygame.K_SPACE):
                        if self.score.is_game_over():
                            self.restart()
                        else:
                            self.paused = not self.paused
                    elif event.key == pygame.K_m and self.score.is_game_over():
                        self.return_to_menu()

        # Handle paddle movement when in playing state and not paused or game over
        if (
            self.state == "playing"
            and not self.paused
            and not self.score.is_game_over()
        ):
            keys = pygame.key.get_pressed()
            # Player 1 controls (W/S)
            if keys[pygame.K_w]:
                self.paddle1.move_up()
            if keys[pygame.K_s]:
                self.paddle1.move_down()

            # Player 2 controls (Up/Down)
            if keys[pygame.K_UP]:
                self.paddle2.move_up()
            if keys[pygame.K_DOWN]:
                self.paddle2.move_down()

    def update(self) -> None:
        """Advance game physics, handle collisions, and manage scoring."""
        if self.state != "playing" or self.paused or self.score.is_game_over():
            return

        self.ball.update()

        # Wall collisions (top and bottom)
        if self.ball.check_wall_collision():
            self.sound.play_bounce()

        # Paddle collisions
        if (
            self.ball.check_paddle_collision(self.paddle1)
            or self.ball.check_paddle_collision(self.paddle2)
        ):
            self.sound.play_wall()

        # Scoring / out-of-bounds check
        out = self.ball.check_out_of_bounds()
        if out == 1:
            # Player 1 scores point
            self.score.player1_point()
            self.sound.play_score()
            self.ball.reset(direction=-1)
        elif out == -1:
            # Player 2 scores point
            self.score.player2_point()
            self.sound.play_score()
            self.ball.reset(direction=1)

    def draw(self) -> None:
        """Render all game components and UI to the screen."""
        self.screen.fill(BLACK)
        if self.state == "menu":
            self.menu.draw(self.screen)
        else:
            self.score.draw(self.screen, ball_speed=self.ball.current_speed)
            self.paddle1.draw(self.screen)
            self.paddle2.draw(self.screen)
            self.ball.draw(self.screen)

            if self.paused:
                self.score.draw_pause(self.screen)

        if not self.headless:
            pygame.display.flip()

    def restart(self) -> None:
        """Reset the game state to play again."""
        self.score.reset()
        self.ball.reset()
        self.paddle1.reset()
        self.paddle2.reset()
        self.paused = False

    def step(self) -> None:
        """Execute a single game frame."""
        self.handle_input()
        if not self.running:
            return
        self.update()
        self.draw()

    def run(self) -> None:
        """Run the main game loop until quit is requested."""
        while self.running:
            self.step()
            self.clock.tick(FPS)


def main() -> None:
    """Launch the Pong game."""
    game = PongGame()
    try:
        game.run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
