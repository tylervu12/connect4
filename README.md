# Connect 4

A Python implementation of the classic Connect 4 game with an AI opponent using the minimax algorithm with alpha-beta pruning.

## Overview

This project implements Connect 4, a two-player board game where participants take turns dropping colored discs into a 6x7 vertical grid. The objective is to be the first to form a horizontal, vertical, or diagonal line of four discs.

The AI opponent is designed to challenge casual players, using sophisticated decision-making techniques:
- Minimax algorithm with alpha-beta pruning
- Transposition table for position caching
- Strategic position evaluation
- Configurable difficulty levels

## Requirements

- Python 3.9 or higher

## Getting Started

### For Players

Simply clone the repository and run the game:

```bash
git clone https://github.com/tylervu12/connect4.git
cd connect4
python main.py
```

### For Developers

If you want to modify the code or run tests:

```bash
git clone https://github.com/tylervu12/connect4.git
cd connect4
pip install -e .  # Install in development mode
pytest tests/     # Run the test suite
```

## How to Play

- When prompted, enter a column number (0-6) to drop your piece
- Enter 'q' at any time to quit the game
- After a game ends, enter 'y' to play again or 'n' to exit

You play as Player 1 (X) and the AI is Player 2 (O).

## Architecture

The project follows a modular design with clear separation of concerns:

```
connect4/                  # Root project directory
├── connect4/              # Python package directory
│   ├── __init__.py        # Package definition and exports
│   ├── board.py           # Board representation and core mechanics
│   ├── bot.py             # AI opponent implementation
│   ├── game.py            # Game state and rules management
│   └── ui.py              # Terminal user interface
├── tests/                 # Test directory
│   ├── test_board.py      # Tests for Board class
│   ├── test_game.py       # Tests for Game class
│   └── test_bot.py        # Tests for Bot class
├── main.py                # Entry point script
└── setup.py               # Package configuration
```

### Module Responsibilities

- **Board**: Handles the grid representation, piece placement mechanics, and win detection
- **Game**: Manages game state, turn-taking, and outcome determination
- **Bot**: Implements the AI logic and decision-making process
- **UI**: Provides the terminal interface and user interaction

## Design Decisions

### Data Structures

The board uses a simple 2D grid of integers for representation, with values:
- 0: Empty cell
- 1: Player 1's piece (human)
- 2: Player 2's piece (AI)

This straightforward approach balances clarity and performance, making the code maintainable while ensuring efficient operations.

### AI Strategy

The AI implementation combines several techniques to create a challenging opponent:

#### 1. Minimax with Alpha-Beta Pruning
The core algorithm allows the AI to explore possible future game states and select optimal moves, while pruning unproductive branches to improve efficiency.

```
function minimax(position, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or game_over in position:
        return static evaluation of position
        
    if maximizingPlayer:
        value = -∞
        for child in position:
            value = max(value, minimax(child, depth-1, alpha, beta, False))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = +∞
        for child in position:
            value = min(value, minimax(child, depth-1, alpha, beta, True))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value
```

#### 2. Transposition Table
To prevent redundant calculations, the algorithm caches evaluated positions in a transposition table. This significantly improves performance, especially in the mid-game.

#### 3. Position Evaluation
When the search reaches its depth limit, positions are evaluated using multiple heuristics:

- **Window Evaluation**: Examines all possible 4-cell windows for potential winning opportunities
- **Positional Weighting**: Assigns higher values to strategically advantageous positions (center column, lower rows)
- **Threat Detection**: Prioritizes blocking opponent's potential winning moves

#### 4. Move Ordering
Moves are pre-sorted by a quick evaluation before the full minimax search, enhancing alpha-beta pruning efficiency by examining promising moves first.

#### 5. Immediate Win/Block Detection
Before running the full search, the AI checks for immediate winning moves or critical blocks, allowing faster decisions in tactical situations.

### Difficulty Scaling

The difficulty level (1-5) directly affects the search depth, creating a balance between playing strength and response time:

- Lower depths (1-2): Quick decisions with limited foresight
- Medium depths (3-4): Balanced play suitable for casual players
- Higher depths (5+): Strong play with increased calculation time

## Testing Strategy

The testing strategy follows a component-based approach with distinct test suites for each module:

### Board Tests
- Initialization and dimensions
- Piece placement with gravity
- Win detection in all directions
- Valid move identification
- Full board detection

### Game Tests
- Game state management
- Player switching
- Win and draw detection
- Move validation

### Bot Tests
- Immediate win and block detection
- Position evaluation accuracy
- Transposition table functionality
- Minimax search behavior

Tests are implemented using pytest and designed to be deterministic and independent.

## Performance Optimizations

- **Cached Window Positions**: All possible winning windows are pre-computed for faster evaluation
- **Transposition Table Clearing**: The table is reset between moves to prevent memory growth
- **Strategic Move Ordering**: Preliminary evaluation sorts moves to maximize pruning efficiency
- **Early Termination**: Searches end immediately when wins or losses are detected

