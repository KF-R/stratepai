import random, os, re
board = [0] * 100
board[42], board[43], board[52], board[53], board[46], board[47], board[56], board[57] = [255] * 8 # Lakes

TEAM_RED, TEAM_BLUE = 0, 1 
P_FLAG = 1; P_SPY = 2; P_SCOUT = 3; P_MINER = 4; P_MARSHALL = 11; P_BOMB = 12 # Pieces with special rules
PIECE_CHAR = ['', '@', 'S', '1', 'm', '3', '4', '5', '6', 'C', 'G', 'M', 'o'] # ASCII piece representation unicode: @Ⓢ①ⓜ③④⑤⑥ⒸⒼⓂⓞ, @🅢𝟏🅜𝟑𝟒𝟓𝟔🅒🅖🅜🅞
PIECE_NAME = ['', 'Flag', 'Spy', 'Scout', 'Miner', 'Sergeant', 'Lieutenant', 'Captain', 'Major', 'Colonel', 'General', 'Marshall', 'Bomb']
TEAM_NAME = ['Red', 'Blue']
PIECE_DISTRIBUTIONS = [0, 1, 1, 8, 5, 4, 4, 4, 3, 2, 1, 1, 6]
PIECE_LIMIT = len(PIECE_CHAR) + 1
ANSI = {'black': "\u001b[30m", 'red': "\u001b[31m", 'green': "\u001b[32m", 'yellow': "\u001b[33m", 'blue': "\u001b[34m", 'magenta': "\u001b[35m", 'cyan': "\u001b[36m", 'white': "\u001b[37m", 'default': "\u001b[0m"}
LOG_WIDTH = 48
LOG_SIDE, LOG_TOP, LOG_BOTTOM = "|", f".{(' Log '.center(LOG_WIDTH - 2,'-'))}.", f"'{('-' * (LOG_WIDTH - 2))}'"

turn, activePlayer, setupPhase, victory, selection, target, messageText, log = 0, TEAM_RED, True, False, None, None, '', []

def log_action(logMessage: str = ''):
    if logMessage: log.append(logMessage)

def piece_char(piece_value: int = 0) -> str:
    return ANSI['red'] + PIECE_CHAR[piece_value] + ANSI['default'] if piece_value < PIECE_LIMIT else ANSI['cyan'] + PIECE_CHAR[piece_value - PIECE_LIMIT] + ANSI['default'] 

def piece_name(piece_value: int = 0) -> str:
    return ANSI['red'] + PIECE_NAME[piece_value] + ANSI['default'] if piece_value < PIECE_LIMIT else ANSI['cyan'] + PIECE_NAME[piece_value - PIECE_LIMIT] + ANSI['default'] 

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

    if empty_spaces: # Check if there are any zeros to replace
        
        replace_index = random.choice(empty_spaces) # Randomly select one 
        board_rows[replace_index] = piece_value # Replace with the piece 

        # Update the board with the modified rows
        board[row_start:row_end] = board_rows

def setup_pieces(side: int = 1):  # side 0: top, red, <= PIECE_LIMIT  side 1: bottom, blue, > PIECE_LIMIT 
    global board
    
    # Place flag
    set_piece(side * 9, 1 + (side * PIECE_LIMIT))
    
    # Place bombs 
    numBombs = PIECE_DISTRIBUTIONS[P_BOMB]
    while numBombs > 0:
        set_piece(side * 6, P_BOMB + (side * PIECE_LIMIT) , 4)
        numBombs -= 1

    # Place other pieces
    piece_value = 11
    while piece_value > 1:
        numPieces = PIECE_DISTRIBUTIONS[piece_value]
        while numPieces >= 1:
            set_piece(side * 6, piece_value + (side * PIECE_LIMIT) , 4)
            numPieces -= 1  
        piece_value -= 1

    return

def strip_ANSI(line):
    escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return escape.sub('', line)

