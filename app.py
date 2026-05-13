from flask import Flask, render_template, request, jsonify
import chess
import random

app = Flask(__name__)

board = chess.Board()

difficulty = "easy"

# Piece values
piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}


# Evaluate board
def evaluate_board(board):

    score = 0

    for piece_type in piece_values:

        score += len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

        score -= len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]

    return score


# Easy AI
def easy_ai():

    legal_moves = list(board.legal_moves)

    move = random.choice(legal_moves)

    board.push(move)


# Intermediate AI
def intermediate_ai():

    best_move = None
    best_score = -9999

    legal_moves = list(board.legal_moves)

    for move in legal_moves:

        board.push(move)

        score = evaluate_board(board)

        if board.is_check():
            score += 2

        center_squares = [
            chess.D4,
            chess.D5,
            chess.E4,
            chess.E5
        ]

        if move.to_square in center_squares:
            score += 1

        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

    if best_move:
        board.push(best_move)


# Hard AI using minimax
def minimax(board, depth, maximizing):

    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)

    if maximizing:

        max_eval = -9999

        for move in legal_moves:

            board.push(move)

            eval = minimax(board, depth - 1, False)

            board.pop()

            max_eval = max(max_eval, eval)

        return max_eval

    else:

        min_eval = 9999

        for move in legal_moves:

            board.push(move)

            eval = minimax(board, depth - 1, True)

            board.pop()

            min_eval = min(min_eval, eval)

        return min_eval


# Hard AI
def hard_ai():

    best_move = None
    best_score = -9999

    legal_moves = list(board.legal_moves)

    for move in legal_moves:

        board.push(move)

        score = minimax(board, 2, False)

        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

    if best_move:
        board.push(best_move)


# AI controller
def ai_move():

    global difficulty

    if difficulty == "easy":
        easy_ai()

    elif difficulty == "intermediate":
        intermediate_ai()

    else:
        hard_ai()


@app.route("/")
def home():

    return render_template(
        "index.html",
        fen=board.fen(),
        difficulty=difficulty
    )


@app.route("/set_difficulty", methods=["POST"])
def set_difficulty():

    global difficulty

    data = request.json

    difficulty = data["difficulty"]

    return jsonify({
        "status": "ok"
    })


@app.route("/move", methods=["POST"])
def move():

    data = request.json

    move = data["move"]

    try:

        chess_move = chess.Move.from_uci(move)

        if chess_move in board.legal_moves:

            board.push(chess_move)

            # AI move
            if not board.is_game_over():
                ai_move()

            result = None

            # Game result
            if board.is_checkmate():

                if board.turn:
                    result = "🎉 White Wins by Checkmate!"
                else:
                    result = "🤖 AI Wins by Checkmate!"

            elif board.is_stalemate():

                result = "🤝 Draw by Stalemate!"

            elif board.is_insufficient_material():

                result = "🤝 Draw by Insufficient Material!"

            return jsonify({
                "status": "ok",
                "fen": board.fen(),
                "result": result
            })

    except:
        pass

    return jsonify({
        "status": "error"
    })


@app.route("/reset")
def reset():

    global board

    board = chess.Board()

    return jsonify({
        "fen": board.fen()
    })


if __name__ == "__main__":
    app.run(debug=True)
