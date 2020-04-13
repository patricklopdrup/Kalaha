import easyAI
import copy

USER = 1
AI = 2

PLAYER_LIST = [USER, AI]

# BOARD LAYOUT
#
#     13  12  11  10  09  08        AI
# 14                          07
#     01  02  03  04  05  06        USER
#
# HAND = 00

HOUSE_LIST = {
    USER: [1, 2, 3, 4, 5, 6],
    AI: [8, 9, 10, 11, 12, 13]
}

STORE_IDX = {
    USER: 7,
    AI: 14
}

HAND = 0

OWNER = 0
NEXT = 1
ROLE = 2
OPP = 3
DIST = 4

HOUSE = 88
STORE = 99

# Dictionary for easy lookup
P = {
    1: {OWNER: USER, NEXT: {USER:  2, AI:  2}, ROLE: HOUSE, OPP: 13, DIST: 6},
    2: {OWNER: USER, NEXT: {USER:  3, AI:  3}, ROLE: HOUSE, OPP: 12, DIST: 5},
    3: {OWNER: USER, NEXT: {USER:  4, AI:  4}, ROLE: HOUSE, OPP: 11, DIST: 4},
    4: {OWNER: USER, NEXT: {USER:  5, AI:  5}, ROLE: HOUSE, OPP: 10, DIST: 3},
    5: {OWNER: USER, NEXT: {USER:  6, AI:  6}, ROLE: HOUSE, OPP:  9, DIST: 2},
    6: {OWNER: USER, NEXT: {USER:  7, AI:  8}, ROLE: HOUSE, OPP:  8, DIST: 1},
    7: {OWNER: USER, NEXT: {USER:  8, AI:  8}, ROLE: STORE, OPP:  0, DIST: 0},
    8: {OWNER: AI, NEXT: {USER:  9, AI:  9}, ROLE: HOUSE, OPP:  6, DIST: 6},
    9: {OWNER: AI, NEXT: {USER: 10, AI: 10}, ROLE: HOUSE, OPP:  5, DIST: 5},
    10: {OWNER: AI, NEXT: {USER: 11, AI: 11}, ROLE: HOUSE, OPP:  4, DIST: 4},
    11: {OWNER: AI, NEXT: {USER: 12, AI: 12}, ROLE: HOUSE, OPP:  3, DIST: 3},
    12: {OWNER: AI, NEXT: {USER: 13, AI: 13}, ROLE: HOUSE, OPP:  2, DIST: 2},
    13: {OWNER: AI, NEXT: {USER:  1, AI: 14}, ROLE: HOUSE, OPP:  1, DIST: 1},
    14: {OWNER: AI, NEXT: {USER:  1, AI:  1}, ROLE: STORE, OPP:  0, DIST: 0}
}

ALL_PITS = range(1, 15)


class KalahaHumanPlayer(easyAI.Human_Player):
    pass


class KalahaGame(easyAI.TwoPlayersGame):

    def __init__(self, players):
        self.players = players
        self.nplayer = 1
        self.board = [0]*15

        self.seeds_per_house = 4
        self.reset_board()

        # For debug
        # self.board = [0,
        #               0, 0, 2, 0, 0, 1, 0,
        #               0, 4, 1, 0, 4, 0, 0]

        #     13  12  11  10  09  08        AI
        # 14                          07
        #     01  02  03  04  05  06        USER

        self.old_board = copy.deepcopy(self.board)
        self.board_copy = copy.deepcopy(self.board)

    def possible_moves(self):
        return self.possible_moves_choices()

    # A list of legal moves
    def possible_moves_choices(self):
        possible = []
        for house in HOUSE_LIST[self.nplayer]:
            if self.board[house] != 0:
                possible.append(house)
        #print(f"hej moves: {possible}")
        return possible

    def make_move(self, house):
        # self.old_board = self.board
        # scoop up from chosen house
        self._scoop(house)
        cur_house = house

        # drop seeds into the pits
        for i in range(self.board[HAND]):
            next_house = P[cur_house][NEXT][self.nplayer]
            self._drop(next_house)
            cur_house = next_house
        # steal if possible
        if self.board[cur_house] == 1:
            if P[cur_house][OWNER] == self.nplayer:
                if P[cur_house][ROLE] == HOUSE:
                    if self.board[P[cur_house][OPP]] > 0:
                        self._scoop(cur_house)
                        self._scoop(P[cur_house][OPP])
                        self._drop_all(STORE_IDX[self.nplayer])
        # when game is over - scoop own houses into own store
        if self.is_over():
            for player in PLAYER_LIST:
                for house in HOUSE_LIST[player]:
                    self._scoop(house)
                if self.board[HAND] > 0:
                    self._drop_all(STORE_IDX[player])
        # extra turn if last stone lands in your store
        # if the player does not get extra turn we save the board so we can undo moves
        # if P[cur_house][OWNER] == self.player:
            # if P[cur_house][ROLE] == STORE:
                # self.switch_player()

    def is_over(self):
        for player in PLAYER_LIST:
            has_seed = False
            for house in HOUSE_LIST[player]:
                if self.board[house] != 0:
                    has_seed = True
            if has_seed is False:
                return True
        return False

    def show(self):
        print(f"Player: {self.nplayer}")
        print("Board:\n")
        print("      13  12  11  10  09  08      AI")
        print("      ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ̅ ")
        print("      "+"  ".join(
            ["{:02d}".format(self.board[pit])
             for pit in reversed(HOUSE_LIST[AI])]
        ))
        print(" {:02d}                            {:02d}".format(
            self.board[STORE_IDX[AI]], self.board[STORE_IDX[USER]]
        ))
        print("      "+"  ".join(
            ["{:02d}".format(self.board[pit]) for pit in HOUSE_LIST[USER]]
        ))
        print("      ______________________")
        print("      01  02  03  04  05  06      USER")

    def reset_board(self):
        self.board[HAND] = 0
        for player in PLAYER_LIST:
            for house in HOUSE_LIST[player]:
                self.board[house] = self.seeds_per_house

    def undo_move(self):
        self.board = copy.deepcopy(self.old_board)

    def save_board(self):
        self.old_board = copy.deepcopy(self.board)

    def copy_board(self):
        self.board_copy = copy.deepcopy(self.board)

    def paste_board(self):
        self.board = copy.deepcopy(self.board_copy)

    def _scoop(self, pit):
        self.board[HAND] += self.board[pit]
        self.board[pit] = 0

    def _drop(self, pit, count=1):
        self.board[HAND] -= count
        self.board[pit] += count

    def _drop_all(self, pit):
        self.board[pit] += self.board[HAND]
        self.board[HAND] = 0

    # returning the house with most stones
    def ai_move(self):
        move = 0
        for house in HOUSE_LIST[AI]:
            if self.board[house] > self.board[move]:
                move = house
        return move

    def count_total_seeds(self):
        count = 0
        for seed in ALL_PITS:
            count += self.board[seed]
        return count
