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
        self.move_functions = {
            'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
            'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves
        }

        self.white_to_move = True
        self.move_log = []

        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)

        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []

        # coordinates for the square where en passsant capture is possible
        self.enpassant_possible = ()
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    '''
    move function does not handle castling, am-pasand, pawn promotion
    '''

    def make_move(self, move, b=False):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # log moves
        self.white_to_move = not self.white_to_move  # change turn
        # update king's postion
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            # take this to UI later
            promoted_piece = input("Promote to Q, R, B, or N:")
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + \
                promoted_piece

        # enpassant move
        if move.is_enpassant_move:
            # capturing the pawn
            self.board[move.start_row][move.end_col] = "--"

        # update enpassant_possible variable
        # only on 2 square pawn advance
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = (
                (move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # kingside castle move
                # moves the rook to its new square
                self.board[move.end_row][move.end_col -
                                         1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col +
                                         1] = '--'  # erease old rook
            else:  # queenside castle move
                # moves the rook to its new square
                self.board[move.end_row][move.end_col +
                                         1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col -
                                         2] = '--'  # erease old rook

        # update castling rights - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                   self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    '''
    Undo move function 
    '''

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
        # update king's postion
        if move.piece_moved == 'wK':
            self.white_king_location = (move.start_row, move.start_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.start_row, move.start_col)
        # undo en passant move
            if move.is_enpassant_move:
                # leave landing square blank
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)
            # undo a 2 square pawn advance
            if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ()
            # undo castle rights
            # get rid of the new castle rights from the move we are undoing
            self.castle_rights_log.pop()
            # set the current castle rights to the last one in the list
            self.current_castling_rights = self.castle_rights_log[-1]
            # undo the casle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # kingside
                    self.board[move.end_row][move.end_col +
                                             1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = '--'
                else:  # qeenside
                    self.board[move.end_row][move.end_col -
                                             2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = '--'

    def updateCastleRights(self, move):
        '''
        Update the castle rights given the move
        '''
        if move.piece_captured == "wR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.bks = False

        if move.piece_moved == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.bks = False

    '''
    Returns if the player is in check, a list of pins, and a list of checks 
    '''

    def check_for_pins_and_checks(self):
        pins = []  # squares where the allied pinned piece in and direction pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():  # 1st allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif end_piece[0] == enemy_color:
                        type_p = end_piece[1]
                        # 5 possibilities here in this complex conditional
                        #
                        # 1. orthogonally away from king and piece is a rook
                        # 2. diagonally away from king and piece is a bishop
                        # 3. 1 square away diagonally from king and piece is a pawn
                        # 4. any direction and piece is a queen
                        # 5. any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king.)
                        if (0 <= j <= 3 and type_p == 'R') or (4 <= j <= 7 and type_p == 'B') or (i == 1 and type_p == 'P' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or (type_p == 'Q') or (i == 1 and type_p == 'K'):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # enemy knight attacking king
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks

    def get_valid_moves(self):
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 piece check -> block check or move king
                moves = self.get_all_possible_moves()
                # to block check -> move a piece between check piece and king.
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                # check causing piece
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (
                            king_row + check[2] * i, king_col + check[3] * i)  # check[2] and check[3] are the check direction
                        valid_squares.append(valid_square)
                        # once your get to piece amf checks
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                # get rid of an moves that don't block check or move king
                # IMPORTANT : go through backwards when you are removing from a list as iterating
                for i in range(len(moves) - 1, -1, -1):
                    # move does't move king so it must block or capture
                    if moves[i].piece_moved[1] != 'K':
                        # move doesn't block check ot capture piece
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:  # double check king has to move
                self.get_king_moves(king_row, knig_col, moves)
        else:  # not in check
            moves = self.get_all_possible_moves()
            if self.white_to_move:
                self.getCastleMoves(
                    self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.getCastleMoves(
                    self.black_king_location[0], self.black_king_location[1], moves)

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.current_castling_rights = temp_castle_rights

        return moves

    def inCheck(self):
        '''
        Determine if a current player is in check
        '''
        if self.white_to_move:
            return self.squareUnderAttack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.squareUnderAttack(self.black_king_location[0], self.black_king_location[1])

    def squareUnderAttack(self, row, col):
        '''
        Determine if enemy can attack the square row col
        '''
        self.white_to_move = not self.white_to_move  # switch to oponent's point of wiev
        opponents_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if(turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    # call the move function using dict basend on piece type.
                    self.move_functions[piece](row, col, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.white_to_move:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"

        if self.board[r+move_amount][c] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(
                    Move((r, c), (r + move_amount, c), self.board))
                # 2 square pawn advance
                if r == start_row and self.board[r + 2 * move_amount][c] == "--":
                    moves.append(
                        Move((r, c), (r + 2 * move_amount, c), self.board))
        if c - 1 >= 0:  # capture to the left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[r + move_amount][c - 1][0] == enemy_color:
                    moves.append(
                        Move((r, c), (r + move_amount, c - 1), self.board))
                if (r + move_amount, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + move_amount,
                                               c - 1), self.board, is_enpassant_move=True))
        if c + 1 <= 7:  # capture to the right
            if not piece_pinned or pin_direction == (move_amount, +1):
                if self.board[r + move_amount][c + 1][0] == enemy_color:
                    moves.append(
                        Move((r, c), (r + move_amount, c + 1), self.board))
                if (r + move_amount, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + move_amount,
                                               c + 1), self.board, is_enpassant_move=True))
        # old code {not usefull}
        # if self.white_to_move:  # white pawn moves
        #     if self.board[r-1][c] == '--':  # 1 square pawn advance
        #         if not piece_pinned or pin_direction == (-1, 0):
        #             moves.append(Move((r, c), (r-1, c), self.board))
        #             # 2 square pawn advance
        #             if r == 6 and self.board[r-2][c] == '--':
        #                 moves.append(Move((r, c), (r-2, c), self.board))
        #     if c-1 >= 0:  # capture to the left
        #         if self.board[r-1][c-1][0] == 'b':  # enemy piece to capture
        #             if not piece_pinned or pin_direction == (-1, -1):
        #                 moves.append(Move((r, c), (r-1, c-1), self.board))
        #     if c+1 <= 7:  # capture to the right
        #         if self.board[r-1][c+1][0] == 'b':  # enemy piece to capture
        #             if not piece_pinned or pin_direction == (-1, 1):
        #                 moves.append(Move((r, c), (r-1, c+1), self.board))
        # else:  # black pawn moves
        #     if self.board[r+1][c] == '--':  # 1 square pawn advance
        #         if not piece_pinned or pin_direction == (1, -1):
        #             moves.append(Move((r, c), (r+1, c), self.board))
        #             # 2 square pawn advance
        #             if r == 1 and self.board[r+2][c] == '--':
        #                 moves.append(Move((r, c), (r+2, c), self.board))
        #     if c-1 >= 0:  # capture to the left
        #         if self.board[r+1][c-1][0] == 'w':  # enemy piece to capture
        #             if not piece_pinned or pin_direction == (1, -1):
        #                 moves.append(Move((r, c), (r+1, c-1), self.board))
        #     if c+1 <= 7:  # capture to the right
        #         if self.board[r+1][c+1][0] == 'w':  # enemy piece to capture
        #             if not piece_pinned or pin_direction == (1, 1):
        #                 moves.append(Move((r, c), (r+1, c+1), self.board))

    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                # can't remove queen from the pin on rook moves, only remove it on bishop moves
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        # up, left, down, right
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # still on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':  # empty space
                            moves.append(
                                Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # enemy piece
                            moves.append(
                                Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.white_to_move else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # either empty or enemy piece
                        moves.append(
                            Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diaganols
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # still on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':  # empty space
                            moves.append(
                                Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # enemy piece
                            moves.append(
                                Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # not an ally piece (empty or enemy piece)
                if end_piece[0] != ally_color:
                    # place king on end square and check for checks
                    if ally_color == 'w':
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(
                            Move((r, c), (end_row, end_col), self.board))
                    if ally_color == 'w':
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)

    def getCastleMoves(self, row, col, moves):
        '''
        Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
        '''
        if self.squareUnderAttack(row, col):
            return  # can't castle while in check
        if (self.white_to_move and self.current_castling_rights.wks) or (not self.white_to_move and self.current_castling_rights.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (not self.white_to_move and self.current_castling_rights.bqs):
            self.getQuennsideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row][col+1] == '--' and self.board[row][col+2] == '--':
            if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2):
                moves.append(Move((row, col), (row, col+2),
                                  self.board, is_castle_move=True))

    def getQuennsideCastleMoves(self, row, col, moves):
        if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and self.board[row][col-3] == '--':
            if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2):
                moves.append(Move((row, col), (row, col-2),
                                  self.board, is_castle_move=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


'''
Move class handles moves data and notation conversions.
'''


class Move():
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # pawn promotion
        self.is_pawn_promotion = (self.piece_moved == "wP" and self.end_row == 0) or (
            self.piece_moved == "bP" and self.end_row == 7)
        # en passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"
        # castle move
        self.is_castle_move = is_castle_move

        self.move_id = (self.start_row * 1000) + (self.start_col *
                                                  100) + (self.end_row * 10) + (self.end_col)

    '''
    Overriding the = sign 
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        output_string = ""
        if self.is_pawn_promotion:
            output_string += self.get_rank_file(self.end_row,
                                                self.end_col) + "Q"
        if self.is_castle_move:
            if self.end_col == 1:
                output_string += "0-0-0"
            else:
                output_string += "0-0"
        if self.is_enpassant_move:
            output_string += self.get_rank_file(self.start_row, self.start_col)[
                0] + "x" + self.get_rank_file(self.end_row, self.end_col) + " e.p."
        if self.piece_captured != "--":
            if self.piece_moved[1] == "p":
                output_string += self.get_rank_file(self.start_row, self.start_col)[
                    0] + "x" + self.get_rank_file(self.end_row, self.end_col)
            else:
                output_string += self.piece_moved[1] + "x" + \
                    self.get_rank_file(self.end_row, self.end_col)
        else:
            if self.piece_moved[1] == "p":
                output_string += self.get_rank_file(self.end_row, self.end_col)
            else:
                output_string += self.piece_moved[1] + \
                    self.get_rank_file(self.end_row, self.end_col)

        return output_string

        # TODO
        # Disambiguating moves

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
