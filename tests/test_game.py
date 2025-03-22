import pytest
from connect4.game import Game
from connect4.board import Board

class TestGame:
    """Test cases for the Connect 4 Game class."""
    
    def test_init(self):
        """Test game initialization."""
        game = Game()
        
        # Check initial state
        assert game.current_player == Board.PLAYER_1
        assert game.game_over is False
        assert game.winner is None
        assert isinstance(game.board, Board)
    
    def test_make_move_valid(self):
        """Test making a valid move."""
        game = Game()
        
        # Make a valid move
        success, message = game.make_move(3)
        
        assert success is True
        assert message is None
        # Player should switch after a move
        assert game.current_player == Board.PLAYER_2
        # Check that piece is on the board
        assert game.board.grid[5][3] == Board.PLAYER_1
    
    def test_make_move_invalid(self):
        """Test making an invalid move."""
        game = Game()
        
        # Make an invalid move (out of bounds)
        success, message = game.make_move(-1)
        
        assert success is False
        assert "Invalid move" in message
        # Player should not switch after invalid move
        assert game.current_player == Board.PLAYER_1
    
    def test_make_move_game_over(self):
        """Test making a move when the game is already over."""
        game = Game()
        
        # Manually set game as over
        game.game_over = True
        
        success, message = game.make_move(3)
        
        assert success is False
        assert "Game is already over" in message
    
    def test_horizontal_win(self):
        """Test detecting a horizontal win."""
        game = Game()
        
        # Player 1 makes moves to create a horizontal win
        for col in range(4):
            # Player 1's turn
            success, message = game.make_move(col)
            assert success is True
            
            if col < 3:  # Not the winning move yet
                # Player 2's turn - place in a non-interfering column
                success, message = game.make_move(col + 4)
                assert success is True
        
        # After the fourth move by Player 1, the game should be over
        assert game.game_over is True
        assert game.winner == Board.PLAYER_1
        assert "Player 1 wins" in message
    
    def test_vertical_win(self):
        """Test detecting a vertical win."""
        game = Game()
        
        # Alternating moves in columns 0 and 1
        # Player 1 will stack 4 in column 0
        for _ in range(4):
            # Player 1's turn - always column 0
            success, message = game.make_move(0)
            assert success is True
            
            if not game.game_over:
                # Player 2's turn - always column 1
                success, message = game.make_move(1)
                assert success is True
        
        assert game.game_over is True
        assert game.winner == Board.PLAYER_1
        assert "Player 1 wins" in message
    
    def test_diagonal_win(self):
        """Test detecting a diagonal win.
        
        Creates a board with the following pattern:
        . . . . . . .
        . . . . . . .
        . . . X . . .  <-- Winning diagonal
        . . X O . . .  <-- Winning diagonal
        . X O O . . .  <-- Winning diagonal
        X O O O . . .  <-- Winning diagonal
        """
        game = Game()
        
        # Column 0: Player 1 (bottom piece of the diagonal)
        game.make_move(0)  # Player 1
        
        # Column 1: First Player 2, then Player 1
        game.make_move(1)  # Player 2
        game.make_move(1)  # Player 1
        
        # Column 2: Two Player 2, then Player 1
        game.make_move(2)  # Player 2
        game.make_move(5)  # Player 1 (non-interfering)
        game.make_move(2)  # Player 2
        game.make_move(2)  # Player 1
        
        # Column 3: Three Player 2, then Player 1 (winning move)
        game.make_move(3)  # Player 2
        game.make_move(6)  # Player 1 (non-interfering)
        game.make_move(3)  # Player 2
        game.make_move(6)  # Player 1 (non-interfering)
        game.make_move(3)  # Player 2
        
        # Winning move
        success, message = game.make_move(3)  # Player 1
        assert success is True
        
        assert game.game_over is True
        assert game.winner == Board.PLAYER_1
        assert "wins" in message.lower()
    
    def test_draw_detection(self):
        """Test detecting a draw."""
        game = Game()
        
        # Create a pattern that will lead to a draw
        # We'll use a more careful approach to avoid accidental wins
        
        # Alternate players in a way that fills the board without anyone winning
        # This approach actually plays through moves instead of setting the grid directly
        columns_sequence = [0, 1, 0, 1, 2, 3, 2, 3, 4, 5, 4, 5, 6, 0, 6, 1, 2, 3, 4, 5, 6]
        
        # Manually modify the board state to be almost full but without wins
        # We'll mock the board's is_full method to return True for our test
        original_is_full = game.board.is_full
        
        # After some moves, pretend the board is full
        def mock_is_full():
            return True
            
        # Make some moves first
        for col in columns_sequence[:5]:  # Just make a few moves
            success, _ = game.make_move(col)
            assert success is True
        
        # Now override the is_full method
        game.board.is_full = mock_is_full
        
        # Make one more move which should trigger the draw detection
        success, message = game.make_move(0)
        
        assert success is True
        assert "draw" in message.lower()
        assert game.game_over is True
        assert game.winner is None
        
        # Restore the original method
        game.board.is_full = original_is_full
    
    def test_get_current_player(self):
        """Test getting the current player."""
        game = Game()
        
        assert game.get_current_player() == Board.PLAYER_1
        
        # Make a move to switch players
        game.make_move(0)
        assert game.get_current_player() == Board.PLAYER_2
    
    def test_is_game_over(self):
        """Test checking if the game is over."""
        game = Game()
        
        assert game.is_game_over() is False
        
        # Manually set game as over
        game.game_over = True
        assert game.is_game_over() is True
    
    def test_get_winner(self):
        """Test getting the winner."""
        game = Game()
        
        assert game.get_winner() is None
        
        # Set a winner
        game.winner = Board.PLAYER_2
        assert game.get_winner() == Board.PLAYER_2
    
    def test_get_valid_moves(self):
        """Test getting valid moves."""
        game = Game()
        
        # Initially all columns should be valid
        assert len(game.get_valid_moves()) == game.board.cols
        assert set(game.get_valid_moves()) == set(range(game.board.cols))
        
        # Fill a column directly using the board
        for row in range(game.board.rows):
            # Set each cell in column 0 to be filled
            game.board.grid[row][0] = Board.PLAYER_1
        
        # Column 0 should no longer be valid
        valid_moves = game.get_valid_moves()
        assert 0 not in valid_moves
    
    def test_reset(self):
        """Test resetting the game."""
        game = Game()
        
        # Make some moves
        game.make_move(0)
        game.make_move(1)
        
        # Reset the game
        game.reset()
        
        # Check that everything is back to initial state
        assert game.current_player == Board.PLAYER_1
        assert game.game_over is False
        assert game.winner is None
        assert all(game.board.grid[r][c] == Board.EMPTY 
                  for r in range(game.board.rows) 
                  for c in range(game.board.cols))
    
    def test_string_representation(self):
        """Test string representation of the game."""
        game = Game()
        
        # Check initial representation
        str_rep = str(game)
        assert "Player 1's turn" in str_rep
        
        # Make a move and check representation again
        game.make_move(0)
        str_rep = str(game)
        assert "Player 2's turn" in str_rep
        
        # End the game and check representation
        game.game_over = True
        game.winner = Board.PLAYER_1
        str_rep = str(game)
        assert "Game over" in str_rep
        assert "Player 1 wins" in str_rep
        
        # Check draw representation
        game.winner = None
        str_rep = str(game)
        assert "Game over" in str_rep
        assert "draw" in str_rep.lower()