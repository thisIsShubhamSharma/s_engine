"""
@author - thisIsShubhamSharma
Date - 03-01-2021
Main driver file - Displays board and handels user input.
"""
import os
import sys

import pygame as p
import chess_engine
import chess_ai

p.init()

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


'''
initialize a global dict of images.
'''


def load_images():
    pieces = ["bP", "bR", "bN", "bB", "bQ", "bK", "bB", "bN",
              "bR", "wP", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(os.path.join(
            'images', piece+'.png')), (SQ_SIZE, SQ_SIZE))


'''
Main function
'''


def main():

    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chess_engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag for if a new move has been made

    animate = False  # flag for animation

    load_images()
    running = True

    sq_selected = ()  # keeps track of last user click. tuple(row,col)
    # keeps track of user clicks. list[tuple(row,col), tuple(row,col)]
    player_clicks = []
    game_over = False

    white_did_check = ""
    black_did_check = ""
    last_move_printed = False
    moves_list = []

    turn = 1

    player_one = True  # if true human is playing white
    player_two = False  # if true human is playing black

    while running:
        human_turn = (gs.white_to_move and player_one) or (
            not gs.white_to_move and player_two)
        for e in p.event.get():

            if e.type == p.QUIT:
                running = False
                p.quit()
                sys.exit()

            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE

                    if sq_selected == (row, col):  # user clicked the same square
                        sq_selected = ()  # clear selection
                        player_clicks = []  # clear the list

                    else:
                        sq_selected = (row, col)
                        # append the clicks to the list
                        player_clicks.append(sq_selected)

                    if len(player_clicks) == 2:  # 1st and 2nd click
                        move = chess_engine.Move(
                            player_clicks[0], player_clicks[1], gs.board)
                        # prints the move in chess notation
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                sq_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    if gs.white_to_move:
                        if turn > 1:
                            turn -= 1
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    last_move_printed = False

                if e.key == p.K_r:  # reset the game when r is pressed
                    gs = chess_engine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    turn = 1
                    last_move_printed = False
                    moves_list = []

        # AI move finder
        if not game_over and not human_turn:
            AI_move = chess_ai.findBestMoveNegaMaxAlphaBeta(gs, valid_moves)
            if AI_move is None:
                AI_move = chess_ai.findRandomMove(valid_moves)
            gs.make_move(AI_move, True)
            move_made = True
            animate = True

        if move_made:
            if gs.check_for_pins_and_checks()[0]:
                if not gs.white_to_move:
                    white_did_check = "+"
                else:
                    black_did_check = "+"
            if gs.white_to_move:
                moves_list.append(
                    f"\n{turn}. {gs.move_log[-2].get_chess_notation()}{white_did_check} {gs.move_log[-1].get_chess_notation()}{black_did_check}")
                print(
                    f"\n{turn}. {gs.move_log[-2].get_chess_notation()}{white_did_check} {gs.move_log[-1].get_chess_notation()}{black_did_check}", end="")
                turn += 1
                white_did_check = ""
                black_did_check = ""

            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, sq_selected)

        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, "Black wins by checkmate")
                if not last_move_printed:
                    moves_list[-1] += "+"
                    moves_list.append("result: 0-1")
                    print("+")
                    print("result: 0-1")
                    last_move_printed = True
                    save_game(moves_list)

            else:
                draw_text(screen, "White wins by checkmate")
                if not last_move_printed:
                    moves_list.append(
                        f"\n{turn}. {gs.move_log[-1].get_chess_notation()}++")
                    moves_list.append("result: 1-0")
                    print(
                        f"\n{turn}. {gs.move_log[-1].get_chess_notation()}++")
                    print("result: 1-0")
                    last_move_printed = True
                    save_game(moves_list)

        elif gs.stalemate:
            game_over = True
            draw_text(screen, "Stalemate")
            if not last_move_printed:
                if not gs.white_to_move:
                    moves_list.append(
                        f"\n{turn}. {gs.move_log[-1].get_chess_notation()}")
                    moves_list.append("result: 1/2-1/2")
                    print(f"\n{turn}. {gs.move_log[-1].get_chess_notation()}")
                    print("result: 1/2-1/2")
                    last_move_printed = True
                    save_game(moves_list)

        clock.tick(MAX_FPS)
        p.display.flip()


def save_game(moves_list):
    result = moves_list.pop()
    turns_dict = {}
    for i in range(len(moves_list)-1, -1, -1):
        try:
            if int(moves_list[i][1]) not in turns_dict:
                turns_dict[moves_list[i][1]] = moves_list[i][1:]+"\n"
        except:
            pass
    file = open("game_logs.txt", "w")
    for turn in sorted(turns_dict.keys()):
        file.write(turns_dict[turn])
    file.write(result)
    file.close()


def drawText(screen, text):
    font = p.font.SysFont("Bahnschrift", 32, True, False)
    text_object = font.render(text, 0, p.Color("gray"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - text_object.get_width() / 2, HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))


def highlight_squares(screen, gs, valid_moves, sq_selected):
    '''
    Highlight square selected and moves for piece selected.
    '''
    if (len(gs.move_log)) > 0:
        last_move = gs.move_log[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('blue'))
        screen.blit(s, (last_move.end_col*SQ_SIZE, last_move.end_row*SQ_SIZE))
    if sq_selected != ():
        row, col = sq_selected
        # square_selected is a piece that can be moved
        if gs.board[row][col][0] == ('w' if gs.white_to_move else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            # transparency value 0 -> transparent, 255 -> opaque
            s.set_alpha(100)
            s.fill(p.Color('green'))
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(
                        s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))


def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)


'''
Draws the board.
'''


def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            # adds rows and columns gets reminder if reminder is 1 draws a dark block else if reminder is 0 draws white.
            color = colors[((row+column) % 2)]
            p.draw.rect(screen, color, p.Rect(
                column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draws the pieces on board.
'''


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animate_move(move, screen, board, clock):
    '''
    Animating a move
    '''
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10  # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + d_row * frame / frame_count,
                    move.start_col + d_col * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        # erease the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE,
                            move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(
            col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
