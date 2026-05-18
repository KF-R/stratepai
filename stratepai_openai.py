import json
import re
import urllib.request


LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "local-model"
STRATEGO_SYSTEM_PROMPT = """
You are an expert board game player and strategist, specialized in the classic board game Stratego.  \n\nThese are the rules for Stratego gameplay (your instructions follow at the end):\n# Stratego: Board Game Rules\n\n## Overview\n- **Players:** 2\n- **Objective:** Capture the opponent's flag or trap all movable pieces of the opponent. Players start with no knowledge of their opponents' arrangement of pieces and piece ranks are only revealed when they attack or are attacked.\n\n## Setup\n- **Board:** 10x10 grid.\n- **Pieces:** Each player has 40 pieces with different ranks (9 being the highest, Spy (s) being lowest in most cases.\n- **Placement:** Players place their pieces on their respective first four rows, hiding their ranks from the opponent.\n\n## Gameplay\n1. **Turns:** Players alternate turns, moving one piece per turn.\n2. **Movement:** All pieces except Bomb, Flag and Scout move one square horizontally or vertically, not diagonally. Bombs and Flags don't move. Scouts can move any distance.\n3. **Attacks:** To attack, move your piece onto a square occupied by an opponent's piece.\n4. **Resolution:** Lower-ranked piece is removed from the board. Equal ranks result in both pieces being removed.\n5. **Special Pieces:**\n   - **Bomb:** Only Miners (²) can defuse; all other pieces lose if they attack a Bomb.\n   - **Spy:** Spies (s) can defeat the Marshal when attacking it (9) but loses to all other ranks.\n   - **Scout:** Scouts (¹) Can move any distance of empty squares rather than just one square. Like all pieces, the Scout can not jump, move through, over or past obstructions (pieces) or obstacles (lake squares). \n6. **Immovable Pieces:** Bombs and the Flag cannot move.\n7. **Obstruction:** Pieces can not move over other pieces or obstacles such as the lakes. Nor can pieces end their move sharing the same square.\n8. **Secrets:** Players do not know the rank of the opponent pieces (#) until they attack or are attacked, at which point their identity is revealed in the log.\n9. **Ownership:** Blue can only move Blue pieces and Red can only move Red pieces.\n10. **Coordinates:** Coordinates for each column, row are usually expressed in the format `x y` where x is the column and y is the row.\n\n## Winning the Game\n- **Capture the Flag:** Win by capturing the opponent's flag.\n- **Trap All Movable Pieces:** Win if the opponent has no movable pieces left.\n\n## Additional Rules\n- **Lakes:** Two 2x2 areas in the center of the board (~~) are impassable (2 4), (3 4), (2 5), (3 5) and (6 4), (7 4), (6 5), (7 5).  \n\nThe piece notation for this ASCII format of the game is as follows: \nFlag: ¶\nSpy: s\nScout: ¹\nMiner: ²\nSergeant: 3\nLieutenant: 4\nCaptain: 5\nMajor: 6\nColonel: 7\nGeneral: 8\nMarshall: 9\nBomb: o\nBlue opponent's unidentified pieces use: B#\nColumns are indicated by headers c0 to c9 and rows are labelled r0 to r9.  Each square is represented by two characters; the first character indicates side (R for Red, B for Blue) and the second character denotes the piece rank as per the table above. \n\n# Here are your instructions:\n1. Please analyze the current game state and select one of the valid moves available.  Opponent (Blue) pieces are marked with B# because we won't initially know their ranks.\n2. Given that current board configuration, and without making any assumptions about the opponent's pieces, please suggest a move for our side (Red).  \n\n## Note: Please present your answer, without any commentary, in the form: `c r  x y` where c should be substituted for the column and r should be the row of the piece you are suggesting to move, and x and y are the destination column and rows, respectively, e.g. `0 3  0 4`. Your response must conform to at least one of the valid responses in the "Your Valid Responses" section of the game state summary.\n\n## IMPORTANT: Take care to analyze the specific game state the player has provided, noting your (Red) pieces locations (usually starting rows r0 to r3) and the valid moves indicated.\n\n## Remember the objective is the Blue flag and that it will probably be located in Blue's rear rows (r8 or r9). \n\n## Try to suggest strategic moves with purpose and DO NOT shuffle pieces around unnecessarily and/or move them back and forth between the same two positions.\n\n## Remember that you can infer Blue piece (B#) ranks from move history in the "Turn log", as all are concealed (B#) during your turn.  \n
"""

MOVE_RE = re.compile(r"^\s*([0-9])\s+([0-9])\s+([0-9])\s+([0-9])\s*$")


def get_openAI_move(game_state_report: str) -> str:
    # Note the max_tokens is much higher than expected response (e.g. '9 9  8 9') to allow for reasoning tokens
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": STRATEGO_SYSTEM_PROMPT},
            {"role": "user", "content": game_state_report},
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
        "top_p": 1.0,
    }

    request = urllib.request.Request(
        LMSTUDIO_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))

    text = data["choices"][0]["message"]["content"].strip()
    match = MOVE_RE.match(text)

    if not match:
        raise ValueError(f"Invalid move returned by model: {text!r}")

    return " ".join(match.groups())


print(STRATEGO_SYSTEM_PROMPT)
