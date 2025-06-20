import chess
import random
from stockfish import Stockfish
import os

# Adjust the path to your Stockfish binary if needed
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
stockfish_path = os.path.join(project_root, "bin", "stockfish.exe")

stockfish = Stockfish(path=stockfish_path, depth=12)
stockfish.set_skill_level(10)

def is_fair_position(fen, cp_threshold=100):
    stockfish.set_fen_position(fen)
    eval_info = stockfish.get_evaluation()
    
    if eval_info['type'] == 'cp':
        cp = eval_info['value']
        return abs(cp) <= cp_threshold
    return False  # Skip if Stockfish can't evaluate

def get_balanced_random_position(min_pieces=5, max_pieces=6, max_tries=100):
    for _ in range(max_tries):
        board = chess.Board()

        # Play random moves until piece count target is met
        while True:
            if board.is_game_over():
                break

            white_pieces = sum(1 for p in board.piece_map().values() if p.color == chess.WHITE)
            black_pieces = sum(1 for p in board.piece_map().values() if p.color == chess.BLACK)
            
            if (min_pieces <= white_pieces <= max_pieces) and (min_pieces <= black_pieces <= max_pieces):
                break

            move = random.choice(list(board.legal_moves))
            board.push(move)

        # Check if the position is fair
        fen = board.fen()
        if is_fair_position(fen):
            return fen

    raise RuntimeError("Failed to generate a balanced position after many tries.")
