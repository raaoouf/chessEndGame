import chess
import random
from stockfish import Stockfish
import platform
import os

# the stockfish thats installed with pip is just a wrapper, so we need hada stockfish.exe 
# that i downloaded from the official sotckfish website and stored in "bin" folder in the main project's folder
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

stockfish = Stockfish(path=get_stockfish_path(), depth=12)
stockfish.set_skill_level(10)
#nconfirmiw bli neither side is more than 1 pawn ahead 
# aka returns true idha stock fish evaluation egale +/-100 score
def is_fair_position(fen, cp_threshold=100):
    stockfish.set_fen_position(fen)
    eval_info = stockfish.get_evaluation()
    
    if eval_info['type'] == 'cp': 
        cp = eval_info['value']
        return abs(cp) <= cp_threshold
    return False  

def get_balanced_random_position(min_pieces=5, max_pieces=6, max_tries=100):
    for _ in range(max_tries):
        board = chess.Board()

        # play random moves until piece count target is met
        while True:
            if board.is_game_over():
                break

            white_pieces = sum(1 for p in board.piece_map().values() if p.color == chess.WHITE)
            black_pieces = sum(1 for p in board.piece_map().values() if p.color == chess.BLACK)
            
            if (min_pieces <= white_pieces <= max_pieces) and (min_pieces <= black_pieces <= max_pieces):
                break

            move = random.choice(list(board.legal_moves))
            board.push(move)

        # check if the position is fair
        fen = board.fen()
        if is_fair_position(fen):
            return fen

    raise RuntimeError("Failed to generate a balanced position after many tries.")
