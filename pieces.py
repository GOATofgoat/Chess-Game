import pygame
import copy  # Add this import at the top
from constants import PIECE_IMAGE_SCALE

class Piece(pygame.sprite.Sprite):
    def __init__(self, type, color, row, col):
        super().__init__()
        self.type = type
        self.color = color
        self.row = row
        self.col = col

        path = f"assets/{color}_{type}.png"
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, PIECE_IMAGE_SCALE)
        self.rect = self.image.get_rect()
        
  


def is_valid_move(piece, board_state, row, col, en_passant_target=None, en_passant_turn=-1, turn=0):
    start_row = piece.row
    start_col = piece.col
    target = board_state[row][col]
    # Prevent capturing own piece
    if target is not None and target.color == piece.color:
        return False
    # Pawn Piece Logic
    if piece.type == "pawn":
        if piece.color == "white":
            direction = -1
            start_rank = 6
        else:
            direction = 1  
            start_rank = 1
        
        # Move forward 1 square
        if row == start_row + direction and col == start_col:
            if board_state[row][col] is None:
                return True
        
        # Move forward 2 squares from starting position
        if start_row == start_rank and row == start_row + 2 * direction and col == start_col:
            between_row = start_row + direction
            if board_state[between_row][col] is None and board_state[row][col] is None:
                return True  
        
        # Diagonal capture (normal + en passant)
        if row == start_row + direction and abs(col - start_col) == 1:
            # Normal capture
            if target is not None and target.color != piece.color:
                return True
            
            # En passant capture  ← ADDED THIS SECTION
            if en_passant_target and (row, col) == en_passant_target:
                if turn == en_passant_turn + 1:
                    return True
    
            
            
    # Rook Piece Logic
    if piece.type == "rook":
        if row == start_row:
            step = -1 if start_col > col else 1
            for c in range(start_col + step, col, step):
                if board_state[row][c] is not None:
                    return False
            if start_col != col:
                if target is None or target.color != piece.color:
                    return True
        if col == start_col:
            step = -1 if start_row > row else 1
            for r in range(start_row + step, row, step):
                if board_state[r][col] is not None:
                    return False
            if start_row != row:
                if target is None or target.color != piece.color:
                    return True
    # Knight Piece Logic
    if piece.type == "knight":
        if (abs(row - start_row) == 2 and abs(col - start_col) == 1) or (abs(col - start_col) == 2 and abs(row - start_row) == 1):
            if target is None or target.color != piece.color:
                return True
    # Bishop Piece Logic
    if piece.type == "bishop":
        if abs(row - start_row) == abs(col - start_col): 
            row_step = 1 if row > start_row else -1
            col_step = 1 if col > start_col else -1
            r, c = start_row + row_step, start_col + col_step
            while r != row and c != col:
                if board_state[r][c] is not None:
                    return False  
                r += row_step
                c += col_step
            if target is None or target.color != piece.color:
                return True
    # Queen Piece Logic
    if piece.type == "queen":
        # Horizontal
        if row == start_row:
            step = 1 if col > start_col else -1
            for c in range(start_col + step, col, step):
                if board_state[row][c] is not None:
                    return False
            if target is None or target.color != piece.color:
                return True
        # Vertical
        if col == start_col:
            step = 1 if row > start_row else -1
            for r in range(start_row + step, row, step):
                if board_state[r][col] is not None:
                    return False
            if target is None or target.color != piece.color:
                return True
        # Diagonal
        if abs(row - start_row) == abs(col - start_col): 
            row_step = 1 if row > start_row else -1
            col_step = 1 if col > start_col else -1
            r, c = start_row + row_step, start_col + col_step
            while r != row and c != col:
                if board_state[r][c] is not None:
                    return False
                r += row_step
                c += col_step
            if target is None or target.color != piece.color:
                return True
    # King Piece Logic
    if piece.type == "king":
        if target is not None and target.color == piece.color:
            return False
        if abs(start_row - row) <= 1 and abs(start_col - col) <= 1:
            return True  
    return False


def look_for_check(board_state, turn):
    if turn % 2 == 1:
        king_color = "white"
        king_type = "king"
    else:
        king_color = "black"
        king_type = "king"

    king_row = None
    king_col = None
    for r in range(8):
        for c in range(8):
            current = board_state[r][c]
            if current is not None and current.color == king_color and current.type == king_type:
                king_row = r
                king_col = c
                break
        if king_row is not None:
            break

    if king_row is None or king_col is None:
        print("Error: King not found on board")
        return False

    # Rook / Queen horizontal and vertical
    for step in [1, -1]:
        c = king_col + step
        while 0 <= c < 8:
            p = board_state[king_row][c]
            if p is not None:
                if p.color != king_color and p.type in ["rook", "queen"]:
                    return True
                break
            c += step

    for step in [1, -1]:
        r = king_row + step
        while 0 <= r < 8:
            p = board_state[r][king_col]
            if p is not None:
                if p.color != king_color and p.type in ["rook", "queen"]:
                    return True
                break
            r += step

    # Bishop / Queen diagonals
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dr, dc in directions:
        r, c = king_row + dr, king_col + dc
        while 0 <= r < 8 and 0 <= c < 8:
            p = board_state[r][c]
            if p is not None:
                if p.color != king_color and p.type in ["bishop", "queen"]:
                    return True
                break
            r += dr
            c += dc

    # Knight
    knight_moves = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
    for dr, dc in knight_moves:
        r, c = king_row + dr, king_col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            p = board_state[r][c]
            if p is not None and p.color != king_color and p.type == "knight":
                return True

    # Pawn
    if king_color == "white":
        pawn_row = king_row - 1
        pawn_cols = [king_col - 1, king_col + 1]
    else:
        pawn_row = king_row + 1
        pawn_cols = [king_col - 1, king_col + 1]

    for c in pawn_cols:
        if 0 <= pawn_row < 8 and 0 <= c < 8:
            p = board_state[pawn_row][c]
            if p is not None and p.color != king_color and p.type == "pawn":
                return True

    return False


def is_legal_move(piece, board_state, row, col, en_passant_target=None, en_passant_turn=-1, turn=0):
    # First check basic move validity
    if not is_valid_move(piece, board_state, row, col, en_passant_target, en_passant_turn, turn):
        return False
    
    # --- TEMPORARILY make the move on the REAL board ---
    old_row = piece.row
    old_col = piece.col
    captured_piece = board_state[row][col]
    
    # Move the piece
    board_state[old_row][old_col] = None
    board_state[row][col] = piece
    piece.row = row
    piece.col = col
    
    # Check if our king is in check after this move
    in_check = look_for_check(board_state, turn + 1)
    
    # UNDO MOVE
    piece.row = old_row
    piece.col = old_col
    board_state[old_row][old_col] = piece
    board_state[row][col] = captured_piece
    
    # If move left us in check, it's illegal
    return not in_check

