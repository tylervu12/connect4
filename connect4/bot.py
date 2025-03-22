import random
from typing import Optional, Tuple, Dict, Hashable, List
from .board import Board

class Bot:
    """Connect 4 bot player using minimax with alpha-beta pruning and transposition table."""
    
    def __init__(self, player_number: int = Board.PLAYER_2, difficulty: int = 4):
        """
        Initialize the bot.
        
        Args:
            player_number: The player number for the bot (default is 2)
            difficulty: How many moves to look ahead (default is 4)
        """
        self.player_number = player_number
        self.opponent_number = Board.PLAYER_1 if player_number == Board.PLAYER_2 else Board.PLAYER_2
        self.search_depth = difficulty + 2  # Adjusted depth
        
        # Transposition table to cache evaluated positions
        self.transposition_table: Dict[Hashable, tuple] = {}
        
        # Position weights - prioritizing center and lower rows
        self.position_weights = [
            [3, 4, 5, 7, 5, 4, 3],
            [4, 6, 8, 10, 8, 6, 4],
            [5, 7, 9, 11, 9, 7, 5],
            [5, 7, 9, 11, 9, 7, 5],
            [6, 8, 10, 12, 10, 8, 6],
            [7, 9, 12, 15, 12, 9, 7]  
        ]
        
        # Initialize cached window positions
        self.horizontal_windows = []
        self.vertical_windows = []
        self.diagonal_down_windows = []
        self.diagonal_up_windows = []
        self._initialize_window_positions()
    
    def _initialize_window_positions(self):
        """
        Pre-compute all possible window positions for efficient evaluation.
        This removes the need to repeatedly calculate windows during evaluation.
        """
        # Standard Connect 4 board dimensions
        rows, cols = 6, 7
        
        # Horizontal windows (24 total)
        for row in range(rows):
            for col in range(cols - 3):
                self.horizontal_windows.append((row, col))
        
        # Vertical windows (21 total)
        for row in range(rows - 3):
            for col in range(cols):
                self.vertical_windows.append((row, col))
        
        # Diagonal down-right windows (12 total)
        for row in range(rows - 3):
            for col in range(cols - 3):
                self.diagonal_down_windows.append((row, col))
        
        # Diagonal up-right windows (12 total)
        for row in range(3, rows):
            for col in range(cols - 3):
                self.diagonal_up_windows.append((row, col))
    
    def _get_window_values(self, board: Board, row: int, col: int, direction: str) -> List[int]:
        """
        Get the values for a specific window.
        
        Args:
            board: Current game board
            row: Starting row index
            col: Starting column index
            direction: Direction of the window ('horizontal', 'vertical', 'diagonal_down', 'diagonal_up')
            
        Returns:
            List of 4 values in the window
        """
        window = []
        if direction == 'horizontal':
            window = [board.grid[row][col + i] for i in range(4)]
        elif direction == 'vertical':
            window = [board.grid[row + i][col] for i in range(4)]
        elif direction == 'diagonal_down':
            window = [board.grid[row + i][col + i] for i in range(4)]
        elif direction == 'diagonal_up':
            window = [board.grid[row - i][col + i] for i in range(4)]
        
        return window
    
    def _get_board_hash(self, board: Board) -> tuple:
        """
        Generate a hashable representation of the board.
        
        Args:
            board: Current game board
            
        Returns:
            A hashable representation (tuple of tuples)
        """
        return tuple(tuple(row) for row in board.grid)
    
    def get_move(self, board: Board) -> int:
        """
        Determine the best move using heuristic ordering and minimax.
        
        Args:
            board: Current game board
            
        Returns:
            Column index for the best move
        """
        # Clear the transposition table at the start of each move decision
        # to prevent memory bloat while keeping the table valid for this search
        self.transposition_table = {}
        
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return -1  # No valid moves
        
        # Check for immediate win or block
        for col in valid_moves:
            new_board = board.copy()
            success, _ = new_board.drop_piece(col, self.player_number)
            if success and new_board.check_win(self.player_number):
                return col  

        for col in valid_moves:
            new_board = board.copy()
            success, _ = new_board.drop_piece(col, self.opponent_number)
            if success and new_board.check_win(self.opponent_number):
                return col  

        # Assign heuristic scores for move ordering
        move_scores = {}
        for col in valid_moves:
            new_board = board.copy()
            success, _ = new_board.drop_piece(col, self.player_number)
            if success:
                move_scores[col] = self._evaluate_position(new_board)

        # Sort moves based on heuristics (higher scores first)
        sorted_moves = sorted(move_scores.keys(), key=lambda c: move_scores[c], reverse=True)

        # Minimax with sorted moves
        best_score = float('-inf')
        best_moves = []
        alpha, beta = float('-inf'), float('inf')

        for col in sorted_moves:
            new_board = board.copy()
            success, _ = new_board.drop_piece(col, self.player_number)
            if success:
                score = self._minimax(new_board, self.search_depth - 1, alpha, beta, False)

                if score > best_score:
                    best_score = score
                    best_moves = [col]
                elif score == best_score:
                    best_moves.append(col)

                alpha = max(alpha, best_score)

        # Prefer center column if multiple best moves exist
        if len(best_moves) > 1:
            best_moves.sort(key=lambda col: abs(col - board.cols // 2))

        return best_moves[0]

    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        """
        Minimax algorithm with alpha-beta pruning and transposition table.
        
        Args:
            board: Current board state
            depth: Search depth
            alpha: Alpha pruning value
            beta: Beta pruning value
            is_maximizing: Whether this is a maximizing or minimizing node
            
        Returns:
            Evaluation score for the board
        """
        # Terminal state checks
        if board.check_win(self.player_number):
            return 1000 + depth
        if board.check_win(self.opponent_number):
            return -1000 - depth
        if board.is_full() or depth == 0:
            return self._evaluate_position(board)

        # Generate hash for current board state
        board_hash = self._get_board_hash(board)
        
        # Check transposition table
        tt_entry = self.transposition_table.get(board_hash)
        if tt_entry is not None:
            stored_depth, stored_value, value_type = tt_entry
            
            if stored_depth >= depth:
                # If we've searched this position to sufficient depth
                if value_type == 'exact':
                    return stored_value
                elif value_type == 'lower' and stored_value > alpha:
                    alpha = stored_value
                elif value_type == 'upper' and stored_value < beta:
                    beta = stored_value
                
                if alpha >= beta:
                    return stored_value

        valid_moves = board.get_valid_moves()
        move_scores = {}

        for col in valid_moves:
            new_board = board.copy()
            success, _ = new_board.drop_piece(col, self.player_number if is_maximizing else self.opponent_number)
            if success:
                move_scores[col] = self._evaluate_position(new_board)

        sorted_moves = sorted(move_scores.keys(), key=lambda c: move_scores[c], reverse=is_maximizing)

        if is_maximizing:
            max_eval = float('-inf')
            for col in sorted_moves:
                new_board = board.copy()
                success, _ = new_board.drop_piece(col, self.player_number)
                if success:
                    eval = self._minimax(new_board, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            
            # Store in transposition table
            value_type = 'exact'
            if max_eval <= alpha:
                value_type = 'upper'
            elif max_eval >= beta:
                value_type = 'lower'
            self.transposition_table[board_hash] = (depth, max_eval, value_type)
            
            return max_eval
        else:
            min_eval = float('inf')
            for col in sorted_moves:
                new_board = board.copy()
                success, _ = new_board.drop_piece(col, self.opponent_number)
                if success:
                    eval = self._minimax(new_board, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            
            # Store in transposition table
            value_type = 'exact'
            if min_eval <= alpha:
                value_type = 'upper'
            elif min_eval >= beta:
                value_type = 'lower'
            self.transposition_table[board_hash] = (depth, min_eval, value_type)
            
            return min_eval

    def _evaluate_position(self, board: Board) -> float:
        """
        Evaluate the board position using cached window positions.
        
        Args:
            board: Current board state
            
        Returns:
            Score for the position (higher is better for the bot)
        """
        score = 0

        # Positional scoring
        for row in range(board.rows):
            for col in range(board.cols):
                if board.grid[row][col] == self.player_number:
                    score += self.position_weights[row][col]
                elif board.grid[row][col] == self.opponent_number:
                    score -= self.position_weights[row][col]

        # Horizontal windows evaluation - using cached positions
        for row, col in self.horizontal_windows:
            window = self._get_window_values(board, row, col, 'horizontal')
            score += self._evaluate_window(window)  # Removed the 1.2 multiplier

        # Vertical windows evaluation - using cached positions
        for row, col in self.vertical_windows:
            window = self._get_window_values(board, row, col, 'vertical')
            score += self._evaluate_window(window)

        # Diagonal down-right windows evaluation - using cached positions
        for row, col in self.diagonal_down_windows:
            window = self._get_window_values(board, row, col, 'diagonal_down')
            score += self._evaluate_window(window)

        # Diagonal up-right windows evaluation - using cached positions
        for row, col in self.diagonal_up_windows:
            window = self._get_window_values(board, row, col, 'diagonal_up')
            score += self._evaluate_window(window)

        # Center column preference
        center_col = board.cols // 2
        center_array = [board.grid[row][center_col] for row in range(board.rows)]
        center_count = center_array.count(self.player_number)
        score += center_count * 3  

        return score

    def _evaluate_window(self, window: list) -> float:
        """
        Evaluate a window of 4 positions.
        
        Args:
            window: List of 4 cell values
            
        Returns:
            Score for the window
        """
        bot_pieces = window.count(self.player_number)
        opponent_pieces = window.count(self.opponent_number)
        empty_pieces = window.count(Board.EMPTY)

        if bot_pieces == 4:
            return 100  
        elif bot_pieces == 3 and empty_pieces == 1:
            return 10   
        elif bot_pieces == 2 and empty_pieces == 2:
            return 3    
        elif opponent_pieces == 3 and empty_pieces == 1:
            return -50  
        elif opponent_pieces == 2 and empty_pieces == 2:
            return -5   

        return 0