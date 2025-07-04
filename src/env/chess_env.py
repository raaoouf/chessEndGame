import gymnasium as gym
import chess
import numpy as np
from src.env.position_sampler import get_balanced_random_position
from gymnasium import spaces
import stockfish
class MiniChessEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        # init will be updated in reset()
        self.uci_moves = [move.uci() for move in self.board.legal_moves]
        self.action_space = spaces.Discrete(len(self.uci_moves))
        self.observation_space = spaces.Box(0, 1, (8, 8, 12), dtype=np.int8)

    def reset(self, seed=None, options=None):
        fen = get_balanced_random_position()
        self.board.set_fen(fen)
        self.uci_moves = [m.uci() for m in self.board.legal_moves]
        self.action_space = spaces.Discrete(len(self.uci_moves))
        return self._get_obs(), {}
    
    def observation_space(self):   # En passant square, None if not applicable   
        self.observation_space = gym.spaces.Dict({
            'board': gym.spaces.Box(low=0, high=1, shape=(8, 8, 12), dtype=np.float32),
            'data': gym.spaces.Dict({
            'turn': gym.spaces.Discrete(2),
            'is_check': gym.spaces.Discrete(2),
            'ep_square': gym.spaces.Discrete(65),  # optional: always 64 if no EP
    })
})
    def _get_obs(self):
        obs = np.zeros((8, 8, 12), dtype=np.int8)
        for square, piece in self.board.piece_map().items():
            row, col = divmod(square, 8)
            plane = (piece.piece_type - 1) + (0 if piece.color == chess.WHITE else 6)
            obs[row][col][plane] = 1
        return obs    
        return self.observation_space
    def action_space(self):
        # Define the action space, e.g., all legal moves in UCI format
        self.board.legal_moves = list(self.board.legal_moves)
        self.board.legal_moves = [move.uci() for move in self.board.legal_moves]
        self.board.legal_moves.sort()
        return gym.spaces.Discrete(len(list(self.board.legal_moves)))
if __name__ == "__main__":
    env = MiniChessEnv()
    obs, _ = env.reset()
    obs, r, done, _ = env.step(0)
    print("OK:", obs.shape, r, done)
    

    

    

    


