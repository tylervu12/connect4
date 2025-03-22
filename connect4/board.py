from typing import List, Optional, Tuple

class Board:
    """Connect 4 board representation."""
    
    EMPTY = 0
    PLAYER_1 = 1
    PLAYER_2 = 2
    
    def __init__(self, rows: int = 6, cols: int = 7):
        """Initialize an empty board with specified dimensions."""
        self.rows = rows
        self.cols = cols
        self.grid = [[self.EMPTY for _ in range(cols)] for _ in range(rows)]
        
    def drop_piece(self, col: int, player: int) -> Tuple[bool, Optional[int]]:
        """
        Attempt to drop a piece in the specified column.
        
        Args:
            col: Column index (0-based)
            player: Player identifier (1 or 2)
            
        Returns:
            Tuple of (success, row) where row is the row where piece landed
        """
        if not 0 <= col < self.cols:
            return False, None
            
        # Find the lowest empty spot in the column
        for row in range(self.rows - 1, -1, -1):
            if self.grid[row][col] == self.EMPTY:
                self.grid[row][col] = player
                return True, row
                
        # Column is full
        return False, None
    
    def is_valid_move(self, col: int) -> bool:
        """Check if a move is valid (column exists and isn't full)."""
        return 0 <= col < self.cols and self.grid[0][col] == self.EMPTY
        
    def get_valid_moves(self) -> List[int]:
        """Return a list of valid column indices for moves."""
        return [col for col in range(self.cols) if self.is_valid_move(col)]
    
    def check_win(self, player: int) -> bool:
        """Check if the specified player has a winning position."""
        # Check horizontal
        for row in range(self.rows):
            for col in range(self.cols - 3):
                if all(self.grid[row][col + i] == player for i in range(4)):
                    return True
                    
        # Check vertical
        for row in range(self.rows - 3):
            for col in range(self.cols):
                if all(self.grid[row + i][col] == player for i in range(4)):
                    return True
                    
        # Check diagonal (down-right)
        for row in range(self.rows - 3):
            for col in range(self.cols - 3):
                if all(self.grid[row + i][col + i] == player for i in range(4)):
                    return True
                    
        # Check diagonal (up-right)
        for row in range(3, self.rows):
            for col in range(self.cols - 3):
                if all(self.grid[row - i][col + i] == player for i in range(4)):
                    return True
                    
        return False
    
    def is_full(self) -> bool:
        """Check if the board is completely full."""
        return all(self.grid[0][col] != self.EMPTY for col in range(self.cols))
    
    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        new_board = Board(self.rows, self.cols)
        new_board.grid = [row[:] for row in self.grid]
        return new_board
    
    def __str__(self) -> str:
        """String representation of the board for display."""
        result = ""
        # Column numbers
        result += "  " + " ".join(str(i) for i in range(self.cols)) + "\n"
        # Board
        for row in self.grid:
            result += "| " + " ".join(self._cell_to_str(cell) for cell in row) + " |\n"
        # Bottom
        result += "+" + "-" * (self.cols * 2 + 1) + "+\n"
        return result
    
    def _cell_to_str(self, cell: int) -> str:
        """Convert cell value to display character."""
        if cell == self.EMPTY:
            return "·"
        elif cell == self.PLAYER_1:
            return "X"
        elif cell == self.PLAYER_2:
            return "O"
        return "?"