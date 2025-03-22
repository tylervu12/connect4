from typing import Optional, Tuple
from .board import Board

class Game:
    """Connect 4 game manager."""
    
    def __init__(self):
        """Initialize a new game with an empty board."""
        self.board = Board()
        self.current_player = Board.PLAYER_1
        self.game_over = False
        self.winner = None
    
    def make_move(self, col: int) -> Tuple[bool, Optional[str]]:
        """
        Attempt to make a move in the specified column.
        
        Args:
            col: Column index (0-based)
            
        Returns:
            Tuple of (success, message)
        """
        if self.game_over:
            return False, "Game is already over."
            
        success, _ = self.board.drop_piece(col, self.current_player)
        
        if not success:
            return False, "Invalid move."
            
        # Check for win
        if self.board.check_win(self.current_player):
            self.game_over = True
            self.winner = self.current_player
            return True, f"Player {self.current_player} wins!"
            
        # Check for draw
        if self.board.is_full():
            self.game_over = True
            return True, "Game ended in a draw."
            
        # Switch players
        self.current_player = Board.PLAYER_2 if self.current_player == Board.PLAYER_1 else Board.PLAYER_1
        
        return True, None
    
    def get_current_player(self) -> int:
        """Get the current player number."""
        return self.current_player
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.game_over
    
    def get_winner(self) -> Optional[int]:
        """Get the winner player number, or None if no winner."""
        return self.winner
    
    def get_valid_moves(self) -> list[int]:
        """Get a list of valid moves for the current state."""
        return self.board.get_valid_moves()
    
    def reset(self) -> None:
        """Reset the game to initial state."""
        self.board = Board()
        self.current_player = Board.PLAYER_1
        self.game_over = False
        self.winner = None
    
    def __str__(self) -> str:
        """String representation of the current game state."""
        result = str(self.board)
        if self.game_over:
            if self.winner:
                result += f"\nGame over! Player {self.winner} wins!"
            else:
                result += "\nGame over! It's a draw!"
        else:
            result += f"\nPlayer {self.current_player}'s turn"
        return result