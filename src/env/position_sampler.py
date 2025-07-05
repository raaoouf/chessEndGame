import chess
import random
from stockfish import Stockfish
import platform
import os

def get_stockfish_path():
    try:
        if "google.colab" in str(get_ipython()):
            return "/usr/games/stockfish"
    except NameError:
        pass

    proj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    exe = "stockfish.exe" if platform.system() == "Windows" else "stockfish"
    return os.path.join(proj, "bin", exe)
#depth 8 reduced 3la jal time gain, and skill level 10 to get better moves than random moves
stockfish = Stockfish(path=get_stockfish_path(), depth=8)  
stockfish.set_skill_level(10)

def is_fair_position(fen, cp_threshold=150):
    stockfish.set_fen_position(fen)
    eval_info = stockfish.get_evaluation()
    if eval_info['type'] == 'cp': 
        return abs(eval_info['value']) <= cp_threshold
    return False

def get_balanced_random_position(min_pieces=4, max_pieces=6, max_tries=100):
    for trial in range(max_tries):
        board = chess.Board()
        move_count = 0

        for _ in range(150): 
            if board.is_game_over():
                break

            stockfish.set_fen_position(board.fen())
            moves = stockfish.get_top_moves(5)
            if not moves:
                break

            candidate_moves = moves[:3] if len(moves) >= 3 else moves
            move_info = random.choice(candidate_moves)
            move_str = move_info['Move']
            move = chess.Move.from_uci(move_str)

            if move not in board.legal_moves:
                break

            board.push(move)
            move_count += 1

            white_pieces = sum(1 for p in board.piece_map().values()
                               if p.color == chess.WHITE and p.piece_type != chess.KING)
            black_pieces = sum(1 for p in board.piece_map().values()
                               if p.color == chess.BLACK and p.piece_type != chess.KING)

            if (min_pieces <= white_pieces <= max_pieces) and (min_pieces <= black_pieces <= max_pieces):
                fen = board.fen()
                if is_fair_position(fen):
                    print(f"fair position on trial {trial} after {move_count} moves: {white_pieces}W, {black_pieces}B")
                    return fen

        print(f"[trial {trial}] no fair position found")

    raise RuntimeError("failed to generate a balanced fair position")

if __name__ == "__main__":
    print("sampling balanced position")
    fen = get_balanced_random_position()
    print("final FEN:", fen)
