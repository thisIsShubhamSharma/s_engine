"""
@author - thisIsShubhamSharma
Date - 03-01-2021
Storage Class - Stores board state , void moves, move log.
"""


class GameState():

    def __init__(self):
        # 8x8 board represented by a 2d list
        # b_ and w_ are for color
        # -- is a black spaces
        # _R for rook
        # _N for knight
        # _B for bishop
        # _Q for queen
        # _K for king
        # _P for pawn

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.whiteToMove = True
        self.MoveLog = []
