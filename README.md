## stratepai (/ˈstrætə-paɪ/ "stratta-pie")
Terminal Stratego for the ASCII and ANSI inclined.

<img src="https://github.com/KF-R/stratepai/assets/6677966/222e26b3-c290-4c3c-b029-1bbba4216fed" align="right" height="241">
This is a fairly concise plain text Stratego interface that has been useful for experimenting with various LLMs. 
<hr/>

### Piece notation: 
¶ s ¹ ² 3 4 5 6 7 8 9 o <br/>
_Unknown pieces use:_ ■

### Corresponding piece names:
'Flag', 'Spy', 'Scout', 'Miner', 'Sergeant', 'Lieutenant', 'Captain', 'Major', 'Colonel', 'General', 'Marshall', 'Bomb'

<hr/>

**Assumes a local endpoint to be already running. Confiugrable via** `stratepai_openai.py`**:**
```
LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
```

### Installation and usage

_No dependencies to install; venv not necessary._

```
git clone https://github.com/KF-R/stratepai
cd stratepai/
python stratepai.py
```

<hr/>
Stratego on Wikipedia: <br/>
https://en.wikipedia.org/wiki/Stratego
<br/><br/>
Leading research on Stratego AI: <br/>
https://deepmind.google/discover/blog/mastering-stratego-the-classic-game-of-imperfect-information/
