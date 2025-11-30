"""
Louis Urbina
Sources: (PyGame Documentation: https://www.pygame.org/docs/index.html, Sprite Images: https://opengameart.org/)

May 2025 - August 2025: 
- Chess board and piece rendering using Pygame sprites and images
- Piece movement logic for all standard chess pieces (pawn, rook, knight, bishop, queen, king)
- Turn tracking and board flipping
- Piece selection and drag and drop movement with mouse events
- Move validation for all pieces, including legal moves and captures
- Capturing opponent pieces and removing them from the board and sprite group
- Basic check detection using check function
- Source attribution for images and documentation


Nov 17, 2025 - Nov 18, 2025: 
- Added pawn promotion to logic and pop up menu for selecting promotion piece

"""

import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_IMG_PATH, CHESSBOARD_IMG_PATH, PIECE_IMAGE_SCALE
from pieces import is_valid_move, look_for_check, is_legal_move
from board import create_starting_board, get_board_coords
from gameui import show_pawn_promotion_menu, draw_promotion_menu

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()  # For delta time

background_img = pygame.image.load(BACKGROUND_IMG_PATH).convert_alpha()
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
chessboard_img = pygame.image.load(CHESSBOARD_IMG_PATH).convert_alpha()
chessboard_img = pygame.transform.scale(chessboard_img, (700, 500))

screen_rect = screen.get_rect()
chessboard_rect = chessboard_img.get_rect()
chessboard_rect.center = screen_rect.center

square_width = chessboard_rect.width // 8
square_height = chessboard_rect.height // 8

def update_sprite_positions(board_state, flip=False):
    group = pygame.sprite.Group()
    for row in range(8):
        for col in range(8):
            piece = board_state[row][col]
            if piece:
                draw_row = 7 - row if flip else row
                draw_col = 7 - col if flip else col
                x = chessboard_rect.left + draw_col * square_width + 25
                y = chessboard_rect.top + draw_row * square_height
                piece.rect.topleft = (x, y)
                group.add(piece)
    return group

def apply_promotion(board_state, all_sprites, pos, color, new_type, turn):
    if pos is None:
        return
    r, c = pos
    pawn = board_state[r][c]
    if pawn is None:
        return
    if getattr(pawn, "type", None) != "pawn":
        return
    
    # Change piece type
    pawn.type = new_type
    
   
    img_path = f"images/{color}_{new_type}.png"
    try:
        new_img = pygame.image.load(img_path).convert_alpha()
        pawn.image = pygame.transform.scale(new_img, PIECE_IMAGE_SCALE)  # (40, 50)
        pawn.rect = pawn.image.get_rect()  # Create new rect from scaled image
    except Exception as e:
        print("Failed to load promoted image:", img_path, e)
        return
    
    # Recalculate ALL piece positions with correct flip state
    flip_view = (turn % 2 == 1)
    refreshed = update_sprite_positions(board_state, flip_view)
    all_sprites.empty()
    for spr in refreshed:
        all_sprites.add(spr)

board_state = create_starting_board()
all_sprites = update_sprite_positions(board_state)

selected_piece = None
turn = 0
running = True

promotion_menu_active = False
promoting_color = None
promoting_pos = None
promotion_buttons = []
promotion_menu_rect = None
promotion_buttons_ready = False


en_passant_target = None
en_passant_turn = -1

# Castling Flags
white_king_has_moved = False
white_kingside_rook_has_moved = False   
white_queenside_rook_has_moved = False  
black_king_has_moved = False
black_kingside_rook_has_moved = False   
black_queenside_rook_has_moved = False 

