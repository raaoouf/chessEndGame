from stockfish import Stockfish
stockfish = Stockfish(path="bin/stockfish.exe")
print(stockfish.get_best_move()) 