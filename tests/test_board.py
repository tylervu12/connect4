import pytest
from connect4.board import Board

class TestBoard:
    """Test cases for the Connect 4 Board class."""
    
    def test_init(self):
        """Test board initialization with default and custom dimensions."""
        # Test default initialization
        board = Board()
        assert board.rows == 6
        assert board.cols == 7
        assert all(board.grid[r][c] == Board.EMPTY for r in range(board.rows) for c in range(board.cols))
        
        # Test custom dimensions
        custom_board = Board(rows=5, cols=6)
        assert custom_board.rows == 5
        assert custom_board.cols == 6
        assert all(custom_board.grid[r][c] == Board.EMPTY for r in range(custom_board.rows) for c in range(custom_board.cols))
    
    def test_drop_piece_valid(self):
        """Test dropping a piece in a valid column."""
        board = Board()
        success, row = board.drop_piece(3, Board.PLAYER_1)
        
        assert success is True
        assert row == 5  # Bottom row (0-indexed)
        assert board.grid[5][3] == Board.PLAYER_1
        
        # Drop another piece in the same column
        success, row = board.drop_piece(3, Board.PLAYER_2)
        assert success is True
        assert row == 4  # Second row from bottom
        assert board.grid[4][3] == Board.PLAYER_2
    
    def test_drop_piece_invalid_column(self):
        """Test dropping a piece in an invalid column."""
        board = Board()
        
        # Column too low
        success, row = board.drop_piece(-1, Board.PLAYER_1)
        assert success is False
        assert row is None
        
        # Column too high
        success, row = board.drop_piece(7, Board.PLAYER_1)
        assert success is False
        assert row is None
    
    def test_drop_piece_full_column(self):
        """Test dropping a piece in a full column."""
        board = Board()
        
        # Fill a column
        for i in range(board.rows):
            success, _ = board.drop_piece(0, Board.PLAYER_1)
            assert success is True
        
        # Try to drop in the full column
        success, row = board.drop_piece(0, Board.PLAYER_2)
        assert success is False
        assert row is None
    
    def test_is_valid_move(self):
        """Test valid move checking."""
        board = Board()
        
        # Valid moves in empty board
        for col in range(board.cols):
            assert board.is_valid_move(col) is True
        
        # Invalid column indices
        assert board.is_valid_move(-1) is False
        assert board.is_valid_move(board.cols) is False
        
        # Fill a column and test
        for i in range(board.rows):
            board.drop_piece(3, Board.PLAYER_1)
        assert board.is_valid_move(3) is False
    
    def test_get_valid_moves(self):
        """Test getting all valid moves."""
        board = Board()
        
        # All moves valid in empty board
        assert board.get_valid_moves() == list(range(board.cols))
        
        # Fill a column
        for i in range(board.rows):
            board.drop_piece(3, Board.PLAYER_1)
        
        # Column 3 should no longer be valid
        assert 3 not in board.get_valid_moves()
        assert len(board.get_valid_moves()) == board.cols - 1
    
    def test_check_win_horizontal(self):
        """Test horizontal win detection."""
        board = Board()
        
        # No win initially
        assert board.check_win(Board.PLAYER_1) is False
        
        # Create horizontal win for Player 1
        for col in range(4):
            board.drop_piece(col, Board.PLAYER_1)
        
        assert board.check_win(Board.PLAYER_1) is True
        assert board.check_win(Board.PLAYER_2) is False
    
    def test_check_win_vertical(self):
        """Test vertical win detection."""
        board = Board()
        
        # Create vertical win for Player 2
        for _ in range(4):
            board.drop_piece(0, Board.PLAYER_2)
        
        assert board.check_win(Board.PLAYER_2) is True
        assert board.check_win(Board.PLAYER_1) is False
    
    def test_check_win_diagonal_down(self):
        """Test diagonal (down-right) win detection."""
        board = Board()
        
        # Create a diagonal win (down-right)
        for i in range(4):
            # Fill lower positions first to allow piece placement
            for j in range(i):
                board.drop_piece(i, Board.PLAYER_2)
            # Add the winning piece
            board.drop_piece(i, Board.PLAYER_1)
        
        assert board.check_win(Board.PLAYER_1) is True
        assert board.check_win(Board.PLAYER_2) is False
    
    def test_check_win_diagonal_up(self):
        """Test diagonal (up-right) win detection."""
        board = Board()
        
        # Create a diagonal win (up-right)
        # First, create a "staircase" pattern
        for i in range(4):
            # Fill column 0 with 3 pieces
            if i == 0:
                for _ in range(3):
                    board.drop_piece(i, Board.PLAYER_2)
            # Fill columns 1-3 with decreasing pieces
            else:
                for _ in range(3 - i):
                    board.drop_piece(i, Board.PLAYER_2)
        
        # Now place the winning diagonal
        for i in range(4):
            board.drop_piece(i, Board.PLAYER_1)
        
        assert board.check_win(Board.PLAYER_1) is True
        assert board.check_win(Board.PLAYER_2) is False
    
    def test_is_full(self):
        """Test board full detection."""
        board = Board()
        
        # Board starts empty
        assert board.is_full() is False
        
        # Fill the board
        for col in range(board.cols):
            for _ in range(board.rows):
                board.drop_piece(col, Board.PLAYER_1)
        
        assert board.is_full() is True
    
    def test_copy(self):
        """Test board copying."""
        board = Board()
        
        # Make some moves
        board.drop_piece(0, Board.PLAYER_1)
        board.drop_piece(1, Board.PLAYER_2)
        
        # Create a copy
        board_copy = board.copy()
        
        # Verify the copy is independent but identical
        assert board_copy is not board
        assert board_copy.rows == board.rows
        assert board_copy.cols == board.cols
        for r in range(board.rows):
            for c in range(board.cols):
                assert board_copy.grid[r][c] == board.grid[r][c]
        
        # Modify the copy and verify original is unchanged
        board_copy.drop_piece(2, Board.PLAYER_1)
        assert board.grid[5][2] == Board.EMPTY
        assert board_copy.grid[5][2] == Board.PLAYER_1
    
    def test_string_representation(self):
        """Test string representation of the board."""
        board = Board(rows=2, cols=3)  # Smaller board for easier testing
        
        # Check empty board representation
        str_rep = str(board)
        assert "  0 1 2" in str_rep  # Column headers
        assert "| · · · |" in str_rep  # Empty cells
        
        # Add pieces and check representation
        board.drop_piece(0, Board.PLAYER_1)
        board.drop_piece(1, Board.PLAYER_2)
        
        str_rep = str(board)
        assert "X" in str_rep  # Player 1 piece
        assert "O" in str_rep  # Player 2 piece