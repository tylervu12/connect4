import os
import time
from typing import Optional
from .game import Game
from .bot import Bot
from .board import Board

class TerminalUI:
    """Terminal-based user interface for Connect 4 game."""
    
    def __init__(self):
        """Initialize the UI with a new game and bot."""
        self.game = Game()
        self.bot = Bot(player_number=Board.PLAYER_2, difficulty=4)
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def get_player_move(self) -> Optional[int]:
        """
        Get and validate the player's move.
        
        Returns:
            Column number or None if player wants to quit
        """
        valid_moves = self.game.get_valid_moves()
        
        while True:
            try:
                user_input = input(f"Your turn! Enter column (0-6) or 'q' to quit: ")
                
                if user_input.lower() == 'q':
                    return None
                    
                col = int(user_input)
                
                if col not in valid_moves:
                    print(f"Invalid move. Please choose from {valid_moves}")
                    continue
                    
                return col
                
            except ValueError:
                print("Please enter a number between 0 and 6.")
    
    def play_game(self):
        """Run the main game loop."""
        self.clear_screen()
        print("Welcome to Connect 4!")
        print("You are X, the bot is O.")
        print("Enter a column number (0-6) to make your move.")
        print("\nPress Enter to start...")
        input()
        
        # Main game loop
        while not self.game.is_game_over():
            self.clear_screen()
            print(self.game)
            
            current_player = self.game.get_current_player()
            
            if current_player == Board.PLAYER_1:  # Human player
                col = self.get_player_move()
                
                if col is None:  # Player quit
                    print("Thanks for playing!")
                    return
                    
                success, message = self.game.make_move(col)
                
                if message:
                    print(message)
                    
            else:  # Bot's turn
                print("Bot is thinking...")
                # Add a small delay to make it feel more natural
                time.sleep(1)
                col = self.bot.get_move(self.game.board)
                success, message = self.game.make_move(col)
                print(f"Bot placed in column {col}")
                
                if message:
                    print(message)
                    time.sleep(1)  # Give player time to read any messages
        
        # Game over
        self.clear_screen()
        print(self.game)
        
        winner = self.game.get_winner()
        if winner == Board.PLAYER_1:
            print("Congratulations! You won!")
        elif winner == Board.PLAYER_2:
            print("The bot won this time. Better luck next time!")
        else:
            print("It's a draw!")
            
        play_again = input("Play again? (y/n): ")
        if play_again.lower() == 'y':
            self.game.reset()
            self.play_game()
        else:
            print("Thanks for playing!")

    def show_instructions(self):
        """Display game instructions."""
        self.clear_screen()
        print("=== CONNECT 4 INSTRUCTIONS ===")
        print("\nOBJECTIVE:")
        print("Be the first to connect 4 of your pieces in a row horizontally, vertically, or diagonally.")
        print("\nHOW TO PLAY:")
        print("1. You are X, the bot is O")
        print("2. Players take turns dropping pieces into columns")
        print("3. Pieces fall to the lowest available position in the chosen column")
        print("4. The game ends when a player connects 4 in a row or the board is full")
        print("\nPress Enter to continue...")
        input()