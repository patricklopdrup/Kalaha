import game
import easyAI


def eval(board):
    score = 0
    # AI wins
    if board[game.STORE_IDX[game.AI]] > board[game.STORE_IDX[game.USER]]:
        # print(
        # f"ai vinder: {board[game.STORE_IDX[game.AI]]} - {board[game.STORE_IDX[game.USER]]}")
        score += 10_000
        score += (board[game.STORE_IDX[game.AI]] -
                  board[game.STORE_IDX[game.USER]]) * 100
    # user wins
    if board[game.STORE_IDX[game.AI]] < board[game.STORE_IDX[game.USER]]:
        score -= 10_000
        score -= (board[game.STORE_IDX[game.USER]] -
                  board[game.STORE_IDX[game.AI]]) * 100
    # don't let the user steal from AI
    for house in game.HOUSE_LIST[game.USER]:
        if board[house] < 1:
            score -= (board[game.P[house][game.OPP]] * 1000)

    # if there is more stones on the user side we give minus point to AI
    user = 0
    ai = 0
    for house in game.HOUSE_LIST[game.USER]:
        user += board[house]
    for house in game.HOUSE_LIST[game.AI]:
        ai += board[house]
    if (user + ai) < 20:
        if user > ai:
            score -= (user - ai) * 1000

    return score


# For the game engine
human = game.KalahaHumanPlayer()
# The AI is just an automated "human"
m_ai = game.KalahaHumanPlayer()
kalaha = game.KalahaGame([human, m_ai])


def alpha_beta_search(ply):
    kalaha.nplayer = game.AI
    m_move = -1
    alpha = -float('inf')
    beta = float('inf')
    best_score = -float('inf')

    # copy beginning board
    kalaha.copy_board()
    legal_moves = kalaha.possible_moves()
    for move in legal_moves:
        if ply == 0:
            return eval(kalaha.board)

        kalaha.make_move(move)
        # AI is maximizing player. We switch to minimazing (human) before calling "min_value"
        kalaha.switch_player()
        s = min_value(ply-1, alpha, beta)
        # paste board that was copyed before for loop
        kalaha.paste_board()

        # Printing the score for each move
        print(f"s= {s} for move {move}")
        if s > best_score:
            m_move = move
            best_score = s

        alpha = max(best_score, alpha)

    kalaha.nplayer = game.AI
    # Printing the best score. That is the AI's move
    print(f"bestscore {best_score} at move {m_move}")
    return m_move

# For the maximizing player (AI). This is done in the "mind" of the AI.


def max_value(ply, alpha, beta):
    if kalaha.is_over():
        return eval(kalaha.board)

    # Worst score for maximizing player
    score = -float('inf')

    legal_moves = kalaha.possible_moves()
    for m in legal_moves:
        if ply == 0:
            return eval(kalaha.board)

        # save board before making move
        kalaha.save_board()
        # switch to minimizing player
        kalaha.switch_player()
        kalaha.make_move(m)
        score = max(score, min_value(ply-1, alpha, beta))
        kalaha.undo_move()

        # Prune subtree if possible
        if score >= beta:
            return score

        alpha = max(alpha, score)

    return score


# For the minimizing player (human). This is done in the "mind" of the AI.
def min_value(ply, alpha, beta):
    if kalaha.is_over():
        return eval(kalaha.board)

    # Worst score for minimizing player
    score = float('inf')

    legal_moves = kalaha.possible_moves()
    for m in legal_moves:
        if ply == 0:
            return eval(kalaha.board)

        # save board before making move
        kalaha.save_board()
        # switch to maximizing player
        kalaha.switch_player()
        kalaha.make_move(m)
        score = min(score, max_value(ply-1, alpha, beta))
        kalaha.undo_move()

        # Prune subtree if possible
        if score <= alpha:
            return score

        beta = min(beta, score)

    return score


# Print when game is over
def winner(board):
    if board[game.STORE_IDX[game.USER]] > board[game.STORE_IDX[game.AI]]:
        return "You win!"
    elif board[game.STORE_IDX[game.USER]] == board[game.STORE_IDX[game.AI]]:
        return "It's a draw!"
    else:
        return "You lose!"


# Driver code for the game
if __name__ == "__main__":

    # The search depth. Even number makes most sense, because it is plys (halv-moves)
    SEARCH_DEPTH = 6
    round = 0
    while not kalaha.is_over():
        round += 1
        kalaha.show()
        print(f"round: {round}")
        if kalaha.nplayer == game.USER:
            # The move from the human player
            move = int(input("Enter move:"))
            while move not in game.HOUSE_LIST[game.USER]:
                move = int(input("Enter legal move:"))
        else:
            # The move for the AI
            move = alpha_beta_search(SEARCH_DEPTH)
            print(f"\nAI moves: {move}\n")
        kalaha.play_move(move)
    # when game is over
    kalaha.show()
    print(winner(kalaha.board))
