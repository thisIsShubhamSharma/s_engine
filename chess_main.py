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
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen, gs):
    draw_board(screen)

    draw_pieces(screen, gs.board)


def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row+column) % 2)]
            p.draw.rect(screen, color, p.Rect(
                column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    pass


if __name__ == "__main__":
    main()
