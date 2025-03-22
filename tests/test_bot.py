import pytest
from connect4.board import Board
from connect4.bot import Bot

class TestBot:
    """Test cases for the Connect 4 Bot class."""
    
    def test_init(self):
        """Test bot initialization with default and custom parameters."""
        # Test with default parameters
        default_bot = Bot()
        assert default_bot.player_number == Board.PLAYER_2
        assert default_bot.opponent_number == Board.PLAYER_1
        assert default_bot.search_depth == 6  # difficulty (4) + 2
        
        # Test with custom parameters
        custom_bot = Bot(player_number=Board.PLAYER_1, difficulty=2)
        assert custom_bot.player_number == Board.PLAYER_1
        assert custom_bot.opponent_number == Board.PLAYER_2
        assert custom_bot.search_depth == 4  # difficulty (2) + 2
    
    def test_initialize_window_positions(self):
        """Test that window positions are correctly pre-computed."""
        bot = Bot()
        
        # Check window counts match expected values
        assert len(bot.horizontal_windows) == 24  # 6 rows × 4 positions per row
        assert len(bot.vertical_windows) == 21    # 7 columns × 3 positions per column
        assert len(bot.diagonal_down_windows) == 12
        assert len(bot.diagonal_up_windows) == 12
        
        # Check a few specific window positions
        assert (0, 0) in bot.horizontal_windows  # Top-left horizontal window
        assert (5, 3) in bot.horizontal_windows  # Bottom-middle horizontal window
        assert (0, 0) in bot.vertical_windows    # Top-left vertical window
        assert (0, 0) in bot.diagonal_down_windows  # Top-left diagonal down window
        assert (3, 0) in bot.diagonal_up_windows    # Position for diagonal up window
    
    def test_get_window_values(self):
        """Test retrieving window values in different directions."""
        board = Board()
        bot = Bot()
        
        # Place some pieces to test
        board.drop_piece(0, Board.PLAYER_1)  # Column 0, bottom row
        board.drop_piece(1, Board.PLAYER_2)  # Column 1, bottom row
        board.drop_piece(2, Board.PLAYER_1)  # Column 2, bottom row
        board.drop_piece(3, Board.PLAYER_2)  # Column 3, bottom row
        
        # Test horizontal window
        horizontal_window = bot._get_window_values(board, 5, 0, 'horizontal')
        assert horizontal_window == [Board.PLAYER_1, Board.PLAYER_2, Board.PLAYER_1, Board.PLAYER_2]
        
        # Test vertical window
        vertical_window = bot._get_window_values(board, 2, 0, 'vertical')
        assert vertical_window == [Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.PLAYER_1]
        
        # Test diagonal windows (we need more pieces for interesting cases)
        board.drop_piece(0, Board.PLAYER_2)  # Column 0, second from bottom
        board.drop_piece(1, Board.PLAYER_1)  # Column 1, second from bottom
        board.drop_piece(2, Board.PLAYER_2)  # Column 2, second from bottom
        
        # Test diagonal-down window
        diagonal_down = bot._get_window_values(board, 2, 0, 'diagonal_down')
        expected_down = [
            board.grid[2][0],  # Starting position
            board.grid[3][1],
            board.grid[4][2],
            board.grid[5][3]   # Bottom row, column 3
        ]
        assert diagonal_down == expected_down
        
        # Test diagonal-up window
        diagonal_up = bot._get_window_values(board, 5, 0, 'diagonal_up')
        expected_up = [
            board.grid[5][0],  # Bottom-left
            board.grid[4][1], 
            board.grid[3][2],
            board.grid[2][3]
        ]
        assert diagonal_up == expected_up
    
    def test_get_board_hash(self):
        """Test that board hashing works correctly for the transposition table."""
        board = Board()
        bot = Bot()
        
        # Empty board hash
        empty_hash = bot._get_board_hash(board)
        assert isinstance(empty_hash, tuple)
        assert len(empty_hash) == board.rows
        assert all(isinstance(row, tuple) for row in empty_hash)
        
        # Make a move and check hash changes
        board.drop_piece(0, Board.PLAYER_1)
        modified_hash = bot._get_board_hash(board)
        assert empty_hash != modified_hash
        
        # Same position should hash to same value
        board_copy = board.copy()
        copy_hash = bot._get_board_hash(board_copy)
        assert copy_hash == modified_hash
    
    def test_evaluate_window(self):
        """Test the window evaluation function for different scenarios."""
        bot = Bot(player_number=Board.PLAYER_1)
        
        # 4 in a row for bot
        window_4_bot = [bot.player_number] * 4
        assert bot._evaluate_window(window_4_bot) == 100
        
        # 3 in a row for bot with an empty space
        window_3_bot = [bot.player_number] * 3 + [Board.EMPTY]
        assert bot._evaluate_window(window_3_bot) == 10
        
        # 2 in a row for bot with two empty spaces
        window_2_bot = [bot.player_number] * 2 + [Board.EMPTY] * 2
        assert bot._evaluate_window(window_2_bot) == 3
        
        # 3 in a row for opponent with an empty space
        window_3_opp = [bot.opponent_number] * 3 + [Board.EMPTY]
        assert bot._evaluate_window(window_3_opp) == -50
        
        # 2 in a row for opponent with two empty spaces
        window_2_opp = [bot.opponent_number] * 2 + [Board.EMPTY] * 2
        assert bot._evaluate_window(window_2_opp) == -5
        
        # Mixed window
        window_mixed = [bot.player_number, bot.opponent_number, Board.EMPTY, Board.EMPTY]
        assert bot._evaluate_window(window_mixed) == 0
    
    def test_immediate_win_detection(self):
        """Test that the bot detects and plays an immediate winning move."""
        board = Board()
        bot = Bot(player_number=Board.PLAYER_1)
        
        # Set up a position where player 1 can win horizontally
        board.drop_piece(0, Board.PLAYER_1)
        board.drop_piece(1, Board.PLAYER_1)
        board.drop_piece(2, Board.PLAYER_1)
        
        # Bot should choose column 3 to win
        move = bot.get_move(board)
        assert move == 3
        
        # Verify that's actually a winning move
        new_board = board.copy()
        new_board.drop_piece(move, bot.player_number)
        assert new_board.check_win(bot.player_number)
    
    def test_immediate_block_detection(self):
        """Test that the bot detects and blocks an opponent's winning move."""
        board = Board()
        bot = Bot(player_number=Board.PLAYER_2)
        
        # Set up a position where player 1 can win vertically
        board.drop_piece(3, Board.PLAYER_1)
        board.drop_piece(3, Board.PLAYER_1)
        board.drop_piece(3, Board.PLAYER_1)
        
        # Bot should choose column 3 to block
        move = bot.get_move(board)
        assert move == 3
        
        # Verify that prevents opponent from winning
        new_board = board.copy()
        new_board.drop_piece(move, bot.player_number)
        board.drop_piece(3, Board.PLAYER_1)  # Simulate if bot didn't block
        assert not new_board.check_win(bot.opponent_number)
        assert board.check_win(bot.opponent_number)  # Would have been a win
    
    def test_diagonal_win_detection(self):
        """Test that the bot detects and plays a diagonal winning move."""
        board = Board()
        bot = Bot(player_number=Board.PLAYER_1)

        # Set up a board where Player 1 can win with an up-right diagonal

        # (5,0): X
        board.drop_piece(0, Board.PLAYER_1)

        # (5,1): O | (4,1): X
        board.drop_piece(1, Board.PLAYER_2)
        board.drop_piece(1, Board.PLAYER_1)

        # (5,2): O | (4,2): O | (3,2): X
        board.drop_piece(2, Board.PLAYER_2)
        board.drop_piece(2, Board.PLAYER_2)
        board.drop_piece(2, Board.PLAYER_1)

        # (5,3): O | (4,3): O | (3,3): O
        board.drop_piece(3, Board.PLAYER_2)
        board.drop_piece(3, Board.PLAYER_2)
        board.drop_piece(3, Board.PLAYER_2)

        # Now (2,3) is empty and placing X there completes the diagonal

        move = bot.get_move(board)
        assert move == 3  # Column 3 should complete the diagonal win

        new_board = board.copy()
        new_board.drop_piece(move, bot.player_number)
        assert new_board.check_win(bot.player_number)


    def test_no_valid_moves(self):
        """Test that the bot returns -1 when the board is full."""
        board = Board()
        bot = Bot()

        # Fill up the entire board with alternating pieces
        for col in range(board.cols):
            for _ in range(board.rows):
                player = Board.PLAYER_1 if col % 2 == 0 else Board.PLAYER_2
                board.drop_piece(col, player)

        # Ensure the board is full
        assert board.is_full()
        
        move = bot.get_move(board)
        assert move == -1

    def test_transposition_table_usage(self):
        """Test that the transposition table is being used and updated."""
        board = Board()
        bot = Bot(difficulty=2)  # Use lower difficulty for faster test
        
        # Table should start empty with each move
        assert len(bot.transposition_table) == 0
        
        # Make some moves to create a non-trivial position
        board.drop_piece(3, Board.PLAYER_1)
        board.drop_piece(3, Board.PLAYER_2)
        board.drop_piece(4, Board.PLAYER_1)
        
        # Get move and check table was populated
        bot.get_move(board)
        assert len(bot.transposition_table) > 0
        
        # Check table entry format
        for key, value in bot.transposition_table.items():
            assert isinstance(key, tuple)
            assert isinstance(value, tuple)
            assert len(value) == 3  # (depth, score, value_type)
            
        # Save table size
        initial_size = len(bot.transposition_table)
        
        # Table should be cleared for next move
        bot.get_move(board)
        assert len(bot.transposition_table) > 0
        
        # Due to reuse of positions, the new table might have
        # a different size than the initial table
    
    def test_center_column_preference(self):
        """Test that the bot prefers the center column when scores are equal."""
        board = Board()
        bot = Bot()
        
        # For an empty board, the center column should be preferable
        move = bot.get_move(board)
        assert move == 3  # Center column (0-indexed)
    
    def test_move_ordering(self):
        """Test that moves are ordered based on heuristic evaluation."""
        board = Board()
        bot = Bot()
        
        # Create a test position where central columns should score higher
        board.drop_piece(0, Board.PLAYER_1)
        board.drop_piece(6, Board.PLAYER_2)
        
        # Add a spy to observe move ordering
        original_minimax = bot._minimax
        called_columns = []
        
        def spy_minimax(test_board, depth, alpha, beta, is_maximizing):
            # Get the last move made to determine the column
            for col in range(test_board.cols):
                if (board.grid[5][col] == Board.EMPTY and 
                    test_board.grid[5][col] != Board.EMPTY):
                    called_columns.append(col)
                    break
            return original_minimax(test_board, depth, alpha, beta, is_maximizing)
        
        # Replace the method with our spy
        bot._minimax = spy_minimax
        
        # Get the bot's move
        bot.get_move(board)
        
        # Assert central columns were evaluated first
        # This is approximated by checking if column 3 appears earlier than columns 0 or 6
        if 3 in called_columns and 0 in called_columns:
            assert called_columns.index(3) < called_columns.index(0)
        if 3 in called_columns and 6 in called_columns:
            assert called_columns.index(3) < called_columns.index(6)
        
        # Restore the original method
        bot._minimax = original_minimax
    
    def test_difficulty_levels(self):
        """Test that different difficulty levels affect search depth."""
        easy_bot = Bot(difficulty=1)
        medium_bot = Bot(difficulty=3)
        hard_bot = Bot(difficulty=5)
        
        assert easy_bot.search_depth < medium_bot.search_depth
        assert medium_bot.search_depth < hard_bot.search_depth
        
        # Confirm search depth formula
        assert easy_bot.search_depth == 1 + 2
        assert medium_bot.search_depth == 3 + 2
        assert hard_bot.search_depth == 5 + 2