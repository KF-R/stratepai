import random, os
board = [0] * 100
board[42], board[43], board[52], board[53], board[46], board[47], board[56], board[57] = [255] * 8 # Lakes

TEAM_RED, TEAM_BLUE = 0, 1 
P_FLAG = 1; P_SPY = 2; P_SCOUT = 3; P_MINER = 4; P_MARSHALL = 11; P_BOMB = 12 # Pieces with special rules
pieceChar = ['', '@', 'S', '1', 'm', '3', '4', '5', '6', 'C', 'G', 'M', 'o'] # ASCII piece representation
pieceName = ['', 'Flag', 'Spy', 'Scout', 'Miner', 'Sergeant', 'Lieutenant', 'Captain', 'Major', 'Colonel', 'General', 'Marshall', 'Bomb']
teamName = ['Red', 'Blue']
pieceDistribtions = [0, 1, 1, 8, 5, 4, 4, 4, 3, 2, 1, 1, 6]
PIECE_LIMIT = len(pieceChar) + 1
ANSI = {'black': "\u001b[30m", 'red': "\u001b[31m", 'green': "\u001b[32m", 'yellow': "\u001b[33m", 'blue': "\u001b[34m", 'magenta': "\u001b[35m", 'cyan': "\u001b[36m", 'white': "\u001b[37m", 'default': "\u001b[0m"}

activePlayer, setupPhase, victory = TEAM_RED, True, False
selection, target = None, None

def piece_char(piece_value: int = 0):
    return ANSI['red'] + pieceChar[piece_value] + ANSI['default'] if piece_value < PIECE_LIMIT else ANSI['cyan'] + pieceChar[piece_value - PIECE_LIMIT] + ANSI['default'] 

def piece_name(piece_value: int = 0):
    return ANSI['red'] + pieceName[piece_value] + ANSI['default'] if piece_value < PIECE_LIMIT else ANSI['cyan'] + pieceName[piece_value - PIECE_LIMIT] + ANSI['default'] 

def set_piece(row: int = 0, piece_value:int = 0, numRows:int = 1):
    """
    Replace a random zero in the specified row or subsequent rows of the board with the given piece value.
    
    :param row: The starting row number where the piece can be placed.
    :param piece_value: The piece value to place (between 1 and 12).
    :param numRows: The number of rows to consider for placing the piece, starting from 'row'.
    """
    global board

    # The board is 10x10
    row_start = row * 10
    row_end = row_start + 10 * numRows

    # Extract the specific rows
    board_rows = board[row_start:row_end]

    # Find all indices of zeros in the rows
    empty_spaces = [i for i, x in enumerate(board_rows) if x == 0]

    # Check if there are any zeros to replace
    if empty_spaces:
        # Randomly select one of these indices
        replace_index = random.choice(empty_spaces)

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
    os.system("clear")
    print(ANSI['default'] + "   " + "  ".join(str(i) for i in range(0, 10)))
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

    # if setupPhase: print(f" {ANSI['green']}Setup Phase{ANSI['default']} ".center(20,'-'))
    if setupPhase: print('  ' + ANSI['yellow'] + f" Setup Phase ".center(29,'-'))
    else: print('  ' + ANSI['green'] + "".center(29,'-'))

def is_friendly(subject_piece_value, target_piece_value):
    return (subject_piece_value > PIECE_LIMIT) == (target_piece_value >= PIECE_LIMIT)

def get_valid_moves(selection: int):

    def follow_line_to_obstacle(line):
        result = []
        for position in line:
            obstruction = board[position]
            if obstruction == 0: # Empty space
                result.append(position)
            elif obstruction == 255: # Physical obstacle i.e. Lake
                break
            elif is_friendly(board[selection], board[position]): # Obstacle is friendly piece
                break
            else: # Obstacle is an opponent piece
                result.append(position)
                break
        
        return result

    if board[selection] == 0 or board[selection] == 255: return []
    row, col = divmod(selection, 10)
    
    piece = board[selection] % PIECE_LIMIT # Blue pieces are >= PIECE_LIMIT
    if piece in [P_BOMB, P_FLAG]: # Static piece
        return []
    elif piece  == P_SCOUT:
        n = 9
    else:
        n = 1

    north = follow_line_to_obstacle([selection - 10 * i for i in range(1, n + 1) if row - i >= 0])
    east = follow_line_to_obstacle([selection + i for i in range(1, n + 1) if col + i < 10])
    south = follow_line_to_obstacle([selection + 10 * i for i in range(1, n + 1) if row + i < 10])
    west = follow_line_to_obstacle([selection - i for i in range(1, n + 1) if col - i >= 0])

    return north + east + south + west

def validated_input(prompt:str = '> ') -> int:
    global selection, activePlayer, setupPhase

    while True:
        user_input = input(prompt)
        if user_input == '': # End turn if nothing selected; otherwise cancel selection
            if not selection:
                 # No selection so not cancelling a swap or move 
                if setupPhase:
                    if activePlayer == TEAM_BLUE:
                        activePlayer = TEAM_RED
                        setupPhase = False
                    else:
                        activePlayer = TEAM_BLUE
                    
            selection = None
            target = None
            return None
        elif user_input.upper() == 'Q':
            print('Bye!')
            exit()

        # Moving on to expected coordinate pairs: Split the input based on space
        parts = user_input.split()
        # Check if there are exactly two parts and each part is a single digit
        if len(parts) == 2 and all(part.isdigit() and len(part) == 1 for part in parts):
            x, y = int(parts[0]), int(parts[1])
            return (y * 10) + x
        else:
            print(f"{ANSI['yellow']}Invalid input. Please enter a single digit, a space, then another single digit." + ANSI['default'] + ' (Q to quit, ENTER to cancel or continue)')
            return None

