# main.py
from connect4.ui import TerminalUI

def main():
    """Run the Connect 4 game."""
    ui = TerminalUI()
    ui.play_game()

if __name__ == "__main__":
    main()