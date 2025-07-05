# src/reward/stockfish_utils.py

import chess
from stockfish import Stockfish
import os, platform

def get_stockfish_path():
    # 1) If running in Colab, install via apt and use the system binary
    try:
        if "google.colab" in str(get_ipython()):
            return "/usr/games/stockfish"
    except NameError:
        pass  # get_ipython() not defined → we're not in Colab/IPython

    # 2) Otherwise, assume local
    proj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    exe = "stockfish.exe" if platform.system() == "Windows" else "stockfish"
    return os.path.join(proj, "bin", exe)

# Initialize a singleton Stockfish instance
SF = Stockfish(path=get_stockfish_path(), depth=12)
SF.set_skill_level(10)

def evaluate_move_delta(board: chess.Board, move: chess.Move) -> float:
    """
    Returns centipawn delta: eval_after - eval_before.
    Positive if move improves position for side to move.
    """
    # 1) FEN before
    SF.set_fen_position(board.fen())
    before = SF.get_evaluation()['value']
    # 2) Apply and eval
    board.push(move)
    SF.set_fen_position(board.fen())
    after = SF.get_evaluation()['value']
    # 3) Undo move for RL loop consistency
    board.pop()
    return float(after - before)