def resolve_conflict(attacker: int, defender: int ):
    global victory
    if defender == 0: return attacker
    attacker_strength, defender_strength = attacker % PIECE_LIMIT, defender % PIECE_LIMIT # Blue pieces are > PIECE_LIMIT
    if defender_strength == P_FLAG:
        print(f"Player {activePlayer} wins!") 
        victory = True
        return attacker
    elif defender_strength == P_BOMB and attacker_strength == P_MINER: return attacker # piece_name(defender) destroyed
    elif defender_strength == P_MARSHALL and attacker_strength == P_SPY: return attacker # piece_name(defender) destroyed
    elif defender_strength == attacker_strength: return 0 # piece_name(attacker) and piece_name(defender) destroyed
    elif defender_strength < attacker_strength: return attacker # piece_name(defender) destroyed
    else: return defender # piece_name(attacker) destroyed

def no_valid_moves_check():
    for i in range(0, len(board)):
        # print(piece_name(board[i]))
        if board[i] == 0 or board[i] == 255: continue
        if activePlayer == TEAM_RED:
            if board[i] <= PIECE_LIMIT: # Red piece
                if len(get_valid_moves(i)) > 0: # print(f"valid red move found at {i}")
                    return False
        else: # TEAM_BLUE
            if board[i] > PIECE_LIMIT: # Blue piece
                if len(get_valid_moves(i)) > 0: # print(f"valid blue move found at {i}")
                    return False

    return True

def positions_to_string(tuple_list):
    result = ""
    for tpl in tuple_list: result += f"{tpl[0]} {tpl[1]}, "
    return result[:-2] # Last two characters (, ) removed from list

# Automatically set up player pieces
setup_pieces(TEAM_RED)
setup_pieces(TEAM_BLUE)

# Players can rearrange pieces
while setupPhase:

    print_board()

    # Loop until valid piece successfully selected
    while selection == None:
        prompt = ANSI['red'] if activePlayer == TEAM_RED else ANSI['cyan']
        prompt += 'Select a piece to swap (x y): ' + ANSI['default']
        selection = validated_input(prompt)
        if not selection == None:
            if (activePlayer > 0 and board[selection] <= PIECE_LIMIT) or (activePlayer == 0 and board[selection] > PIECE_LIMIT):
                print(f"That is not your piece ({piece_char(board[selection])})")
                selection = None
        else: # Valid input but no selection; ending turn
            break

    # Piece selected, need target to swap with
    if not selection == None:
        print(f"Selected: {piece_char(board[selection])}")

        while target == None:
            prompt = ANSI['red'] if activePlayer == TEAM_RED else ANSI['cyan']
            prompt += 'Select a target position to swap with (x y): ' + ANSI['default']
            target = validated_input(prompt)
            if not target == None:
                if board[target] == 0:
                    print(f"Not a valid target position.")
                    target = None 
                elif (activePlayer > 0 and board[target] <= PIECE_LIMIT) or (activePlayer == 0 and board[target] > PIECE_LIMIT):
                    print(f"That is not your piece ({piece_char(board[target])})")
                    target = None
        
        print(f"Target: {piece_char(board[target])}")

        swapPiece = board[selection]
        board[selection] = board[target]
        board[target] = swapPiece
        selection, target = None, None

# Setup complete, taking turns until flag exposed
while not victory:

    print_board()

    # Players can lose if none of their pieces can move
    if no_valid_moves_check():
        print(f"{teamName[activePlayer]} is unable to move.")
        activePlayer = activePlayer ^ 1
        print(f"{teamName[activePlayer]} wins!")
        victory = True
        continue

    # Loop until valid piece successfully selected
    while selection == None:
        prompt = ANSI['red'] if activePlayer == TEAM_RED else ANSI['cyan']
        prompt += 'Select a piece to move (x y): ' + ANSI['default']
        selection = validated_input(prompt)
        if not selection == None:
            if (activePlayer > 0 and board[selection] <= PIECE_LIMIT) or (activePlayer == 0 and board[selection] > PIECE_LIMIT):
                print(f"That is not your piece ({piece_char(board[selection])})")
                selection = None
            else:
                valid_destinations = get_valid_moves(selection)
                if len(valid_destinations) == 0:
                    print(f"No valid moves ({piece_char(board[selection])})")
                    selection = None
                    
        else: # Valid input but no selection; ending turn
            break

    # Piece selected, need valid move destination
    if not selection == None:
        yx_coords = [divmod(position, 10) for position in valid_destinations]
        xy_coords = [(x, y) for y, x in yx_coords]

        print(f"Selected: {piece_name(board[selection])}  Moves: {positions_to_string(xy_coords)}")

        while target == None:
            prompt = ANSI['red'] if activePlayer == TEAM_RED else ANSI['cyan']
            prompt += 'Select a valid move (x y): ' + ANSI['default']
            target = validated_input(prompt)
            if not target == None:
                
                if target in valid_destinations:

                    winner = resolve_conflict(board[selection], board[target])

                    board[target] = winner
                    board[selection] = 0

                    selection, target = None, None
                    activePlayer = activePlayer ^ 1 # XOR to flip player turns
                    break

                else:
                    print(f"That is not a valid move.")
                    target = None

print('Bye!')
