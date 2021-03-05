"""
@author - thisIsShubhamSharma
Date - 03-01-2021
Main driver file - Displays board and handels user input.
"""
import os
import pygame as p
import chess_engine

p.init()

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 30
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
    load_images()
    running = True
    sq_selected = ()  # keeps track of last user click. tuple(row,col)
    # keeps track of user clicks. list[tuple(row,col), tuple(row,col)]
    player_clicks = []
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            if e.type == p.MOUSEBUTTONDOWN:
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
                    gs.make_move(move)
                    sq_selected = ()
                    player_clicks = []
        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen, gs):
    draw_board(screen)

    draw_pieces(screen, gs.board)


'''
Draws the board.
'''


def draw_board(screen):
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


if __name__ == "__main__":
    main()
