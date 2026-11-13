# Pygame Pong

A classic 2D Pong game implementation built in Python using the [Pygame](https://www.pygame.org/) library.

## Overview

Pong is one of the earliest arcade video games. In this game, two players control paddles on opposite sides of the screen to hit a ball back and forth. A player scores a point whenever the opponent fails to return the ball. The objective is to reach the target score before the opposing player.

## Features

- **Start Menu & Customization**: Interactive start menu to customize player names and choose paddle colors (RGB: Red, Green, Blue) with real-time paddle previews.
- **Classic Gameplay**: Authentic paddle movement, ball bouncing physics, and score tracking.
- **Controls**: Smooth two-player keyboard controls (W/S and Up/Down arrows).
- **Dynamic Ball Speed**: Ball speed increases with successive paddle hits for added challenge.
- **Audio & Visuals**: Retro sound effects and visual boundary indicators.

## Prerequisites

- **Python 3.8+** (authoritative requirements and tooling configuration are defined in `pyproject.toml`)
- **Pygame 2.0+**

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ADLC-Day-Of-Learning/test.git
   cd test
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Alternatively, install via `pyproject.toml`:
   ```bash
   pip install .
   ```

## How to Play

### Running the Game

Once dependencies are installed, start the game:

```bash
python src/main.py
```

### Running Tests

To execute the test suite:

```bash
pytest
```

### Running Linters

To run code quality and Python version compatibility checks with Ruff:

```bash
ruff check .
```

### Controls

#### Main Menu
- **Edit Names:** Click on text box or press `TAB` to switch fields, type custom name (defaults to "Player 1" / "Player 2" if left blank)
- **Select Paddle Color:** Click on `Red`, `Green`, or `Blue` buttons for either player
- **Toggle Gradual Acceleration:** Click the `Gradual Acceleration` button or press `A` (when no text field is focused) to turn gradual ball acceleration on or off
- **Start Game:** Click `START GAME` or press `ENTER` / `SPACE`

#### In-Game
| Player | Move Up | Move Down |
| :--- | :--- | :--- |
| **Player 1 (Left)** | `W` | `S` |
| **Player 2 (Right)** | `Up Arrow` (`↑`) | `Down Arrow` (`↓`) |

- **Pause Game:** `P` or `Space`
- **Return to Menu:** `M` (when game is over)
- **Quit Game:** `ESC` or close window

## Project Structure

```text
.
├── README.md        # Project documentation
├── pyproject.toml   # Project metadata, dependencies, and tooling configuration (Ruff, Pytest)
├── requirements.txt # Project dependencies
├── src/
│   ├── __init__.py  # Package initialization
│   ├── main.py      # Game entry point and main game loop
│   ├── menu.py      # Start menu and player customization UI
│   ├── ball.py      # Ball movement and collision logic
│   ├── paddle.py    # Paddle movement and player input
│   ├── score.py     # Scoreboard and UI rendering
│   ├── sound.py     # Audio manager and sound effects
│   └── constants.py # Game constants (screen dimensions, speeds, colors)
├── tests/           # Unit and integration test suite
│   ├── conftest.py  # Pytest configuration and fixtures
│   ├── test_ball.py # Ball physics and collision tests
│   ├── test_game.py # Game loop and input handling tests
│   ├── test_menu.py # Start menu UI and customization tests
│   ├── test_paddle.py # Paddle movement and bounds tests
│   ├── test_score.py  # Score tracking and UI rendering tests
│   └── test_sound.py  # Sound manager fallback tests
└── assets/
    └── sounds/      # Sound effects for ball bounce and scoring
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
