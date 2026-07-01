ROWS, COLS = 3, 3

LEVELS = {
    'starter-1': {
        'board': ['+', '◊', 'X', '◻', ' ', 'O', '=', '∗', '▷'],
        'pawn_pos': 8,
        'orientation': [0, 0, 2, 1, 0, 3, 0, 0, 2]
    },
    'starter-2': {
        'board': ['=', '∗', 'X', '◻', ' ', '◊', 'O', '+', '▷'],
        'pawn_pos': 1,
        'orientation': [2, 3, 0, 0, 0, 0, 0, 2, 2]
    },
    'starter-3': {
        'board': ['X', '∗', '◻', '◊', 'O', '▷', '=', ' ', '+'],
        'pawn_pos': 1,
        'orientation': [2, 1, 3, 0, 3, 0, 0, 0, 1]
    },
    'starter-4': {
        'board': ['◻', '◊', 'O', '∗', 'X', '▷', ' ', '=', '+'],
        'pawn_pos': 3,
        'orientation': [1, 0, 2, 1, 0, 3, 0, 0, 0]
    },
    'junior-1': {
        'board': ['X', '▷', '∗', '=', '◻', '+', 'O', ' ', '◊'],
        'pawn_pos': 6,
        'orientation': [2, 1, 3, 2, 1, 1, 0, 0, 1]
    },
    'junior-2': {
        'board': ['+', '∗', 'X', '▷', ' ', '◊', 'O', '◻', '='],
        'pawn_pos': 5,
        'orientation': [0, 0, 1, 0, 0, 2, 0, 3, 1]
    },
    'junior-3': {
        'board': ['+', '=', '◻', '◊', '∗', 'X', ' ', '▷', 'O'],
        'pawn_pos': 5,
        'orientation': [1, 0, 2, 2, 0, 2, 0, 2, 1]
    },
    'junior-4': {
        'board': ['X', 'O', '+', '◻', ' ', '◊', '=', '∗', '▷'],
        'pawn_pos': 7,
        'orientation': [2, 0, 1, 1, 0, 0, 0, 0, 2]
    },
    'expert-1': {
        'board': ['◊', '◻', '+', 'X', '▷', '=', 'O', '∗', ' '],
        'pawn_pos': 0,
        'orientation': [1, 2, 3, 0, 2, 3, 3, 1, 0]
    },
    'expert-2': {
        'board': ['◻', '=', '◊', '+', '▷', 'X', ' ', 'O', '∗'],
        'pawn_pos': 4,
        'orientation': [2, 0, 1, 0, 2, 1, 0, 3, 3]
    },
    'expert-3': {
        'board': ['+', '=', ' ', '◻', 'O', '◊', '∗', 'X', '▷'],
        'pawn_pos': 5,
        'orientation': [1, 2, 0, 0, 1, 2, 0, 0, 2]
    },
    'expert-4': {
        'board': ['◻', '◊', '▷', '=', '∗', 'X', 'O', '+', ' '],
        'pawn_pos': 5,
        'orientation': [1, 0, 2, 0, 0, 2, 0, 1, 0]
    }
}

# Your exact original configurations from final.py
TILES_DEF = {
    "=": ({"I", "II"}, set(), False, False),
    "◻": ({"I", "II"}, set(), False, False),
    "+": ({"II", "IV"}, set(), False, False),
    "◊": ({"IV"}, {"II"}, True, True),
    "∗": ({"IV"}, {"II"}, True, True),
    "▷": (set(), {"I", "II"}, True, False),
    "X": (set(), {"I", "II"}, True, False),
    "O": (set(), {"I", "II"}, True, False),
    " ": (set(), set(), False, False),
}

ADJ_SIDES = {
    (-1, 0): ("I", "III"),
    (1, 0): ("III", "I"),
    (0, -1): ("IV", "II"),
    (0, 1): ("II", "IV"),
}