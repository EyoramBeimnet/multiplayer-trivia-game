import json

VERSION = 1

# Message types
JOIN = "JOIN"
JOIN_ACK = "JOIN_ACK"
PLAYERS = "PLAYERS"
START_GAME = "START_GAME"
START = "START"
QUESTION = "QUESTION"
ANSWER = "ANSWER"
QUESTION_END = "QUESTION_END"
SCORE = "SCORE"
FINAL = "FINAL"
LEAVE = "LEAVE"
ERROR = "ERROR"

# Error codes
ERR_BAD_JSON = 1
ERR_BAD_MESSAGE = 2
ERR_VERSION = 3
ERR_WRONG_ROOM = 4
ERR_NAME_TAKEN = 5
ERR_ROOM_FULL = 6
ERR_IN_PROGRESS = 7
ERR_TOO_LATE = 8
ERR_DUPLICATE = 9
ERR_NOT_HOST = 10
ERR_BAD_STATE = 11


# ---- Builders: one per message, so field names live in one place ----

def make(type_, **fields) -> dict:
    return {"v": VERSION, "type": type_, **fields}

def make_join(room, name):
    # client -> server
    return make(JOIN, room=room, name=name)

def make_join_ack(is_host: bool):
    # server -> client
    return make(JOIN_ACK, is_host=is_host)

def make_players(players: list[str], host: str):
    # server -> all
    return make(PLAYERS, players=players, host=host)

def make_start_game():
    # host client -> server
    return make(START_GAME)

def make_start(total_questions: int):
    # server -> all
    return make(START, total_questions=total_questions)

def make_question(number: int, text: str, choices: list[str], duration: int):
    # Note: Duration is in seconds
    # server -> all
    return make(QUESTION, number=number, text=text, choices=choices, duration=duration)

def make_question_end(number: int, correct: int, counts: list[int], your_choice, points: int):
    # counts: the distribution of what other people picked per answer index
    # correct: answer index of the correct choice
    # server -> each client
    return make(QUESTION_END, correct=correct, counts=counts, your_choice=your_choice, points=points)

def make_answer(number: int, choice: int): 
    # client -> server
    return make(ANSWER, number=number, choice=choice)

def make_score(scores: list[dict]):
    # server -> all
    # reminder to sort list by value
    # dict = {name: score}
    return make(SCORE, scores=scores)

def make_final(scores: list[dict]):
    # server -> all
    return make(FINAL, scores=scores)

def make_error(code: int, message: str):
    # client -> server
    return make(ERROR, code=code, message=message)


# Framing

def send_msg(sock, msg):
    # TODO: json.dumps (compact), add "\n", encode, sendall
    return NotImplementedError

def read_msgs(sock):
    # TODO: revc into a buffer, split on b"\n", json.loads each line, yield
    # Think about: what should happen on bad JSON? (ERR_BAD_JSON)
    return NotImplementedError


# ----- VALIDATION --------

REQUIRED = {
    JOIN: {"room": str, "name": str},
    ANSWER: {"number": int, "choice": int},
    ERROR: {"code": int, "message": str}
}

def validate(msg):
    # TODO: return None if ok, else an error code
    # Check in order: is it a dict, version matches, type known,
    # required fields present with the right types
    return NotImplementedError

