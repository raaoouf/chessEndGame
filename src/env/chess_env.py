import gymnasium as gym
from gymnasium import spaces
import chess
import numpy as np
from .position_sampler import get_balanced_random_position

class MiniChessEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        
        # Action space: all legal UCI moves (can be filtered later)
        self.uci_moves = [move.uci() for move in chess.Board().legal_moves]
        self.action_space = spaces.Discrete(len(self.uci_moves))
        
        # Observation space: binary plane for each piece type + turn
        self.observation_space = spaces.Box(0, 1, (8, 8, 12), dtype=np.int8)

    def step(self, action):
        # 1. Convert action to UCI via the *current* list
        move_str = self.uci_moves[action]
        move = chess.Move.from_uci(move_str)

        # 2. Validate & apply
        if move not in self.board.legal_moves:
            return self._get_obs(), -1.0, True, {}
        self.board.push(move)

        # 3. (Later) compute reward via Stockfish delta
        reward = 0.0
        done = self.board.is_game_over()

        # 4. Rebuild legal moves for next step
        self.uci_moves = [m.uci() for m in self.board.legal_moves]
        self.action_space = spaces.Discrete(len(self.uci_moves))

        return self._get_obs(), reward, done, {}


    def reset(self, seed=None, options=None):
        self.board = chess.Board()
        return self._get_obs(), {}

    def _get_obs(self):
        # Return a simple 8x8x12 board representation (to be customized)
        return np.zeros((8, 8, 12), dtype=np.int8)
if __name__ == "__main__":
    env = MiniChessEnv()
    obs, _ = env.reset()
    obs, r, done, _ = env.step(0)
    print("OK:", obs.shape, r, done)