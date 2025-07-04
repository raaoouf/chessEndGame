import streamlit as st
import chess
import chess.svg
import chess.engine
import chess.pgn
import io
import base64
from src.env.position_sampler import get_balanced_random_position
from gym import spaces
def render_svg(svg_data):
    """Helper to render raw SVG in Streamlit."""
    b64 = base64.b64encode(svg_data.encode("utf-8")).decode("utf-8")
    html = f'<div align="center"><img src="data:image/svg+xml;base64,{b64}"/></div>'
    st.write(html, unsafe_allow_html=True)

# -- UI --
st.title("🔍 Chess Position Visualizer")
if st.button("Random Balanced Position"):
    fen = get_balanced_random_position()
    board = chess.Board(fen)
    svg = chess.svg.board(board=board, size=400)
    render_svg(svg)

# Action space test
def test_action_space(board):
    legal_moves = list(board.legal_moves)
    legal_moves_uci = [move.uci() for move in legal_moves]
    legal_moves_uci.sort()
    action_space = spaces.Discrete(len(legal_moves_uci))
    return action_space, legal_moves_uci

# Observation space test
def test_observation_space(board):
    ep_square = board.ep_square if board.ep_square is not None else 64
    obs = {
        'board': (8, 8, 12),  # shape only, not real data
        'data': {
            'turn': int(board.turn),
            'is_check': int(board.is_check()),
            'ep_square': ep_square
        }
    }
    return obs

# Run tests
action_space, legal_moves = test_action_space(board)
obs = test_observation_space(board)

# Display results
st.subheader("Action Space:")
st.write(f"Type: Discrete({action_space.n})")
st.write("Legal moves:")
st.code(legal_moves)

st.subheader("Observation:")
st.json(obs)