while running:
    dt = clock.tick(60)  
    flip_view = (turn % 2 == 1)  
    mouse_pos = pygame.mouse.get_pos()

    # Update button hover states
    if promotion_menu_active and promotion_buttons:
        for btn in promotion_buttons:
            btn.update(mouse_pos, dt)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if promotion_menu_active:
                for btn in promotion_buttons:
                    if btn.handle_click(mouse_pos):
                        apply_promotion(board_state, all_sprites, promoting_pos, promoting_color, btn.piece_name, turn)
                        promotion_menu_active = False
                        promoting_color = None
                        promoting_pos = None
                        promotion_buttons = []
                        promotion_menu_rect = None
                        promotion_buttons_ready = False
                        turn += 1
                        flip_view = (turn % 2 == 1)
                        all_sprites = update_sprite_positions(board_state, flip_view)
                        break
                continue  # Skip normal selection while menu open

            row, col = get_board_coords(mouse_pos, chessboard_rect, square_width, square_height, flip_view)
            for sprite in all_sprites:
                if sprite.rect.collidepoint(mouse_pos):
                    if (turn % 2 == 0 and sprite.color == "white") or (turn % 2 == 1 and sprite.color == "black"):
                        selected_piece = sprite
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_piece and not promotion_menu_active:
                old_row, old_col = selected_piece.row, selected_piece.col
                new_row, new_col = get_board_coords(mouse_pos, chessboard_rect, square_width, square_height, flip_view)
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if is_legal_move(selected_piece, board_state, new_row, new_col, en_passant_target, en_passant_turn, turn):
                        board_state[old_row][old_col] = None

                        # CHECK FOR EN PASSANT CAPTURE
                        is_en_passant_capture = False
                        if selected_piece.type == "pawn" and (new_row, new_col) == en_passant_target:
                            if turn == en_passant_turn + 1:
                                is_en_passant_capture = True
                                
                                # Calculate where the captured pawn actually is
                                if selected_piece.color == "white":
                                    captured_pawn_row = new_row + 1  
                                else:
                                    captured_pawn_row = new_row - 1  
                                
                                captured_pawn_col = new_col
                                
                                # Remove the pawn from its actual location
                                captured_pawn = board_state[captured_pawn_row][captured_pawn_col]
                                if captured_pawn:
                                    all_sprites.remove(captured_pawn)  
                                    board_state[captured_pawn_row][captured_pawn_col] = None
                        
                        # Normal capture (only if NOT en passant)
                        if not is_en_passant_capture:
                            captured = board_state[new_row][new_col]
                            if captured is not None and captured.color != selected_piece.color:
                                all_sprites.remove(captured)  
                        
                        board_state[new_row][new_col] = selected_piece
                        selected_piece.row = new_row
                        selected_piece.col = new_col
                        
                      
                        # Reset
                        en_passant_target = None
                        
                        # Check if a pawn just moved 2
                        if selected_piece.type == "pawn":
                            # White pawn moved from row 6 to row 4
                            if selected_piece.color == "white" and old_row == 6 and new_row == 4:
                                en_passant_target = (5, new_col)  # Target is the skipped square
                                en_passant_turn = turn

                            # Black pawn moved from row 1 to row 3
                            elif selected_piece.color == "black" and old_row == 1 and new_row == 3:
                                en_passant_target = (2, new_col)  
                                en_passant_turn = turn
                                
                            #Check for pawn promotion
                            if selected_piece.color == "white" and new_row == 0:
                                promotion_menu_active = True
                                promoting_color = "white"
                                promoting_pos = (new_row, new_col)
                                promotion_buttons_ready = False
                            elif selected_piece.color == "black" and new_row == 7:
                                promotion_menu_active = True
                                promoting_color = "black"
                                promoting_pos = (new_row, new_col)
                                promotion_buttons_ready = False
                                
                        if not promotion_menu_active:
                            turn += 1
                            flip_view = (turn % 2 == 1)
                            all_sprites = update_sprite_positions(board_state, flip_view)
                            
                          
                    else:
                        draw_row = 7 - old_row if flip_view else old_row
                        draw_col = 7 - old_col if flip_view else old_col
                        x = chessboard_rect.left + draw_col * square_width + 25
                        y = chessboard_rect.top + draw_row * square_height
                        selected_piece.rect.topleft = (x, y)
                selected_piece = None

    # Update dragging
    if selected_piece and not promotion_menu_active:
        selected_piece.rect.center = mouse_pos

    # Draw everything
    screen.blit(background_img, (0, 0))
    screen.blit(chessboard_img, chessboard_rect.topleft)
    all_sprites.draw(screen)

    if promotion_menu_active:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        if not promotion_buttons_ready:
            promotion_buttons, promotion_menu_rect = show_pawn_promotion_menu(promoting_color)
            promotion_buttons_ready = True
        else:
            draw_promotion_menu(promotion_buttons, promotion_menu_rect, promoting_color)
    
    pygame.display.flip()
    

pygame.quit()
