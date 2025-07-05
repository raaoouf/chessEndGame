import time
import chess
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from src.env.position_sampler import get_balanced_random_position
from stockfish import Stockfish
import os

class MiniChessEnv(gym.Env):
    def __init__(self):
        super().__init__()

        # --- Stockfish setup for Module 2 ---
        # stockfish.exe is located: [this file]/../..​/bin/stockfish.exe
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sf_exe = os.path.join(base_dir, "..", "..", "bin", "stockfish.exe")
        self.stockfish = Stockfish(path=sf_exe, depth=8)
        self.stockfish.set_skill_level(10)

        # --- Action & observation spaces (Module 1, already done) ---
        # precompute all possible UCI moves (64×64 = 4096)
        self.uci_moves = sorted([a + b
                                 for a in [f"{f}{r}" for f in 'abcdefgh' for r in '12345678']
                                 for b in [f"{f}{r}" for f in 'abcdefgh' for r in '12345678']])
        self.action_space = spaces.Discrete(len(self.uci_moves))
        self.observation_space = spaces.Box(0, 1, (8, 8, 12), dtype=np.int8)

        self.board = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        fen = get_balanced_random_position()
        self.board = chess.Board(fen)
        return self._get_obs(), {}

    def step(self, action: int):
        # stockfish eval before move
        self.stockfish.set_fen_position(self.board.fen())
        t0 = time.time()
        eval_before = self.stockfish.get_evaluation()
        dt_before = time.time() - t0

        cp_before = eval_before['value'] if eval_before['type'] == 'cp' else 0

        # agent's action 
        move_uci = self.uci_moves[action]
        move = chess.Move.from_uci(move_uci)
        if move not in self.board.legal_moves:
            # illegal move: heavy penalty, episode ends
            return self._get_obs(), -1.0, True, False, {}
        self.board.push(move)

        # stockfish eval after move
        self.stockfish.set_fen_position(self.board.fen())
        t1 = time.time()
        eval_after = self.stockfish.get_evaluation()
        dt_after = time.time() - t1

        cp_after = eval_after['value'] if eval_after['type'] == 'cp' else 0

        delta_cp = cp_after - cp_before
        reward = delta_cp / 100.0

        done = self.board.is_game_over()
        if done:
            result = self.board.result()  # "1-0", "0-1", or "1/2-1/2"
            if result == "1-0" and self.board.turn == chess.BLACK:
                reward += 1.0   
            elif result == "0-1" and self.board.turn == chess.WHITE:
                reward += 1.0   
            else:
                reward -= 1.0  

        print(f"[SF timings] depth={self.stockfish.depth}: "
              f"before={dt_before:.3f}s after={dt_after:.3f}s")

        return self._get_obs(), reward, done, False, {}

    def _get_obs(self):
        obs = np.zeros((8, 8, 12), dtype=np.int8)
        for square, piece in self.board.piece_map().items():
            r, c = divmod(square, 8)
            plane = (piece.piece_type - 1) + (0 if piece.color == chess.WHITE else 6)
            obs[r, c, plane] = 1
        return obs


#####testing
if __name__ == "__main__":
    env = MiniChessEnv()
    obs, _ = env.reset()
    total_reward = 0
    done = False

    while not done:
        action = env.action_space.sample()
        obs, reward, done, _, _ = env.step(action)
        total_reward += reward

    print("Test episode finished.")
    print("Total reward:", total_reward)