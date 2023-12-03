import random, os, re
from stratepai_openai import get_openAI_move
from setups import SETUPS
board = [0] * 100
board[42], board[43], board[52], board[53], board[46], board[47], board[56], board[57] = [255] * 8 # Lakes
STATE_FILE = "stratepai.state"
TEAM_RED, TEAM_BLUE = 0, 1 
P_FLAG = 1; P_SPY = 2; P_SCOUT = 3; P_MINER = 4; P_MARSHALL = 11; P_BOMB = 12 # Pieces with special rules
PIECE_CHAR, CONCEALED_CHAR = ['', '¶', 's', '¹', '²', '3', '4', '5', '6', '7', '8', '9', 'o'], '■' # ASCII piece representation
PIECE_NAME = ['', 'Flag', 'Spy', 'Scout', 'Miner', 'Sergeant', 'Lieutenant', 'Captain', 'Major', 'Colonel', 'General', 'Marshall', 'Bomb']
for n in range(1, len(PIECE_NAME)):
    PIECE_NAME[n] = f"{PIECE_NAME[n]} ({PIECE_CHAR[n]})"
TEAM_NAME = ['Red', 'Blue']
PIECE_DISTRIBUTIONS = [0, 1, 1, 8, 5, 4, 4, 4, 3, 2, 1, 1, 6]
PIECE_LIMIT = len(PIECE_CHAR) + 1
ANSI = {'black': "\u001b[30m", 'red': "\u001b[31m", 'green': "\u001b[32m", 'yellow': "\u001b[33m", 'blue': "\u001b[34m", 'magenta': "\u001b[35m", 'cyan': "\u001b[36m", 'white': "\u001b[37m", 'default': "\u001b[0m"}
LOG_WIDTH = 48
LOG_SIDE, LOG_TOP, LOG_BOTTOM = "|", f".{(' Log '.center(LOG_WIDTH - 2,'-'))}.", f"'{('-' * (LOG_WIDTH - 2))}'"

turn, activePlayer, setupPhase, victory, selection, target, messageText, log = 0, TEAM_RED, True, False, None, None, '', []
gameState, aiSuggestion, aiMove = '', '', []

WRITE_STATE = True
AI = True


def log_action(logMessage: str = ''):
    if logMessage: log.append(logMessage)

def piece_char(piece_value: int = 0) -> str:
    return ANSI['red'] + PIECE_CHAR[piece_value] + ANSI['default'] if piece_value < PIECE_LIMIT else ANSI['cyan'] + PIECE_CHAR[piece_value - PIECE_LIMIT] + ANSI['default'] 

def piece_name(piece_value: int = 0) -> str:
    return ANSI['red'] + PIECE_NAME[piece_value] + ANSI['default'] if piece_value < PIECE_LIMIT else ANSI['cyan'] + PIECE_NAME[piece_value - PIECE_LIMIT] + ANSI['default'] 

def setup_pieces(side: int = TEAM_RED):
    global board
    setup = random.choice(SETUPS)
    if side == TEAM_RED:
        for i in range(len(setup)): board[39-i] = PIECE_CHAR.index(setup[i])
    else:
        for i in range(len(setup)): board[i+60] = PIECE_CHAR.index(setup[i]) + PIECE_LIMIT

def strip_ANSI(line):
    escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return escape.sub('', line)

