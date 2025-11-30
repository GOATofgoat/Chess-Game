from pieces import Piece

def flip_board(board):
    return [row[::-1] for row in board[::-1]]

def create_starting_board():
    board_state = [
        [Piece("rook", "black", 0, 0), Piece("knight", "black", 0, 1), Piece("bishop", "black", 0, 2), Piece("queen", "black", 0, 3),
         Piece("king", "black", 0, 4), Piece("bishop", "black", 0, 5), Piece("knight", "black", 0, 6), Piece("rook", "black", 0, 7)],
        [Piece("pawn", "black", 1, col) for col in range(8)],
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [Piece("pawn", "white", 6, col) for col in range(8)],
        [Piece("rook", "white", 7, 0), Piece("knight", "white", 7, 1), Piece("bishop", "white", 7, 2), Piece("queen", "white", 7, 3),
         Piece("king", "white", 7, 4), Piece("bishop", "white", 7, 5), Piece("knight", "white", 7, 6), Piece("rook", "white", 7, 7)],
    ]
    return board_state

def get_board_coords(mouse_pos, chessboard_rect, square_width, square_height, flip = False):
    mx, my = mouse_pos
    col = (mx - chessboard_rect.left) // square_width
    row = (my - chessboard_rect.top) // square_height
    
    if flip:
        col = 7 - col
        row = 7 - row
    
    return int(row), int(col)