import random
board = [0] * 100
board[42], board[43], board[52], board[53], board[46], board[47], board[56], board[57] = [255] * 8 # Lakes

TEAM_RED, TEAM_BLUE = 0, 1 
P_FLAG = 1; P_SPY = 2; P_SCOUT = 3; P_MINER = 4; P_MARSHALL = 11; P_BOMB = 12
pieceChar = ['', '@', 'S', '1', 'm', '3', '4', '5', '6', 'C', 'G', 'M', 'o']
pieceNames = ['', 'Flag', 'Spy', 'Scout', 'Miner', 'Sergeant', 'Lieutenant', 'Captain', 'Major', 'Colonel', 'General', 'Marshall', 'Bomb']
pieceDistribtions = [0, 1, 1, 8, 5, 4, 4, 4, 3, 2, 1, 1, 6]
PIECE_LIMIT = len(pieceChar) + 1
ANSI = {
    'black': "\u001b[30m",
    'red': "\u001b[31m",
    'green': "\u001b[32m",
    'yellow': "\u001b[33m",
    'blue': "\u001b[34m",
    'magenta': "\u001b[35m",
    'cyan': "\u001b[36m",
    'white': "\u001b[37m",
    'default': "\u001b[0m"}

activePlayer, setupPhase, victory = TEAM_RED, True, False


def describe_piece_distribution():
    for i in range(1,len(pieceChar)):
        print(f"{pieceDistribtions[i]} x {pieceNames[i]} ({pieceChar[i]})")


def set_piece(row: int = 0, piece_value:int = 0, numRows:int = 1):
    global board
    """
    Replace a random zero in the specified row or subsequent rows of the board with the given piece value.
    
    :param row: The starting row number where the piece can be placed.
    :param piece_value: The piece value to place (between 1 and 12).
    :param numRows: The number of rows to consider for placing the piece, starting from 'row'.
    """
    # Assuming the board is 10x10
    row_start = row * 10
    row_end = row_start + 10 * numRows

    # Extract the specific rows
    board_rows = board[row_start:row_end]

    # Find all indices of zeros in the rows
    zero_indices = [i for i, x in enumerate(board_rows) if x == 0]

    # Check if there are any zeros to replace
    if zero_indices:
        # Randomly select one of these indices
        replace_index = random.choice(zero_indices)

        # Replace the zero with the piece value
        board_rows[replace_index] = piece_value

        # Update the board with the modified rows
        board[row_start:row_end] = board_rows


def setup_pieces(side: int = 1):  # side 0: top, red, <= PIECE_LIMIT  side 1: bottom, blue, > PIECE_LIMIT 
    global board
    
    # Place flag
    set_piece(side * 9, 1 + (side * PIECE_LIMIT))
    
    # Place bombs 
    numBombs = pieceDistribtions[P_BOMB]
    while numBombs > 0:
        set_piece(side * 6, P_BOMB + (side * PIECE_LIMIT) , 4)
        numBombs -= 1

    # Place other pieces
    piece_value = 11
    while piece_value > 1:
        numPieces = pieceDistribtions[piece_value]
        while numPieces >= 1:
            set_piece(side * 6, piece_value + (side * PIECE_LIMIT) , 4)
            numPieces -= 1  
        piece_value -= 1

    return
    

def print_board():
    print("   " + "  ".join(str(i) for i in range(0, 10)))
    for i in range(0, len(board), 10):
        outputRow = f"{i // 10} " + ANSI['black']
        row = board[i:i+10]
        for char in row:
            if char == 255:
                outputRow += ANSI['blue'] + '~~~'
            elif char == 0:
                outputRow += ANSI['black'] + ' . '
            else:  
                if char > PIECE_LIMIT: 
                    char = char - PIECE_LIMIT
                    side = 1
                    outputRow += ANSI['cyan']
                else:
                    side = 0
                    outputRow += ANSI['red']
                outputRow += f" {pieceChar[char]} "
        
        print(f"{outputRow}" + ANSI['default'])

    print(ANSI['default'])


# Automatically set up player pieces
setup_pieces(TEAM_RED)
setup_pieces(TEAM_BLUE)

# Allow player to swap pieces around until they're happy
while setupPhase:
    print_board()
    setupPhase = False
    # Red setup loop
    # Blue setup loop


# while not victory:
#     # Get red player move
#     # Get blue player move