def summarise_state(fromSide: int = TEAM_RED):
    """ Writes the game state to a file """
    global gameState

    summaryLog = ['## Most recent moves:'] if len(log) > 0 else ['']
    for e, entry in enumerate(log):
        summaryLog.append( (f"Turn {(e // 2) + 1}:" if e % 2 == 0 else "       ") + entry.replace(ANSI['red'],'Red ').replace(ANSI['cyan'], 'Blue ').replace(ANSI['default'],'').replace('Red Red ', 'Red ').replace('Blue Blue ', 'Blue '))
    summary = "\n".join(summaryLog)

    boardState = [['  ', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9']]
    for i in range(0, len(board), 10):
        row = board[i:i+10]
        summaryRow = [f"r{i // 10}"]
        for char in row:
            if char == 0: summaryRow.append('..')
            elif char == 255: summaryRow.append('~~')
            else: summaryRow.append('B#' if char > PIECE_LIMIT else 'R' + PIECE_CHAR[char]) 
        boardState.append(summaryRow)

    gameState = ''
    moveable_pieces = []
    for i in range(0,100):
        if (board[i] > PIECE_LIMIT or board[i] == 0): continue
        valid_moves = get_valid_moves(i)
        if len(valid_moves) > 0: moveable_pieces.append({'position': i, 'valid_moves': valid_moves})

    gameState += "## Board State:\n"
    gameState += '\n'.join([', '.join(map(str, sublist)) for sublist in boardState]) + "\n\n"
    gameState += summary + "\n\n"
    gameState += "## Valid moves: \n"
    moves = ''
    for piece in moveable_pieces:
        name = PIECE_NAME[board[piece['position']] - PIECE_LIMIT]
        yx_coords = [divmod(position, 10) for position in piece['valid_moves']]
        xy_coords = [(x, y) for y, x in yx_coords]
        thisX = str(piece['position'])[1]
        thisY = str(piece['position'])[0]
        moves += f"{TEAM_NAME[TEAM_RED]} {name} at {thisX} {thisY} could move to{' any of' if len(piece['valid_moves']) > 1 else ''}: {positions_to_string(xy_coords)}\n"

    gameState += moves + "\n"

    if WRITE_STATE:
        with open(STATE_FILE, 'w', encoding='utf-8') as file:
            file.write(gameState)

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
                        outputRow += f" {CONCEALED_CHAR} " # #
                    else:
                        outputRow += f" {PIECE_CHAR[char]} " if selection != i + c else f"[{PIECE_CHAR[char]}]"

                else:
                    side = TEAM_RED
                    outputRow += ANSI['red']
                    if activePlayer == TEAM_BLUE:
                        outputRow += f" {CONCEALED_CHAR} " # #
                    else:
                        outputRow += f" {PIECE_CHAR[char]} " if selection != i + c else f"[{PIECE_CHAR[char]}]"

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
        if user_input == '' and setupPhase: # End turn if nothing selected; otherwise cancel selection
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
        print(f"Player {activePlayer} wins by capturing the flag in {turn} turns!") 
        victory = True
        return attacker
    elif defender_strength == P_BOMB and attacker_strength == P_MINER: 
        log_action(f"{piece_name(attacker)} defused {piece_name(defender)} at {positions_to_string([get_coords(defender_position)])}") 
        return attacker # piece_name(defender) destroyed
    elif defender_strength == P_MARSHALL and attacker_strength == P_SPY:
        log_action(f"{piece_name(attacker)} assassinated {piece_name(defender)} at {positions_to_string([get_coords(defender_position)])}") 
        return attacker # piece_name(defender) destroyed
    elif defender_strength == attacker_strength: 
        log_action(f"{piece_name(attacker)} and {piece_name(defender)} met at {positions_to_string([get_coords(defender_position)])}") 
        return 0 # piece_name(attacker) and piece_name(defender) destroyed
    elif defender_strength < attacker_strength: 
        log_action(f"{piece_name(attacker)} destroyed {piece_name(defender)} at {positions_to_string([get_coords(defender_position)])}") 
        return attacker # piece_name(defender) destroyed
    else:
        log_action(f"{piece_name(defender)} defeated {piece_name(attacker)} from {positions_to_string([get_coords(attacker_position)])}") 
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

def extract_digits(s):
    # Use a regular expression to find all single digits in the string
    digits = re.findall(r'\b\d\b', s)
    # Convert the found digits to integers and return the first four
    return [int(digit) for digit in digits[:4]]

def get_fallbackAI_move():
    global selection, target

    moveable_pieces = []
    for i in range(0,100):
        if board[i] > PIECE_LIMIT: continue
        if len(get_valid_moves(i)) > 0: moveable_pieces.append(i)

    selection = random.choice(moveable_pieces[(len(moveable_pieces) // 2):]) # Select a random moveable piece from the secon half of the list
    valid_destinations = get_valid_moves(selection)
    target = valid_destinations[-1]

# Automatically set up player pieces
setup_pieces(TEAM_RED)
setup_pieces(TEAM_BLUE)

# Players can rearrange pieces
while setupPhase:

    if AI: activePlayer = TEAM_BLUE

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

        while (target == None) and selection is not None:
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
        
        if target is not None:
            swapPiece = board[selection]
            board[selection] = board[target]
            board[target] = swapPiece
            selection, target = None, None

# Setup complete, taking turns until flag exposed
while not victory:
    if AI and activePlayer == TEAM_RED and not setupPhase:
        summarise_state()
        aiSuggestion = get_openAI_move(gameState)
        aiMove = extract_digits(aiSuggestion)
        if len(aiMove) < 4:
            # OpenAI fail
            print(f"OpenAI suggestion fail: {aiMove}")
            get_fallbackAI_move()
        else:
            selection  = (aiMove[1] * 10) + aiMove[0]
            if board[selection] > 0 and board[selection] <= PIECE_LIMIT:
                target = (aiMove[3] * 10) + aiMove[2]
       
        valid_destinations = get_valid_moves(selection)
        if target not in valid_destinations:
            print(f"OpenAI detail fail: {aiMove}")
            get_fallbackAI_move()

        turn += 1

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
                    messageText = f"{piece_name(board[selection])} has no valid moves."
                    selection = None
                    
        print_board()            

    if AI and activePlayer == TEAM_RED: 
        # Do AI move
        winner = resolve_conflict(selection, target)

        board[target] = winner
        board[selection] = 0

        selection, target = None, None
        activePlayer = activePlayer ^ 1 # XOR to flip player turns
        
    else:

        # Piece selected, need valid move destination
        if (not selection == None):
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

print(' Bye!')
