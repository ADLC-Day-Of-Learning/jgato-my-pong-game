"""Main menu module for configuring player names and paddle colors."""

from __future__ import annotations

import pygame

from src.constants import (
    BLACK,
    BLUE,
    DARK_GRAY,
    FONT_SIZE_MESSAGE,
    FONT_SIZE_NAME,
    FONT_SIZE_SMALL,
    FONT_SIZE_TITLE,
    GRAY,
    GREEN,
    LIGHT_GRAY,
    PADDLE_WIDTH,
    RED,
    RGB_COLORS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)


class Menu:
    """Main menu interface for customizing player names and paddle colors."""

    def __init__(
        self,
        screen_width: int = SCREEN_WIDTH,
        screen_height: int = SCREEN_HEIGHT,
        player1_name: str = "",
        player2_name: str = "",
        player1_color: tuple[int, int, int] = RED,
        player2_color: tuple[int, int, int] = BLUE,
        acceleration_enabled: bool = False,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_color = player1_color
        self.player2_color = player2_color
        self.acceleration_enabled = bool(acceleration_enabled)

        # Active input field: None, "player1_name", "player2_name"
        self.active_field: str | None = None
        self.start_requested: bool = False

        # Fonts (lazily initialized)
        self.title_font: pygame.font.Font | None = None
        self.heading_font: pygame.font.Font | None = None
        self.font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

        # Interactive UI Rectangles
        col1_x = 100
        col2_x = 460
        box_width = 240
        box_height = 36

        # Text input boxes
        self.p1_input_rect = pygame.Rect(col1_x, 210, box_width, box_height)
        self.p2_input_rect = pygame.Rect(col2_x, 210, box_width, box_height)

        # Color buttons (Red, Green, Blue)
        btn_width = 70
        btn_height = 32
        btn_gap = 15

        self.p1_color_rects: dict[str, pygame.Rect] = {}
        self.p2_color_rects: dict[str, pygame.Rect] = {}

        for i, color_name in enumerate(["Red", "Green", "Blue"]):
            offset_x = i * (btn_width + btn_gap)
            self.p1_color_rects[color_name] = pygame.Rect(
                col1_x + offset_x, 290, btn_width, btn_height
            )
            self.p2_color_rects[color_name] = pygame.Rect(
                col2_x + offset_x, 290, btn_width, btn_height
            )

        # Acceleration toggle button (centered between previews above start button)
        toggle_w = 260
        toggle_h = 32
        self.acceleration_toggle_rect = pygame.Rect(
            (self.screen_width - toggle_w) // 2, 442, toggle_w, toggle_h
        )

        # Start game button (centered at bottom)
        start_btn_w = 220
        start_btn_h = 48
        self.start_button_rect = pygame.Rect(
            (self.screen_width - start_btn_w) // 2, 490, start_btn_w, start_btn_h
        )

    def reset(self) -> None:
        """Reset UI interaction states (active field and start flag)."""
        self.active_field = None
        self.start_requested = False

    def toggle_acceleration(self) -> None:
        """Toggle gradual ball acceleration on or off."""
        self.acceleration_enabled = not self.acceleration_enabled

    def get_player_name(self, player: int) -> str:
        """Return the trimmed player name or default if empty."""
        if player == 1:
            return self.player1_name.strip() or "Player 1"
        elif player == 2:
            return self.player2_name.strip() or "Player 2"
        raise ValueError(f"Invalid player index: {player}. Must be 1 or 2.")

    def set_player_name(self, player: int, name: str) -> None:
        """Set name for player 1 or player 2."""
        if player == 1:
            self.player1_name = name
        elif player == 2:
            self.player2_name = name
        else:
            raise ValueError(f"Invalid player index: {player}. Must be 1 or 2.")

    def get_paddle_color(self, player: int) -> tuple[int, int, int]:
        """Return selected paddle color for player 1 or 2."""
        if player == 1:
            return self.player1_color
        elif player == 2:
            return self.player2_color
        raise ValueError(f"Invalid player index: {player}. Must be 1 or 2.")

    def set_paddle_color(
        self, player: int, color: tuple[int, int, int] | str
    ) -> None:
        """Set paddle color for player 1 or 2."""
        parsed_color = self._parse_color(color)
        if player == 1:
            self.player1_color = parsed_color
        elif player == 2:
            self.player2_color = parsed_color
        else:
            raise ValueError(f"Invalid player index: {player}. Must be 1 or 2.")

    @staticmethod
    def _parse_color(color: tuple[int, int, int] | str) -> tuple[int, int, int]:
        """Normalize color tuple or string name into RGB tuple."""
        if isinstance(color, str):
            for name, rgb in RGB_COLORS.items():
                if name.lower() == color.lower():
                    return rgb
            if color.lower() == "white":
                return WHITE
            raise ValueError(
                f"Unknown color name: '{color}'. Available: {list(RGB_COLORS.keys())}"
            )
        return color

    def _ensure_fonts(self) -> None:
        """Lazily initialize menu fonts once pygame.font is ready."""
        if self.title_font is None and pygame.font.get_init():
            try:
                self.title_font = pygame.font.Font(None, FONT_SIZE_TITLE)
                self.heading_font = pygame.font.Font(None, FONT_SIZE_MESSAGE)
                self.font = pygame.font.Font(None, FONT_SIZE_NAME)
                self.small_font = pygame.font.Font(None, FONT_SIZE_SMALL)
            except (pygame.error, OSError, RuntimeError):
                self.title_font = None
                self.heading_font = None
                self.font = None
                self.small_font = None

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Process user events for menu interactions.

        Returns:
            True if the game should start, False otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Check text boxes
            if self.p1_input_rect.collidepoint(mouse_pos):
                self.active_field = "player1_name"
            elif self.p2_input_rect.collidepoint(mouse_pos):
                self.active_field = "player2_name"
            else:
                self.active_field = None

            # Check Player 1 color buttons
            for name, rect in self.p1_color_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.player1_color = RGB_COLORS[name]

            # Check Player 2 color buttons
            for name, rect in self.p2_color_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.player2_color = RGB_COLORS[name]

            # Check Acceleration toggle button
            if self.acceleration_toggle_rect.collidepoint(mouse_pos):
                self.toggle_acceleration()

            # Check Start Game button
            if self.start_button_rect.collidepoint(mouse_pos):
                self.start_requested = True
                return True

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) or (
                event.key == pygame.K_SPACE and self.active_field is None
            ):
                self.start_requested = True
                return True
            elif self.active_field is None and event.key == pygame.K_a:
                self.toggle_acceleration()
            elif event.key == pygame.K_TAB:
                # Cycle focus between player 1 and player 2 input boxes
                if self.active_field == "player1_name":
                    self.active_field = "player2_name"
                elif self.active_field == "player2_name":
                    self.active_field = "player1_name"
                else:
                    self.active_field = "player1_name"
            elif self.active_field == "player1_name":
                if event.key == pygame.K_BACKSPACE:
                    self.player1_name = self.player1_name[:-1]
                elif (
                    event.unicode
                    and event.unicode.isprintable()
                    and len(self.player1_name) < 15
                ):
                    self.player1_name += event.unicode
            elif self.active_field == "player2_name":
                if event.key == pygame.K_BACKSPACE:
                    self.player2_name = self.player2_name[:-1]
                elif (
                    event.unicode
                    and event.unicode.isprintable()
                    and len(self.player2_name) < 15
                ):
                    self.player2_name += event.unicode

        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Render the complete start menu interface onto the surface."""
        self._ensure_fonts()

        center_x = self.screen_width // 2

        # Title
        if self.title_font is not None:
            title_surf = self.title_font.render("PYGAME PONG", True, WHITE)
            surface.blit(title_surf, (center_x - title_surf.get_width() // 2, 40))

        # Subtitle
        if self.small_font is not None:
            sub_surf = self.small_font.render(
                "Customize Players & Paddle Colors", True, LIGHT_GRAY
            )
            surface.blit(sub_surf, (center_x - sub_surf.get_width() // 2, 95))

        # Render Player 1 Section
        self._draw_player_section(
            surface=surface,
            player_num=1,
            heading="PLAYER 1 (Left)",
            col_x=self.p1_input_rect.x,
            input_rect=self.p1_input_rect,
            name_text=self.player1_name,
            is_active=(self.active_field == "player1_name"),
            selected_color=self.player1_color,
            color_rects=self.p1_color_rects,
            preview_x=self.p1_input_rect.centerx - (PADDLE_WIDTH // 2),
            preview_y=350,
        )

        # Render Player 2 Section
        self._draw_player_section(
            surface=surface,
            player_num=2,
            heading="PLAYER 2 (Right)",
            col_x=self.p2_input_rect.x,
            input_rect=self.p2_input_rect,
            name_text=self.player2_name,
            is_active=(self.active_field == "player2_name"),
            selected_color=self.player2_color,
            color_rects=self.p2_color_rects,
            preview_x=self.p2_input_rect.centerx - (PADDLE_WIDTH // 2),
            preview_y=350,
        )

        # Acceleration Toggle Button
        toggle_color = DARK_GRAY
        border_color = GREEN if self.acceleration_enabled else GRAY
        pygame.draw.rect(
            surface, toggle_color, self.acceleration_toggle_rect, border_radius=4
        )
        pygame.draw.rect(
            surface, border_color, self.acceleration_toggle_rect, width=2, border_radius=4
        )

        if self.small_font is not None:
            status_text = "ON" if self.acceleration_enabled else "OFF"
            status_color = GREEN if self.acceleration_enabled else LIGHT_GRAY
            toggle_label = f"Gradual Acceleration: {status_text}"
            toggle_surf = self.small_font.render(toggle_label, True, status_color)
            surface.blit(
                toggle_surf,
                (
                    self.acceleration_toggle_rect.centerx - toggle_surf.get_width() // 2,
                    self.acceleration_toggle_rect.centery - toggle_surf.get_height() // 2,
                ),
            )

        # Start Game Button
        btn_color = DARK_GRAY
        pygame.draw.rect(surface, btn_color, self.start_button_rect, border_radius=6)
        pygame.draw.rect(
            surface, WHITE, self.start_button_rect, width=2, border_radius=6
        )

        if self.heading_font is not None:
            start_surf = self.heading_font.render("START GAME", True, WHITE)
            surface.blit(
                start_surf,
                (
                    self.start_button_rect.centerx - start_surf.get_width() // 2,
                    self.start_button_rect.centery - start_surf.get_height() // 2,
                ),
            )

        # Footer Hint
        if self.small_font is not None:
            hint_surf = self.small_font.render(
                "Click or TAB to edit names  •  Toggle Acceleration  •  Press ENTER to Play",
                True,
                GRAY,
            )
            surface.blit(hint_surf, (center_x - hint_surf.get_width() // 2, 555))

    def _draw_player_section(
        self,
        surface: pygame.Surface,
        player_num: int,
        heading: str,
        col_x: int,
        input_rect: pygame.Rect,
        name_text: str,
        is_active: bool,
        selected_color: tuple[int, int, int],
        color_rects: dict[str, pygame.Rect],
        preview_x: int,
        preview_y: int,
    ) -> None:
        """Render one player's customization column."""
        # Heading
        if self.heading_font is not None:
            head_surf = self.heading_font.render(heading, True, selected_color)
            surface.blit(head_surf, (col_x, 140))

        # Name label
        if self.small_font is not None:
            label_surf = self.small_font.render("Player Name:", True, LIGHT_GRAY)
            surface.blit(label_surf, (col_x, 185))

        # Text input box background & border
        pygame.draw.rect(surface, DARK_GRAY, input_rect, border_radius=4)
        border_color = WHITE if is_active else GRAY
        border_width = 2 if is_active else 1
        pygame.draw.rect(
            surface, border_color, input_rect, width=border_width, border_radius=4
        )

        # Text inside input box
        if self.font is not None:
            display_text = name_text
            if not display_text and not is_active:
                display_text = f"Player {player_num}"
                text_color = GRAY
            else:
                text_color = WHITE

            rendered_text = self.font.render(display_text, True, text_color)
            surface.blit(
                rendered_text,
                (
                    input_rect.x + 8,
                    input_rect.centery - rendered_text.get_height() // 2,
                ),
            )

            # Draw cursor if active
            if is_active:
                cursor_x = input_rect.x + 8 + rendered_text.get_width() + 2
                cursor_y1 = input_rect.y + 6
                cursor_y2 = input_rect.bottom - 6
                pygame.draw.line(
                    surface, WHITE, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2
                )

        # Color label
        if self.small_font is not None:
            color_label = self.small_font.render(
                "Paddle Color (RGB):", True, LIGHT_GRAY
            )
            surface.blit(color_label, (col_x, 265))

        # Color buttons
        for color_name, rect in color_rects.items():
            rgb_val = RGB_COLORS[color_name]
            pygame.draw.rect(surface, rgb_val, rect, border_radius=4)

            # Selected indicator: bright white outer outline
            if selected_color == rgb_val:
                pygame.draw.rect(surface, WHITE, rect, width=3, border_radius=4)
            else:
                pygame.draw.rect(surface, DARK_GRAY, rect, width=1, border_radius=4)

            # Color name text inside button
            if self.small_font is not None:
                text_color = BLACK if color_name == "Green" else WHITE
                c_text = self.small_font.render(color_name, True, text_color)
                surface.blit(
                    c_text,
                    (
                        rect.centerx - c_text.get_width() // 2,
                        rect.centery - c_text.get_height() // 2,
                    ),
                )

        # Paddle preview
        preview_height = 80
        preview_rect = pygame.Rect(
            preview_x, preview_y, PADDLE_WIDTH, preview_height
        )
        pygame.draw.rect(surface, selected_color, preview_rect)

        if self.small_font is not None:
            preview_label = self.small_font.render("Paddle Preview", True, GRAY)
            surface.blit(
                preview_label,
                (
                    preview_rect.centerx - preview_label.get_width() // 2,
                    preview_rect.bottom + 6,
                ),
            )