def print_board():
    os.system("clear")

    print(ANSI['default'] + "   " + "  ".join(str(i) for i in range(0, 10)) + f" {LOG_TOP}")
    for i in range(0, len(board), 10):
        outputRow = f"{i // 10} " + ANSI['black']
        row = board[i:i+10]
        for c, char in enumerate(row):
            if char == 255:
                outputRow += ANSI['blue'] + '~~~'
            elif char == 0:
                outputRow += ANSI['black'] + ' . '
            else:  
                if char > PIECE_LIMIT: 
                    char = char - PIECE_LIMIT
                    side = TEAM_BLUE
                    outputRow += ANSI['cyan'] 
                    if activePlayer == TEAM_RED:
                        outputRow += f" # "
                    else:
                        outputRow += f" {PIECE_CHAR[char]} "

                else:
                    side = TEAM_RED
                    outputRow += ANSI['red']
                    if activePlayer == TEAM_BLUE:
                        outputRow += f" # "
                    else:
                        outputRow += f" {PIECE_CHAR[char]} "

        fillerLength = 0
        logSection = log[-10:]
        if len(log) > i // 10: 
            logLine = logSection[i // 10]
            trueLength = len(strip_ANSI(logLine))
            fillerLength = LOG_WIDTH - trueLength - 2

        else: logLine = ' ' * (LOG_WIDTH - 2)
        print(f"{outputRow}" + ANSI['default'] + f"{LOG_SIDE}{logLine}{' ' * fillerLength}{LOG_SIDE}" )

    if setupPhase: print('  ' + ANSI['yellow'] + f" Setup Phase ".center(29,'-') + ANSI['default'] + f" {LOG_BOTTOM}")
    else: print('  ' + ANSI['green'] + f"{turn}".center(29,'-') + ANSI['default'] + f" {LOG_BOTTOM}")
    if messageText: print(' ' + ANSI['white'] + messageText + ANSI['default'])
    elif selection == None: print()

def is_friendly(subject_piece_value, target_piece_value) -> bool:
    return (subject_piece_value > PIECE_LIMIT) == (target_piece_value >= PIECE_LIMIT)

def get_valid_moves(selection: int) -> list:

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
    global selection, activePlayer, setupPhase, messageText
    messageText = '' # Used for input feedback
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
            messageText = f"{ANSI['yellow']}Invalid input. Please enter a single digit, a space, then another single digit." + ANSI['default'] + ' (Q to quit, ENTER to cancel or continue)'
            
            return None

def get_coords(position: int) -> tuple:
    y, x = divmod(position, 10)
    return (x, y)

def resolve_conflict(attacker_position: int, defender_position: int ) -> int:
    global victory
    attacker, defender = board[attacker_position], board[defender_position]
    if defender == 0:
        attackTeam = ANSI['red'] + TEAM_NAME[TEAM_RED] + ANSI['default'] if attacker <= PIECE_LIMIT else ANSI['cyan'] + TEAM_NAME[TEAM_BLUE] + ANSI['default']
        log_action(f"{attackTeam} piece has moved from {positions_to_string([get_coords(attacker_position)])} to {positions_to_string([get_coords(defender_position)])}") 
        return attacker
    attacker_strength, defender_strength = attacker % PIECE_LIMIT, defender % PIECE_LIMIT # Blue pieces are > PIECE_LIMIT
    if defender_strength == P_FLAG:
        print(f"Player {activePlayer} wins!") 
        victory = True
        return attacker
    elif defender_strength == P_BOMB and attacker_strength == P_MINER: 
        log_action(f"{piece_name(attacker)} defused {piece_name(defender)} at {positions_to_string([get_coords(defender_position)])}") 
        return attacker # piece_name(defender) destroyed
    elif defender_strength == P_MARSHALL and attacker_strength == P_SPY:
        log_action(f"{piece_name(attacker)} assassinated {piece_name(defender)} at {positions_to_string([get_coords(defender_position)])}") 
        return attacker # piece_name(defender) destroyed
    elif defender_strength == attacker_strength: 
        log_action(f"{piece_name(attacker)} and {piece_name(defender)} destroyed at {positions_to_string([get_coords(defender_position)])}") 
        return 0 # piece_name(attacker) and piece_name(defender) destroyed
    elif defender_strength < attacker_strength: 
        log_action(f"{piece_name(attacker)} destroyed {piece_name(defender)} at {positions_to_string([get_coords(defender_position)])}") 
        return attacker # piece_name(defender) destroyed
    else:
        log_action(f"{piece_name(defender)} defeated {piece_name(attacker)} attack from {positions_to_string([get_coords(attacker_position)])}") 
        return defender # piece_name(attacker) destroyed

def no_valid_moves_check():
    for i in range(0, len(board)):
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

def positions_to_string(tuple_list) -> str:
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
        prompt += ' Select a piece to swap (x y): ' + ANSI['default']
        selection = validated_input(prompt)
        if not selection == None:
            if board[selection] == 0:
                messageText = "That is not a valid piece."
                selection = None 
            elif (activePlayer > 0 and board[selection] <= PIECE_LIMIT) or (activePlayer == 0 and board[selection] > PIECE_LIMIT):
                messageText = f"That is not your piece."
                selection = None
        else: # Valid input but no selection; ending turn
            break

        print_board()

    # Piece selected, need target to swap with
    if not selection == None:
        print(f" Selected: {piece_char(board[selection])}")

        while target == None:
            prompt = ANSI['red'] if activePlayer == TEAM_RED else ANSI['cyan']
            prompt += ' Select a target position to swap with (x y): ' + ANSI['default']
            target = validated_input(prompt)
            if not target == None:
                if board[target] == 0:
                    messageText = "Not a valid target position."
                    target = None 
                elif (activePlayer > 0 and board[target] <= PIECE_LIMIT) or (activePlayer == 0 and board[target] > PIECE_LIMIT):
                    messageText = "That is not your piece."
                    target = None

            print_board()
        
        swapPiece = board[selection]
        board[selection] = board[target]
        board[target] = swapPiece
        selection, target = None, None

# Setup complete, taking turns until flag exposed
while not victory:

    if activePlayer == TEAM_RED: turn += 1
    print_board()

    # Players can lose if none of their pieces can move
    if no_valid_moves_check():
        print(f"{TEAM_NAME[activePlayer]} is unable to move.")
        activePlayer = activePlayer ^ 1
        print(f"{TEAM_NAME[activePlayer]} wins!")
        victory = True
        continue

    # Loop until valid piece successfully selected
    while selection == None:
        prompt = ANSI['red'] if activePlayer == TEAM_RED else ANSI['cyan']
        prompt += ' Select a piece to move (x y): ' + ANSI['default']
        selection = validated_input(prompt)
        if not selection == None:
            if (activePlayer > 0 and board[selection] <= PIECE_LIMIT) or (activePlayer == 0 and board[selection] > PIECE_LIMIT):
                messageText = f"That is not your piece."
                selection = None
            else:
                valid_destinations = get_valid_moves(selection)
                if len(valid_destinations) == 0:
                    selection = None
                    
        print_board()            

    # Piece selected, need valid move destination
    if not selection == None:
        yx_coords = [divmod(position, 10) for position in valid_destinations]
        xy_coords = [(x, y) for y, x in yx_coords]

        print(f" Selected: {piece_name(board[selection])}  Moves: {positions_to_string(xy_coords)}")

        while target == None:
            prompt = ANSI['red'] if activePlayer == TEAM_RED else ANSI['cyan']
            prompt += ' Select a valid move (x y): ' + ANSI['default']
            target = validated_input(prompt)
            if not target == None:
                
                if target in valid_destinations:

                    winner = resolve_conflict(selection, target)

                    board[target] = winner
                    board[selection] = 0

                    selection, target = None, None
                    activePlayer = activePlayer ^ 1 # XOR to flip player turns
                    break

                else:
                    print(f"That is not a valid move.")
                    target = None

print('Bye!')
