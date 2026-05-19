#!/usr/bin/env python3
"""
Stratego — single-file Flask edition

Usage:
    pip install flask
    python app.py

Optional:
    Put a setups.py file next to this file containing:

        SETUPS = [
            "o¹43¹3¹¹¹o539748¹634²5²¶s²5o¹¹6o7²6o5²o4",
            ...
        ]

    Or point to it explicitly:

        STRATEGO_SETUPS=/path/to/setups.py python app.py
"""

from __future__ import annotations

import importlib.util
import os
import random
import re
from pathlib import Path
from typing import Iterable

from flask import Flask, jsonify, render_template_string

APP_VERSION = "1.1.2-flask"
VALID_SETUP_RE = re.compile(r"^[¶s¹²3456789o]{40}$")

FALLBACK_SETUPS = (
    "o¹43¹3¹¹¹o539748¹634²5²¶s²5o¹¹6o7²6o5²o4",
    "¹36834¹934¹45s¹56²¹5oo²7¹67o²o45¹²¹²o¶o3",
    "5¹4¹5¹4¹35¹7²6²¹69¹²34s²75oo6¹8²oo3o¶o34",
    "5¹5¹5¹63¹4967484s4o36¹²o²73¹²5¹¹o¶o²o3o²",
)


def valid_setups(items: Iterable[object]) -> tuple[str, ...]:
    """Return only valid 40-symbol Stratego setup strings."""
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, str):
            continue
        s = item.strip()
        if VALID_SETUP_RE.fullmatch(s) and s not in seen:
            out.append(s)
            seen.add(s)
    return tuple(out)


def load_setups() -> tuple[str, ...]:
    """Load SETUPS from setups.py, falling back to bundled examples."""
    explicit = os.environ.get("STRATEGO_SETUPS")
    setup_path = Path(explicit).expanduser() if explicit else Path(__file__).with_name("setups.py")

    if setup_path.exists():
        spec = importlib.util.spec_from_file_location("stratego_external_setups", setup_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            loaded = valid_setups(getattr(module, "SETUPS", ()))
            if loaded:
                print(f"Loaded {len(loaded):,} Stratego setup patterns from {setup_path}")
                return loaded
            print(f"Found {setup_path}, but it contained no valid setup strings. Using fallback setups.")

    print(f"Using {len(FALLBACK_SETUPS):,} bundled fallback Stratego setup patterns.")
    return FALLBACK_SETUPS


SETUPS = load_setups()
app = Flask(__name__)


@app.get("/")
def index():
    return render_template_string(
        APP_HTML,
        app_version=APP_VERSION,
        setup_count=len(SETUPS),
    )


@app.get("/api/setups/count")
def setup_count():
    return jsonify({"count": len(SETUPS)})


@app.get("/api/setups/random")
def random_setup():
    return jsonify({"setup": random.choice(SETUPS), "count": len(SETUPS)})


@app.get("/api/setups/pair")
def random_setup_pair():
    return jsonify({
        "red": random.choice(SETUPS),
        "blue": random.choice(SETUPS),
        "count": len(SETUPS),
    })


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "version": APP_VERSION, "setups": len(SETUPS)})


APP_HTML = r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>Stratego — Napoleonic Command</title>
<style>
  :root {
    --bg: #17120e;
    --panel: rgba(42, 31, 23, 0.82);
    --panel-strong: rgba(31, 23, 18, 0.94);
    --ink: #f4ead4;
    --muted: #c8b790;
    --gold: #d6aa50;
    --gold-soft: rgba(214, 170, 80, 0.24);
    --red: #a93232;
    --red-hi: #ef7870;
    --blue: #243f86;
    --blue-hi: #73a2ff;
    --lake: #1b5260;
    --cell: rgba(130, 91, 51, 0.52);
    --cell2: rgba(96, 65, 38, 0.58);
    --danger: #da5e4d;
    --ok: #82cf8a;
    --shadow: 0 22px 60px rgba(0, 0, 0, 0.38);
    --radius: 18px;
    color-scheme: dark;
  }

  * { box-sizing: border-box; }

  html, body {
    margin: 0;
    min-height: 100%;
    background:
      radial-gradient(circle at 12% 5%, rgba(217, 163, 87, 0.13), transparent 28rem),
      radial-gradient(circle at 88% 12%, rgba(58, 83, 151, 0.18), transparent 30rem),
      linear-gradient(135deg, #120e0b, #27190f 48%, #100d0b);
    color: var(--ink);
    font-family: ui-serif, Georgia, Cambria, "Times New Roman", serif;
  }

  body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0.18;
    background-image:
      linear-gradient(0deg, rgba(255,255,255,0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 24px 24px;
    mix-blend-mode: overlay;
  }

  button, input, select, textarea { font: inherit; }

  button, .buttonish, input[type="file"]::file-selector-button {
    border: 1px solid rgba(214, 170, 80, 0.55);
    color: var(--ink);
    background: linear-gradient(180deg, rgba(98, 65, 34, 0.92), rgba(45, 32, 24, 0.96));
    box-shadow: inset 0 1px rgba(255,255,255,0.12), 0 8px 20px rgba(0,0,0,0.18);
    border-radius: 999px;
    padding: 0.58rem 0.86rem;
    cursor: pointer;
    transition: transform 130ms ease, border-color 130ms ease, background 130ms ease, opacity 130ms ease;
  }

  button:hover:not(:disabled), .buttonish:hover, input[type="file"]::file-selector-button:hover {
    transform: translateY(-1px);
    border-color: rgba(255, 216, 140, 0.9);
  }

  button:disabled { cursor: default; opacity: 0.48; }

  input, select, textarea {
    width: 100%;
    color: var(--ink);
    background: rgba(16, 12, 10, 0.68);
    border: 1px solid rgba(214, 170, 80, 0.28);
    border-radius: 12px;
    padding: 0.62rem 0.7rem;
    outline: none;
  }

  input:focus, select:focus, textarea:focus {
    border-color: rgba(255, 216, 140, 0.75);
    box-shadow: 0 0 0 3px rgba(214, 170, 80, 0.14);
  }

  .app {
    width: min(1480px, calc(100vw - 24px));
    margin: 0 auto;
    padding: clamp(12px, 2vw, 30px) 0 28px;
  }

  .titlebar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .brand { display: grid; gap: 0.18rem; }

  .title-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 0.55rem;
  }

  .title-game-btn { display: none; }

  h1 {
    margin: 0;
    letter-spacing: 0.06em;
    font-size: clamp(1.55rem, 2.4vw, 3.05rem);
    text-transform: uppercase;
    text-shadow: 0 2px 0 rgba(0,0,0,0.3);
  }

  .subtitle { color: var(--muted); font-size: clamp(0.88rem, 1.2vw, 1.08rem); }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    width: fit-content;
    border: 1px solid rgba(214, 170, 80, 0.38);
    background: rgba(20, 15, 12, 0.62);
    color: #f6ddb2;
    border-radius: 999px;
    padding: 0.42rem 0.66rem;
    font-size: 0.9rem;
  }

  .screen { display: none; }
  .screen.active { display: block; }

  .menu-card, .board-card, .side-card, .modal-card {
    border: 1px solid rgba(214, 170, 80, 0.28);
    background:
      linear-gradient(180deg, rgba(61, 43, 31, 0.88), rgba(26, 20, 16, 0.9)),
      radial-gradient(circle at 50% 0%, rgba(255,255,255,0.1), transparent 24rem);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    backdrop-filter: blur(9px);
  }

  .menu-card { overflow: hidden; }

  .menu-hero {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    min-height: min(78vh, 820px);
  }

  .hero-art {
    position: relative;
    padding: clamp(22px, 4vw, 58px);
    overflow: hidden;
    background:
      radial-gradient(circle at 40% 42%, rgba(214,170,80,0.24), transparent 15rem),
      linear-gradient(150deg, rgba(81, 46, 28, 0.3), rgba(10, 13, 19, 0.32));
  }

  .hero-art::before {
    content: "";
    position: absolute;
    inset: 24px;
    border: 1px solid rgba(214,170,80,0.25);
    border-radius: 24px;
    background:
      linear-gradient(90deg, transparent 49.6%, rgba(214,170,80,0.09) 50%, transparent 50.4%),
      linear-gradient(0deg, transparent 49.6%, rgba(214,170,80,0.09) 50%, transparent 50.4%),
      radial-gradient(circle at 50% 50%, transparent 0 38%, rgba(214,170,80,0.08) 39% 39.7%, transparent 40%);
  }

  .hero-copy {
    position: relative;
    z-index: 1;
    max-width: 650px;
    display: grid;
    align-content: end;
    min-height: 100%;
  }

  .hero-copy h2 {
    margin: 0 0 0.8rem;
    font-size: clamp(2rem, 4vw, 5.3rem);
    line-height: 0.92;
  }

  .hero-copy p {
    margin: 0;
    max-width: 58ch;
    color: var(--muted);
    font-size: clamp(1rem, 1.2vw, 1.18rem);
    line-height: 1.55;
  }

  .formation {
    position: absolute;
    top: clamp(20px, 6vw, 78px);
    left: clamp(18px, 4vw, 78px);
    display: grid;
    grid-template-columns: repeat(10, clamp(18px, 2.8vw, 36px));
    gap: clamp(4px, 0.5vw, 8px);
    transform: rotate(-6deg);
    opacity: 0.85;
  }

  .formation span {
    width: clamp(18px, 2.8vw, 36px);
    aspect-ratio: 1;
    display: grid;
    place-items: center;
    border-radius: 50%;
    border: 1px solid rgba(255, 224, 153, 0.24);
    background: linear-gradient(145deg, rgba(147, 45, 40, 0.9), rgba(47, 20, 22, 0.92));
    box-shadow: 0 5px 10px rgba(0,0,0,0.25);
    color: #ffe9cf;
    font-weight: 700;
  }

  .menu-form {
    padding: clamp(18px, 3vw, 42px);
    display: grid;
    align-content: center;
    gap: 1rem;
    border-left: 1px solid rgba(214, 170, 80, 0.18);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.85rem;
  }

  label {
    display: grid;
    gap: 0.35rem;
    color: #f5dfba;
    font-size: 0.9rem;
  }

  .wide { grid-column: 1 / -1; }

  .hint {
    color: var(--muted);
    font-size: 0.88rem;
    line-height: 1.4;
  }

  .menu-actions, .toolbar, .setup-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    align-items: center;
  }

  .primary {
    background: linear-gradient(180deg, rgba(184, 121, 48, 0.98), rgba(102, 55, 27, 0.98));
    border-color: rgba(255, 224, 157, 0.75);
  }

  .danger {
    border-color: rgba(218, 94, 77, 0.7);
    background: linear-gradient(180deg, rgba(118, 42, 34, 0.96), rgba(47, 25, 22, 0.96));
  }

  .game-grid {
    display: grid;
    grid-template-columns: minmax(380px, 1fr) minmax(300px, 380px);
    gap: clamp(12px, 1.5vw, 20px);
    align-items: start;
  }

  .board-card { padding: clamp(10px, 1.4vw, 18px); }

  .command-strip {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
    min-height: 4.4rem;
  }

  .command-strip > div:first-child {
    min-height: 3.55rem;
  }

  #phaseHelp {
    min-height: 2.8em;
    max-height: 2.8em;
    overflow: hidden;
  }

  #suggestionText {
    min-height: 1.4em;
  }

  .status-line {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
  }

  .phase-help {
    color: var(--muted);
    font-size: 0.94rem;
    margin-top: 0.4rem;
  }

  .board-shell {
    position: relative;
    width: min(100%, calc(100dvh - 190px));
    min-width: min(100%, 320px);
    aspect-ratio: 1 / 1;
    margin: 0 auto;
    border-radius: 18px;
    overflow: hidden;
    border: 2px solid rgba(214,170,80,0.34);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06), 0 18px 38px rgba(0,0,0,0.35);
    background:
      radial-gradient(circle at 50% 45%, rgba(255,255,255,0.05), transparent 34%),
      linear-gradient(135deg, #67503b, #3f2b1c);
  }

  .cells, .piece-layer, .fx-layer {
    position: absolute;
    inset: 0;
  }

  .cells {
    display: grid;
    grid-template-columns: repeat(10, minmax(0, 1fr));
    grid-template-rows: repeat(10, minmax(0, 1fr));
  }

  .cell {
    position: relative;
    border: 0;
    border-right: 1px solid rgba(45, 31, 22, 0.48);
    border-bottom: 1px solid rgba(45, 31, 22, 0.48);
    border-radius: 0;
    padding: 0;
    background: var(--cell);
    box-shadow: none;
    cursor: pointer;
    min-width: 0;
    aspect-ratio: 1 / 1;
  }

  .cell:nth-child(odd) { background: var(--cell2); }
  .cell:hover { outline: 2px solid rgba(255, 232, 166, 0.23); outline-offset: -2px; }
  .cell:focus-visible { outline: 3px solid rgba(255, 232, 166, 0.8); outline-offset: -3px; }

  .cell::after {
    content: attr(data-coord);
    position: absolute;
    right: 4px;
    bottom: 2px;
    color: rgba(255, 238, 201, 0.24);
    font-size: clamp(0.48rem, 0.7vw, 0.68rem);
    pointer-events: none;
  }

  .cell.setup-red { background-image: linear-gradient(0deg, rgba(169, 50, 50, 0.15), transparent); }
  .cell.setup-blue { background-image: linear-gradient(180deg, rgba(36, 63, 134, 0.18), transparent); }

  .cell.lake {
    cursor: default;
    background:
      radial-gradient(circle at 24% 26%, rgba(255,255,255,0.16), transparent 10%),
      radial-gradient(circle at 70% 80%, rgba(255,255,255,0.1), transparent 14%),
      linear-gradient(145deg, #174856, #0d2f3a);
  }

  .cell.lake::before {
    content: "~~";
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    color: rgba(205, 235, 242, 0.48);
    font-size: clamp(0.7rem, 1.8vw, 1.25rem);
    letter-spacing: 0.12em;
  }

  .cell.selected {
    box-shadow: inset 0 0 0 4px rgba(255, 230, 150, 0.68), inset 0 0 24px rgba(255, 226, 133, 0.18);
    z-index: 1;
  }

  .cell.valid { box-shadow: inset 0 0 0 3px rgba(130, 207, 138, 0.72), inset 0 0 20px rgba(130, 207, 138, 0.12); }
  .cell.attack-target { box-shadow: inset 0 0 0 3px rgba(218, 94, 77, 0.78), inset 0 0 22px rgba(218, 94, 77, 0.22); }
  .cell.last-move { animation: cellGlow 1300ms ease-out 1; }

  @keyframes cellGlow {
    0% { box-shadow: inset 0 0 0 5px rgba(255, 215, 120, 0.8), inset 0 0 25px rgba(255, 215, 120, 0.26); }
    100% { box-shadow: inset 0 0 0 0 rgba(255, 215, 120, 0); }
  }

  .piece-layer { pointer-events: none; z-index: 5; }
  .fx-layer { pointer-events: none; z-index: 8; }

  .piece, .moving-piece {
    position: absolute;
    width: 10%;
    height: 10%;
    left: calc(var(--x) * 10%);
    top: calc(var(--y) * 10%);
    display: grid;
    place-items: center;
    padding: clamp(6px, 0.8vw, 11px);
    transition: transform 150ms ease, filter 150ms ease, opacity 150ms ease;
  }

  .piece-inner {
    width: min(72%, 45px);
    aspect-ratio: 1;
    display: grid;
    place-items: center;
    border-radius: 50%;
    border: 2px solid rgba(255, 235, 180, 0.42);
    box-shadow: inset 0 2px 6px rgba(255,255,255,0.13), inset 0 -10px 18px rgba(0,0,0,0.22), 0 8px 12px rgba(0,0,0,0.32);
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif;
    font-weight: 900;
    font-size: clamp(0.72rem, 1.55vw, 1.32rem);
    text-shadow: 0 2px 2px rgba(0,0,0,0.35);
    line-height: 1;
  }

  .piece.red .piece-inner, .moving-piece.red .piece-inner { background: radial-gradient(circle at 35% 26%, var(--red-hi), var(--red) 55%, #4b1717); }
  .piece.blue .piece-inner, .moving-piece.blue .piece-inner { background: radial-gradient(circle at 35% 26%, var(--blue-hi), var(--blue) 55%, #111d46); }
  .piece.hidden .piece-inner, .moving-piece.hidden .piece-inner {
    background: radial-gradient(circle at 35% 25%, #d6c095, #7f6542 54%, #332417);
    color: #2b1f17;
  }

  .piece.pulse .piece-inner { animation: piecePulse 680ms ease 1; }
  .piece.moving-source { opacity: 0.28; filter: saturate(0.6); }

  @keyframes piecePulse {
    0%, 100% { transform: scale(1); }
    42% { transform: scale(1.16); }
  }

  .moving-piece {
    z-index: 12;
    animation: marchPiece 620ms cubic-bezier(.18,.82,.19,1) forwards;
    filter: drop-shadow(0 12px 15px rgba(0,0,0,0.4));
  }

  @keyframes marchPiece {
    0% { transform: translate(0, 0) scale(1.02); }
    58% { transform: translate(calc(var(--dx) * 58%), calc(var(--dy) * 58%)) scale(1.13); }
    100% { transform: translate(var(--dx), var(--dy)) scale(1.02); }
  }

  .move-vector {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
    opacity: 0;
    animation: vectorFade 660ms ease forwards;
  }

  .move-vector line {
    stroke: rgba(255, 229, 162, 0.72);
    stroke-width: 1.8;
    stroke-dasharray: 5 4;
    stroke-linecap: round;
    filter: drop-shadow(0 2px 2px rgba(0,0,0,0.45));
  }

  @keyframes vectorFade {
    0% { opacity: 0; }
    18% { opacity: 0.95; }
    100% { opacity: 0; }
  }

  .side-stack { display: grid; gap: 0.9rem; }
  .side-card { padding: 1rem; }

  .side-card h3 {
    margin: 0 0 0.65rem;
    font-size: 1.03rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #f6dfb3;
  }

  .panel-text { color: var(--muted); line-height: 1.42; font-size: 0.94rem; }

  .small-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.5rem;
  }

  .mini-stat {
    border: 1px solid rgba(214,170,80,0.22);
    border-radius: 12px;
    background: rgba(15, 11, 9, 0.42);
    padding: 0.58rem;
  }

  .mini-stat b { display: block; font-size: 1.15rem; }

  .log {
    max-height: 260px;
    overflow: auto;
    padding-right: 0.25rem;
    display: grid;
    gap: 0.45rem;
  }

  .log-entry {
    border-left: 3px solid rgba(214,170,80,0.45);
    padding: 0.38rem 0.5rem;
    background: rgba(15, 11, 9, 0.34);
    border-radius: 0 9px 9px 0;
    color: #eadabe;
    font-size: 0.9rem;
    line-height: 1.32;
  }

  .intel-list, .graveyard { display: flex; flex-wrap: wrap; gap: 0.34rem; }

  .intel-chip, .dead-chip {
    display: inline-flex;
    gap: 0.32rem;
    align-items: center;
    border: 1px solid rgba(214,170,80,0.28);
    border-radius: 999px;
    background: rgba(17, 12, 9, 0.42);
    padding: 0.28rem 0.48rem;
    color: #f5e4c8;
    font-size: 0.86rem;
  }

  .combat-modal {
    position: fixed;
    inset: 0;
    display: none;
    pointer-events: none;
    z-index: 30;
    padding: clamp(10px, 2vw, 24px);
    align-items: flex-start;
    justify-content: flex-end;
    background: transparent;
  }

  .combat-modal.visible { display: flex; }

  .victory-modal {
    position: fixed;
    inset: 0;
    display: none;
    place-items: center;
    background: rgba(0,0,0,0.38);
    z-index: 35;
    padding: 1rem;
  }

  .victory-modal.visible { display: grid; }

  .modal-card {
    width: min(440px, 100%);
    padding: clamp(14px, 2vw, 22px);
    background:
      linear-gradient(180deg, rgba(61, 43, 31, 0.82), rgba(26, 20, 16, 0.78)),
      radial-gradient(circle at 50% 0%, rgba(255,255,255,0.08), transparent 18rem);
    backdrop-filter: blur(12px);
  }

  .combat-modal .modal-card {
    margin-top: clamp(72px, 9vh, 118px);
    opacity: 0.92;
    transform: translateY(-8px);
    animation: combatSlide 220ms ease forwards;
  }

  @keyframes combatSlide {
    to { transform: translateY(0); }
  }

  .modal-card h2 { margin: 0 0 0.7rem; }

  .combat-cards {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 0.55rem;
    align-items: stretch;
    margin: 0.7rem 0;
  }

  .combat-card {
    border: 1px solid rgba(214,170,80,0.34);
    border-radius: 14px;
    padding: 0.7rem;
    background: rgba(16, 12, 10, 0.48);
    animation: revealCard 360ms ease both;
  }

  .combat-card .big {
    font-size: clamp(1.85rem, 4vw, 3.25rem);
    line-height: 1;
    margin-bottom: 0.25rem;
  }

  .versus {
    color: var(--gold);
    font-size: 1.1rem;
    font-weight: 800;
    align-self: center;
  }

  @keyframes revealCard {
    from { transform: rotateY(82deg) scale(0.92); opacity: 0; }
    to { transform: rotateY(0deg) scale(1); opacity: 1; }
  }

  .boom {
    position: absolute;
    width: 10%;
    height: 10%;
    left: calc(var(--x) * 10%);
    top: calc(var(--y) * 10%);
    display: grid;
    place-items: center;
  }

  .boom::before, .boom::after {
    content: "";
    position: absolute;
    width: 25%;
    aspect-ratio: 1;
    border-radius: 50%;
    background: radial-gradient(circle, #fff2b8, #f2994a 42%, rgba(218, 94, 77, 0.15) 70%, transparent 71%);
    animation: boom 540ms ease-out forwards;
  }

  .boom::after {
    width: 40%;
    animation-delay: 70ms;
    background: radial-gradient(circle, #fff, #f7c45c 30%, rgba(218, 94, 77, 0.2) 68%, transparent 69%);
  }

  @keyframes boom {
    from { transform: scale(0.4); opacity: 1; filter: blur(0); }
    to { transform: scale(3.2); opacity: 0; filter: blur(2px); }
  }

  .confetti {
    position: fixed;
    top: -8px;
    width: 8px;
    height: 14px;
    background: var(--gold);
    z-index: 40;
    animation: fall var(--dur) linear forwards;
  }

  @keyframes fall {
    to { transform: translate3d(var(--dx), 105vh, 0) rotate(760deg); opacity: 0.2; }
  }

  .toast {
    position: fixed;
    left: 50%;
    bottom: 18px;
    transform: translateX(-50%) translateY(14px);
    opacity: 0;
    transition: opacity 180ms ease, transform 180ms ease;
    border: 1px solid rgba(214,170,80,0.35);
    background: rgba(20, 14, 10, 0.92);
    color: var(--ink);
    border-radius: 999px;
    padding: 0.65rem 0.9rem;
    box-shadow: var(--shadow);
    z-index: 50;
  }

  .toast.visible { opacity: 1; transform: translateX(-50%) translateY(0); }

  @media (max-width: 1020px) {
    .menu-hero { grid-template-columns: 1fr; }
    .hero-art { min-height: 390px; }
    .menu-form { border-left: 0; border-top: 1px solid rgba(214, 170, 80, 0.18); }
    .game-grid { grid-template-columns: 1fr; }
    .board-shell { width: min(100%, calc(100dvh - 220px)); }
    .combat-modal { justify-content: center; align-items: flex-end; }
    .combat-modal .modal-card { margin-top: 0; margin-bottom: 14px; width: min(520px, 100%); }
  }

  @media (max-width: 620px) {
    .titlebar { align-items: flex-start; flex-direction: column; }
    .form-grid, .small-grid { grid-template-columns: 1fr; }
    .command-strip { align-items: stretch; }
    .toolbar, .setup-actions { width: 100%; }
    .toolbar button, .setup-actions button { flex: 1 1 auto; }
    .combat-cards { grid-template-columns: 1fr; }
    .versus { transform: rotate(90deg); }
    .piece-inner { border-width: 1px; width: min(68%, 38px); }
    .board-shell { width: 100%; }
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 1ms !important; transition-duration: 1ms !important; scroll-behavior: auto !important; }
  }
</style>
</head>
<body>
<div class="app">
  <header class="titlebar">
    <div class="brand">
      <h1>Stratego</h1>
      <div class="subtitle">Napoleonic command, hidden ranks, ruthless reconnaissance.</div>
    </div>
    <div class="title-actions">
      <div class="badge" id="versionBadge">Flask build · v{{ app_version }}</div>
      <button id="saveBtn" class="title-game-btn">Export save</button>
      <button id="restartBtn" class="danger title-game-btn">Main menu</button>
    </div>
  </header>

  <main id="screenMenu" class="screen active">
    <section class="menu-card">
      <div class="menu-hero">
        <div class="hero-art" aria-hidden="true">
          <div class="formation" id="formationArt"></div>
          <div class="hero-copy">
            <h2>Deploy. Deceive. Break the line.</h2>
            <p>Classic Stratego rules with server-loaded setup patterns, imperfect information, AI memory, animated movement, combat reveals, move logs, and JSON savegames.</p>
          </div>
        </div>
        <form class="menu-form" id="menuForm">
          <div class="form-grid">
            <label>Opponent
              <select id="opponentType">
                <option value="ai" selected>AI opponent</option>
                <option value="human">Two-player pass-and-play</option>
              </select>
            </label>
            <label>Your colour
              <select id="humanSide">
                <option value="red" selected>Red</option>
                <option value="blue">Blue</option>
              </select>
            </label>
            <label>Red commander
              <input id="redName" value="Red Marshal" maxlength="36" />
            </label>
            <label>Blue commander
              <input id="blueName" value="Blue Marshal" maxlength="36" />
            </label>
            <label>AI difficulty
              <select id="aiDifficulty">
                <option value="easy">Cadet — fallible and impulsive</option>
                <option value="normal" selected>Officer — balanced memory</option>
                <option value="hard">General — careful and tactical</option>
                <option value="expert">Marshal — near-perfect recall</option>
              </select>
            </label>
            <label>Information mode
              <select id="infoMode">
                <option value="classic" selected>Classic — revealed only during combat</option>
                <option value="revelations">Revelations — identified pieces stay revealed</option>
              </select>
            </label>
            <label class="wide">Load setup library or savegame
              <input id="fileInput" type="file" accept=".txt,.json,.py,application/json,text/plain" />
              <span class="hint">The server uses local <code>setups.py</code> by default. This loader still accepts exported savegame JSON, JSON setup arrays, plain text setup rows, or Python files containing <code>SETUPS = [...]</code>.</span>
            </label>
          </div>
          <div class="menu-actions">
            <button class="primary" type="submit">Begin deployment</button>
            <button type="button" id="loadSampleSave">Load tiny demo game</button>
          </div>
          <div class="hint" id="setupCountHint"></div>
        </form>
      </div>
    </section>
  </main>

  <main id="screenGame" class="screen">
    <div class="game-grid">
      <section class="board-card">
        <div class="command-strip">
          <div>
            <div class="status-line">
              <span class="badge" id="turnBadge">Deployment</span>
              <span class="badge" id="viewerBadge">Viewing Red</span>
            </div>
            <div class="phase-help" id="phaseHelp"></div>
          </div>
          <div class="toolbar">
            <button id="suggestBtn">Suggest move</button>
          </div>
        </div>
        <div class="setup-actions" id="setupActions">
          <button id="readyBtn" class="primary">Ready</button>
          <button id="randomizeBtn">Randomize this army</button>
          <button id="switchSetupBtn">Switch viewed army</button>
        </div>
        <div class="phase-help" id="suggestionText"></div>
        <div class="board-shell" id="boardShell">
          <div class="cells" id="cells"></div>
          <div class="piece-layer" id="pieceLayer"></div>
          <div class="fx-layer" id="fxLayer"></div>
        </div>
      </section>

      <aside class="side-stack">
        <section class="side-card">
          <h3>Command</h3>
          <div class="small-grid">
            <div class="mini-stat"><span class="hint">Red</span><b id="redStat">—</b></div>
            <div class="mini-stat"><span class="hint">Blue</span><b id="blueStat">—</b></div>
            <div class="mini-stat"><span class="hint">Mode</span><b id="modeStat">—</b></div>
            <div class="mini-stat"><span class="hint">Setups</span><b id="setupsStat">—</b></div>
          </div>
        </section>
        <section class="side-card">
          <h3>Intel</h3>
          <div class="panel-text" id="intelHelp"></div>
          <div class="intel-list" id="intelList"></div>
        </section>
        <section class="side-card">
          <h3>Captured pieces</h3>
          <div class="graveyard" id="graveyard"></div>
        </section>
        <section class="side-card">
          <h3>Move log</h3>
          <div class="log" id="log"></div>
        </section>
      </aside>
    </div>
  </main>
</div>

<div class="combat-modal" id="combatModal" role="dialog" aria-modal="false" aria-live="polite">
  <div class="modal-card">
    <h2 id="combatTitle">Combat</h2>
    <div class="combat-cards">
      <div class="combat-card" id="attackerCard"></div>
      <div class="versus">⚔</div>
      <div class="combat-card" id="defenderCard"></div>
    </div>
    <div class="panel-text" id="combatResult">Resolving...</div>
  </div>
</div>

<div class="victory-modal" id="victoryModal" role="dialog" aria-modal="true">
  <div class="modal-card">
    <h2 id="victoryTitle">Victory</h2>
    <p class="panel-text" id="victoryText"></p>
    <button id="victoryMenuBtn" class="primary">Return to main menu</button>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
(() => {
  "use strict";

  const SERVER_SETUP_COUNT = {{ setup_count }};
  const FALLBACK_SETUPS = [
    "o¹43¹3¹¹¹o539748¹634²5²¶s²5o¹¹6o7²6o5²o4",
    "¹36834¹934¹45s¹56²¹5oo²7¹67o²o45¹²¹²o¶o3",
    "5¹4¹5¹4¹35¹7²6²¹69¹²34s²75oo6¹8²oo3o¶o34",
    "5¹5¹5¹63¹4967484s4o36¹²o²73¹²5¹¹o¶o²o3o²"
  ];

  const META = {
    "¶": { name: "Flag", short: "Flag", power: 0, immobile: true, order: 0 },
    "o": { name: "Bomb", short: "Bomb", power: 11, immobile: true, order: 1 },
    "s": { name: "Spy", short: "Spy", power: 1, immobile: false, order: 2 },
    "¹": { name: "Scout", short: "Scout", power: 2, immobile: false, scout: true, order: 3 },
    "²": { name: "Miner", short: "Miner", power: 3, immobile: false, order: 4 },
    "3": { name: "Sergeant", short: "Sgt", power: 4, immobile: false, order: 5 },
    "4": { name: "Lieutenant", short: "Lt", power: 5, immobile: false, order: 6 },
    "5": { name: "Captain", short: "Cpt", power: 6, immobile: false, order: 7 },
    "6": { name: "Major", short: "Maj", power: 7, immobile: false, order: 8 },
    "7": { name: "Colonel", short: "Col", power: 8, immobile: false, order: 9 },
    "8": { name: "General", short: "Gen", power: 9, immobile: false, order: 10 },
    "9": { name: "Marshal", short: "Msh", power: 10, immobile: false, order: 11 }
  };

  const AI_PROFILES = {
    easy:   { label: "Cadet",   memory: 0.46, falseMemory: 0.10, decay: 0.075, noise: 18, aggression: 0.60, caution: 0.55 },
    normal: { label: "Officer", memory: 0.70, falseMemory: 0.055, decay: 0.045, noise: 10, aggression: 0.78, caution: 0.86 },
    hard:   { label: "General", memory: 0.89, falseMemory: 0.025, decay: 0.022, noise: 4.2, aggression: 0.92, caution: 1.1 },
    expert: { label: "Marshal", memory: 0.98, falseMemory: 0.006, decay: 0.006, noise: 1.2, aggression: 1.0, caution: 1.28 }
  };

  const LAKES = new Set(["2,4", "3,4", "2,5", "3,5", "6,4", "7,4", "6,5", "7,5"]);
  const DIRS = [[1,0],[-1,0],[0,1],[0,-1]];
  const VALID_SETUP_RE = /^[¶s¹²3456789o]{40}$/u;
  const SYMBOLS = Object.keys(META);

  let localSetupLibrary = null;
  let setupSourceCount = SERVER_SETUP_COUNT;
  let state = null;
  let selected = null;
  let busy = false;
  let nextPieceNo = 1;

  const $ = sel => document.querySelector(sel);
  const $$ = sel => Array.from(document.querySelectorAll(sel));
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const key = (x, y) => `${x},${y}`;
  const idx = (x, y) => y * 10 + x;
  const inBounds = (x, y) => x >= 0 && x < 10 && y >= 0 && y < 10;
  const other = side => side === "red" ? "blue" : "red";
  const cap = s => s.slice(0, 1).toUpperCase() + s.slice(1);
  const pieceName = ch => META[ch]?.name || "Unknown";
  const coord = p => `${p.x} ${p.y}`;
  const rand = arr => arr[Math.floor(Math.random() * arr.length)];
  const clone = obj => JSON.parse(JSON.stringify(obj));

  async function serverSetupPair() {
    try {
      const res = await fetch("/api/setups/pair", { cache: "no-store" });
      if (!res.ok) throw new Error("setup endpoint failed");
      return await res.json();
    } catch (_) {
      return { red: rand(FALLBACK_SETUPS), blue: rand(FALLBACK_SETUPS), count: FALLBACK_SETUPS.length };
    }
  }

  async function randomSetup() {
    if (localSetupLibrary?.length) return rand(localSetupLibrary);
    try {
      const res = await fetch("/api/setups/random", { cache: "no-store" });
      if (!res.ok) throw new Error("setup endpoint failed");
      const data = await res.json();
      setupSourceCount = data.count || setupSourceCount;
      return data.setup;
    } catch (_) {
      setupSourceCount = FALLBACK_SETUPS.length;
      return rand(FALLBACK_SETUPS);
    }
  }

  function buildBoardCells() {
    const cells = $("#cells");
    cells.innerHTML = "";
    for (let y = 0; y < 10; y++) {
      for (let x = 0; x < 10; x++) {
        const c = document.createElement("button");
        c.type = "button";
        c.className = "cell";
        c.dataset.x = String(x);
        c.dataset.y = String(y);
        c.dataset.coord = `${x} ${y}`;
        c.setAttribute("aria-label", `Cell ${x} ${y}`);
        c.addEventListener("click", () => onCellClick(x, y));
        cells.appendChild(c);
      }
    }
  }

  function formationArt() {
    const chars = Array.from(FALLBACK_SETUPS[0]);
    $("#formationArt").innerHTML = chars.map(ch => `<span>${ch}</span>`).join("");
  }

  function showToast(text) {
    const t = $("#toast");
    t.textContent = text;
    t.classList.add("visible");
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => t.classList.remove("visible"), 2300);
  }

  function parseSetupLibrary(text) {
    const trimmed = text.trim();
    const found = [];

    try {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed)) {
        for (const s of parsed) if (typeof s === "string" && VALID_SETUP_RE.test(s.trim())) found.push(s.trim());
      }
      if (parsed && parsed.kind === "stratego-save") return { save: parsed };
    } catch (_) {}

    for (const m of trimmed.matchAll(/["']([¶s¹²3456789o]{40})["']/gu)) found.push(m[1]);
    for (const line of trimmed.split(/\s+/u)) if (VALID_SETUP_RE.test(line)) found.push(line);

    return { setups: [...new Set(found)] };
  }

  function hydrateSave(save) {
    if (!save || save.kind !== "stratego-save" || !save.state) throw new Error("This is not a Stratego savegame.");
    state = save.state;
    state.loadedAt = new Date().toISOString();
    state.board = Array.isArray(state.board) && state.board.length === 100 ? state.board : Array(100).fill(null);
    state.pieces = state.pieces || {};
    state.memory = state.memory || { red: {}, blue: {} };
    state.log = state.log || [];
    state.history = state.history || [];
    state.graveyard = state.graveyard || [];
    state.ready = state.ready || { red: true, blue: true };
    state.setupSourceCount = state.setupSourceCount || setupSourceCount;
    nextPieceNo = 1 + Math.max(0, ...Object.keys(state.pieces).map(id => Number(id.match(/-(\d+)$/)?.[1] || 0)));
    selected = null;
    busy = false;
    showGame();
    render();
    maybeRunAI();
  }

  async function createNewGame(opts) {
    nextPieceNo = 1;
    const aiSide = opts.opponentType === "ai" ? other(opts.humanSide) : null;
    const pair = localSetupLibrary?.length
      ? { red: rand(localSetupLibrary), blue: rand(localSetupLibrary), count: localSetupLibrary.length }
      : await serverSetupPair();
    setupSourceCount = pair.count || setupSourceCount;

    state = {
      kind: "stratego-state",
      version: 1,
      createdAt: new Date().toISOString(),
      phase: "setup",
      mode: opts.infoMode,
      turn: 1,
      activeSide: "red",
      setupSide: opts.opponentType === "ai" ? opts.humanSide : "red",
      humanSide: opts.humanSide,
      opponentType: opts.opponentType,
      aiSide,
      aiDifficulty: opts.aiDifficulty,
      ready: { red: aiSide === "red", blue: aiSide === "blue" },
      players: {
        red: { name: opts.redName || "Red", type: aiSide === "red" ? "ai" : "human" },
        blue: { name: opts.blueName || "Blue", type: aiSide === "blue" ? "ai" : "human" }
      },
      board: Array(100).fill(null),
      pieces: {},
      memory: { red: {}, blue: {} },
      log: [],
      history: [],
      graveyard: [],
      lastMove: null,
      winner: null,
      setupSourceCount
    };

    placeArmy("blue", pair.blue || await randomSetup());
    placeArmy("red", pair.red || await randomSetup());
    addLog(`Deployment begins. Red and Blue armies were drawn from ${setupSourceCount.toLocaleString()} setup pattern${setupSourceCount === 1 ? "" : "s"}.`);
    saveSnapshot("initial deployment");
    showGame();
    render();
  }

  function makePiece(side, ch, x, y) {
    const id = `${side}-${nextPieceNo++}`;
    state.pieces[id] = { id, side, ch, x, y, alive: true, revealedTo: { red: side === "red", blue: side === "blue" } };
    state.board[idx(x, y)] = id;
    return state.pieces[id];
  }

  function clearArmy(side) {
    for (const p of Object.values(state.pieces)) {
      if (p.side === side && p.alive) state.board[idx(p.x, p.y)] = null;
    }
    for (const id of Object.keys(state.pieces)) if (state.pieces[id].side === side) delete state.pieces[id];
  }

  function placeArmy(side, setupLine) {
    const chars = Array.from(setupLine.trim());
    if (chars.length !== 40) throw new Error("Setup must contain 40 symbols.");
    clearArmy(side);

    // Setup strings are ordered front row first, then second, third, back row.
    // Red sits at the bottom, so its front row is y=6 and back row is y=9.
    // Blue sits at the top, so its front row is y=3 and back row is y=0.
    let i = 0;
    for (let r = 0; r < 4; r++) {
      const y = side === "blue" ? 3 - r : 6 + r;
      for (let x = 0; x < 10; x++) makePiece(side, chars[i++], x, y);
    }
  }

  async function randomizeArmy(side) {
    placeArmy(side, await randomSetup());
    addLog(`${cap(side)} army was redeployed from the setup library.`);
    selected = null;
    render();
  }

  function showMenu() {
    $("#screenMenu").classList.add("active");
    $("#screenGame").classList.remove("active");
    $("#victoryModal").classList.remove("visible");
    setTitleGameButtons(false);
    updateSetupHint();
  }

  function showGame() {
    $("#screenMenu").classList.remove("active");
    $("#screenGame").classList.add("active");
    setTitleGameButtons(true);
  }

  function setTitleGameButtons(visible) {
    for (const id of ["#saveBtn", "#restartBtn"]) {
      const el = $(id);
      if (el) el.style.display = visible ? "inline-flex" : "none";
    }
  }

  function updateSetupHint() {
    const src = localSetupLibrary?.length ? "browser-loaded local" : "server-loaded";
    $("#setupCountHint").textContent = `Using ${setupSourceCount.toLocaleString()} ${src} setup pattern${setupSourceCount === 1 ? "" : "s"}.`;
  }

  function isLake(x, y) { return LAKES.has(key(x, y)); }
  function pieceAt(x, y) { const id = state?.board[idx(x, y)]; return id ? state.pieces[id] : null; }
  function isMovable(p) { return p && p.alive && !META[p.ch]?.immobile; }
  function isHuman(side) { return state.players[side]?.type !== "ai"; }
  function viewerSide() {
    if (!state) return "red";
    if (state.phase === "setup") return state.setupSide;
    if (state.opponentType === "ai") return state.humanSide;
    return state.activeSide;
  }

  function displayChar(p, viewer) {
    if (!p) return "";
    if (p.side === viewer) return p.ch;
    if (state.mode === "revelations" && p.revealedTo?.[viewer]) return p.ch;
    return "?";
  }

  function validMovesFrom(x, y, side = null) {
    const p = pieceAt(x, y);
    if (!p || !p.alive || !isMovable(p)) return [];
    if (side && p.side !== side) return [];
    const moves = [];
    const add = (tx, ty) => {
      if (!inBounds(tx, ty) || isLake(tx, ty)) return false;
      const q = pieceAt(tx, ty);
      if (q?.side === p.side) return false;
      moves.push({ id: p.id, from: { x, y }, to: { x: tx, y: ty }, attack: !!q });
      return !q;
    };

    if (META[p.ch].scout) {
      for (const [dx, dy] of DIRS) {
        let tx = x + dx, ty = y + dy;
        while (inBounds(tx, ty) && !isLake(tx, ty)) {
          const canContinue = add(tx, ty);
          if (!canContinue) break;
          tx += dx; ty += dy;
        }
      }
    } else {
      for (const [dx, dy] of DIRS) add(x + dx, y + dy);
    }
    return moves;
  }

  function allValidMoves(side) {
    const moves = [];
    for (const p of Object.values(state.pieces)) {
      if (p.side === side && p.alive && isMovable(p)) moves.push(...validMovesFrom(p.x, p.y, side));
    }
    return moves;
  }

  function sameCell(a, b) { return a && b && a.x === b.x && a.y === b.y; }
  function moveMatches(m, x, y) { return m.to.x === x && m.to.y === y; }

  function render() {
    if (!state) return;
    renderHud();
    renderCells();
    renderPieces();
    renderSidePanels();
  }

  function renderHud() {
    const v = viewerSide();
    const setup = state.phase === "setup";
    const gameOver = state.phase === "gameover";
    const active = state.activeSide;
    $("#turnBadge").textContent = setup ? `${cap(state.setupSide)} deployment` : gameOver ? "Battle concluded" : `Turn ${state.turn} · ${cap(active)} to move`;
    $("#viewerBadge").textContent = `Viewing ${cap(v)}`;
    $("#phaseHelp").textContent = setup
      ? `${state.players[state.setupSide].name}: swap pieces within your first four rows, randomize if desired, then confirm readiness.`
      : gameOver
        ? `${state.players[state.winner].name} controls the field.`
        : isHuman(active) || state.opponentType === "human"
          ? `Select one of ${cap(active)}'s movable pieces, then choose a highlighted destination or enemy target.`
          : `${state.players[active].name} is considering a move.`;
    $("#setupActions").style.display = setup ? "flex" : "none";
    $("#readyBtn").textContent = `${cap(state.setupSide)} ready`;
    $("#switchSetupBtn").style.display = state.opponentType === "human" ? "inline-flex" : "none";
    $("#suggestBtn").disabled = busy || state.phase !== "play" || !isHuman(state.activeSide);
    $("#saveBtn").disabled = !state;
    $("#randomizeBtn").disabled = state.ready[state.setupSide] || busy;
  }

  function renderCells() {
    const valid = selected ? validMovesFrom(selected.x, selected.y, state.phase === "play" ? state.activeSide : null) : [];
    for (const c of $$(".cell")) {
      const x = Number(c.dataset.x), y = Number(c.dataset.y);
      const p = pieceAt(x, y);
      const classes = ["cell"];
      if (isLake(x, y)) classes.push("lake");
      if (y <= 3) classes.push("setup-blue");
      if (y >= 6) classes.push("setup-red");
      if (selected && selected.x === x && selected.y === y) classes.push("selected");
      const vm = valid.find(m => moveMatches(m, x, y));
      if (vm) classes.push(p && p.side !== selected.side ? "attack-target" : "valid");
      if (state.lastMove && (sameCell(state.lastMove.from, {x,y}) || sameCell(state.lastMove.to, {x,y}))) classes.push("last-move");
      c.className = classes.join(" ");
      c.disabled = busy || state.phase === "gameover" || isLake(x, y);
    }
  }

  function renderPieces() {
    const viewer = viewerSide();
    const pieces = Object.values(state.pieces).filter(p => p.alive);
    $("#pieceLayer").innerHTML = pieces.map(p => pieceHtml(p, viewer, "piece", `id=\"piece-${p.id}\"`)).join("");
  }

  function pieceHtml(p, viewer, baseClass = "piece", extra = "") {
    const shown = displayChar(p, viewer);
    const hidden = shown === "?";
    const title = hidden ? `${cap(p.side)} unknown piece` : `${cap(p.side)} ${pieceName(p.ch)} at ${p.x} ${p.y}`;
    const pulse = selected && selected.id === p.id ? " pulse" : "";
    return `<div class="${baseClass} ${p.side}${hidden ? " hidden" : ""}${pulse}" ${extra} style="--x:${p.x};--y:${p.y}" title="${escapeHtml(title)}"><div class="piece-inner">${escapeHtml(shown)}</div></div>`;
  }

  function renderSidePanels() {
    const v = viewerSide();
    $("#redStat").textContent = playerSummary("red");
    $("#blueStat").textContent = playerSummary("blue");
    $("#modeStat").textContent = state.mode === "classic" ? "Classic" : "Revelations";
    $("#setupsStat").textContent = String(state.setupSourceCount || setupSourceCount);

    const enemy = other(v);
    const chips = [];
    for (const p of Object.values(state.pieces)) {
      if (!p.alive || p.side !== enemy) continue;
      const known = knownCharFor(v, p);
      if (known) chips.push(`<span class="intel-chip">${known} · ${pieceName(known)} · ${p.x} ${p.y}</span>`);
    }
    $("#intelHelp").textContent = state.mode === "classic"
      ? "Classic mode keeps enemy pieces face-down; this list is the commander's remembered combat intel. AI commanders can misremember."
      : "Revelations mode keeps identified enemy pieces visible to both players.";
    $("#intelList").innerHTML = chips.length ? chips.join("") : `<span class="hint">No enemy ranks known yet.</span>`;

    const dead = state.graveyard.slice(-40).reverse().map(g => `<span class="dead-chip">${g.ch} ${cap(g.side)}</span>`);
    $("#graveyard").innerHTML = dead.length ? dead.join("") : `<span class="hint">None yet.</span>`;
    $("#log").innerHTML = state.log.slice(-80).reverse().map(e => `<div class="log-entry">${renderLogEntry(e, v)}</div>`).join("");
  }

  function playerSummary(side) {
    const live = Object.values(state.pieces).filter(p => p.side === side && p.alive);
    const movable = live.filter(isMovable);
    return `${live.length} pieces · ${movable.length} movable`;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[ch]));
  }

  function setupRowBelongs(side, y) { return side === "blue" ? y >= 0 && y <= 3 : y >= 6 && y <= 9; }

  function onCellClick(x, y) {
    if (!state || busy || state.phase === "gameover" || isLake(x, y)) return;
    if (state.phase === "setup") return onSetupClick(x, y);
    if (state.phase !== "play" || !isHuman(state.activeSide)) return;
    onPlayClick(x, y);
  }

  function onSetupClick(x, y) {
    const side = state.setupSide;
    if (state.ready[side]) return showToast(`${cap(side)} is already ready.`);
    if (!setupRowBelongs(side, y)) return showToast(`Use only ${cap(side)}'s four setup rows.`);
    const p = pieceAt(x, y);
    if (!selected) {
      if (!p || p.side !== side) return;
      selected = { id: p.id, side, x, y };
      render();
      return;
    }
    if (selected.x === x && selected.y === y) { selected = null; render(); return; }
    const q = pieceAt(x, y);
    if (!q || q.side !== side) return showToast("Select another friendly piece to swap positions.");
    const a = state.pieces[selected.id];
    swapPieces(a, q);
    addLog({ type: "setup-swap", side, a: { x: q.x, y: q.y }, b: { x: a.x, y: a.y } });
    selected = null;
    render();
  }

  function swapPieces(a, b) {
    const ax = a.x, ay = a.y;
    state.board[idx(a.x, a.y)] = b.id;
    state.board[idx(b.x, b.y)] = a.id;
    a.x = b.x; a.y = b.y;
    b.x = ax; b.y = ay;
  }

  function onPlayClick(x, y) {
    const p = pieceAt(x, y);
    if (!selected) {
      if (!p || p.side !== state.activeSide) return;
      if (!isMovable(p)) return showToast(`${pieceName(p.ch)} cannot move.`);
      selected = { id: p.id, side: p.side, x, y };
      render();
      return;
    }

    if (selected.x === x && selected.y === y) { selected = null; render(); return; }

    const valid = validMovesFrom(selected.x, selected.y, state.activeSide);
    const move = valid.find(m => moveMatches(m, x, y));
    if (move) return performMove(move, "human");

    if (p && p.side === state.activeSide && isMovable(p)) {
      selected = { id: p.id, side: p.side, x, y };
      render();
      return;
    }
    showToast("That move is not legal.");
  }

  async function performMove(move, actor = "human") {
    if (busy || state.phase !== "play") return;
    busy = true;
    selected = null;
    $("#suggestionText").textContent = "";
    render();

    const attacker = state.pieces[move.id];
    if (!attacker || !attacker.alive) { busy = false; render(); return; }
    const defender = pieceAt(move.to.x, move.to.y);
    await animateMove(attacker, move.from, move.to);
    revealScoutMoveIfNeeded(attacker, move);

    if (!defender) {
      movePieceState(attacker, move.to.x, move.to.y);
      state.lastMove = clone(move);
      addLog({ type: "move", pieceId: attacker.id, side: attacker.side, from: clone(move.from), to: clone(move.to) });
      afterAction();
      return;
    }

    revealForCombat(attacker, defender);
    render();
    await showCombat(attacker, defender, "Ranks revealed.");
    const result = resolveCombat(attacker, defender, move);
    await burst(move.to.x, move.to.y);
    state.lastMove = clone(move);
    render();
    await showCombat(attacker, defender, result.text);
    $("#combatModal").classList.remove("visible");

    if (result.winner) {
      endGame(result.winner, result.text);
      return;
    }
    afterAction();
  }

  async function animateMove(piece, from, to) {
    const viewer = viewerSide();
    const original = document.getElementById(`piece-${piece.id}`);
    if (original) original.classList.add("moving-source");

    const fx = $("#fxLayer");
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "move-vector");
    svg.setAttribute("viewBox", "0 0 100 100");
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", String(from.x * 10 + 5));
    line.setAttribute("y1", String(from.y * 10 + 5));
    line.setAttribute("x2", String(to.x * 10 + 5));
    line.setAttribute("y2", String(to.y * 10 + 5));
    svg.appendChild(line);
    fx.appendChild(svg);

    const cloneEl = document.createElement("div");
    cloneEl.innerHTML = pieceHtml(piece, viewer, "moving-piece", "");
    const mover = cloneEl.firstElementChild;
    mover.style.setProperty("--x", from.x);
    mover.style.setProperty("--y", from.y);
    mover.style.setProperty("--dx", `${(to.x - from.x) * 100}%`);
    mover.style.setProperty("--dy", `${(to.y - from.y) * 100}%`);
    fx.appendChild(mover);

    await sleep(660);
    svg.remove();
    mover.remove();
    if (original) original.classList.remove("moving-source");
  }

  async function burst(x, y) {
    const fx = document.createElement("div");
    fx.className = "boom";
    fx.style.setProperty("--x", x);
    fx.style.setProperty("--y", y);
    $("#fxLayer").appendChild(fx);
    await sleep(620);
    fx.remove();
  }

  async function showCombat(att, def, text) {
    $("#combatTitle").textContent = "Combat resolution";
    $("#attackerCard").innerHTML = cardHtml(att, "Attacker");
    $("#defenderCard").innerHTML = cardHtml(def, "Defender");
    $("#combatResult").textContent = text;
    $("#combatModal").classList.add("visible");
    await sleep(820);
  }

  function cardHtml(p, role) {
    const aliveText = p.alive ? `${p.x} ${p.y}` : "captured";
    return `<div class="hint">${role} · ${cap(p.side)}</div><div class="big">${escapeHtml(p.ch)}</div><b>${pieceName(p.ch)}</b><div class="hint">${aliveText}</div>`;
  }

  function revealForCombat(att, def) {
    for (const side of ["red", "blue"]) {
      if (att.side !== side) remember(side, att);
      if (def.side !== side) remember(side, def);
      if (state.mode === "revelations") {
        att.revealedTo[side] = true;
        def.revealedTo[side] = true;
      }
    }
  }

  function revealScoutMoveIfNeeded(piece, move) {
    const distance = Math.abs(move.to.x - move.from.x) + Math.abs(move.to.y - move.from.y);
    if (piece.ch !== "¹" || distance <= 1) return;
    const observer = other(piece.side);
    rememberKnown(observer, piece, "¹");
    if (state.mode === "revelations") {
      piece.revealedTo.red = true;
      piece.revealedTo.blue = true;
    }
  }

  function rememberKnown(observer, piece, ch = piece.ch) {
    if (observer === piece.side) return;
    state.memory[observer][piece.id] = { ch, actual: ch === piece.ch, confidence: 1, turn: state.turn };
  }

  function remember(observer, piece) {
    if (observer === piece.side) return;
    const player = state.players[observer];
    if (player.type === "ai" && state.mode === "classic") {
      const profile = AI_PROFILES[state.aiDifficulty] || AI_PROFILES.normal;
      const roll = Math.random();
      if (roll > profile.memory) return;
      const falseRoll = Math.random();
      const remembered = falseRoll < profile.falseMemory ? rand(SYMBOLS.filter(ch => ch !== piece.ch)) : piece.ch;
      state.memory[observer][piece.id] = { ch: remembered, actual: remembered === piece.ch, confidence: profile.memory, turn: state.turn };
    } else {
      state.memory[observer][piece.id] = { ch: piece.ch, actual: true, confidence: 1, turn: state.turn };
    }
  }

  function knownCharFor(observer, piece) {
    if (!piece || observer === piece.side) return piece?.ch || null;
    if (state.mode === "revelations" && piece.revealedTo?.[observer]) return piece.ch;
    const mem = state.memory?.[observer]?.[piece.id];
    if (!mem || mem.confidence <= 0.14) return null;
    return mem.ch;
  }

  function resolveCombat(att, def, move) {
    let text = "";
    let gameWinner = null;

    const kill = p => {
      if (!p || !p.alive) return;
      p.alive = false;
      state.board[idx(p.x, p.y)] = null;
      state.graveyard.push({ side: p.side, ch: p.ch, id: p.id, turn: state.turn });
    };

    const attackerWins = reason => { kill(def); movePieceState(att, move.to.x, move.to.y); text = `${cap(att.side)} ${pieceName(att.ch)} defeats ${cap(def.side)} ${pieceName(def.ch)}. ${reason}`; };
    const defenderWins = reason => { kill(att); text = `${cap(def.side)} ${pieceName(def.ch)} defeats ${cap(att.side)} ${pieceName(att.ch)}. ${reason}`; };
    const bothFall = reason => { kill(att); kill(def); text = `Both pieces are removed. ${reason}`; };

    if (def.ch === "¶") {
      kill(def);
      movePieceState(att, move.to.x, move.to.y);
      gameWinner = att.side;
      text = `${cap(att.side)} captured the flag.`;
    } else if (def.ch === "o") {
      if (att.ch === "²") attackerWins("Miner defuses Bomb.");
      else defenderWins("Bomb destroys the attacker.");
    } else if (att.ch === "s" && def.ch === "9") {
      attackerWins("Spy ambushes Marshal.");
    } else {
      const ap = META[att.ch].power, dp = META[def.ch].power;
      if (ap > dp) attackerWins("Higher rank prevails.");
      else if (ap < dp) defenderWins("Higher rank prevails.");
      else bothFall("Equal ranks clash.");
    }

    addLog({
      type: "attack",
      attackerId: att.id,
      defenderId: def.id,
      attackerSide: att.side,
      defenderSide: def.side,
      from: clone(move.from),
      to: clone(move.to),
      text
    });
    return { winner: gameWinner, text };
  }

  function movePieceState(p, x, y) {
    state.board[idx(p.x, p.y)] = null;
    p.x = x; p.y = y;
    state.board[idx(x, y)] = p.id;
  }

  function afterAction() {
    const enemy = other(state.activeSide);
    decayAIMemory();
    saveSnapshot("turn action");
    if (!hasAnyMoves(enemy)) { endGame(state.activeSide, `${cap(enemy)} has no movable legal pieces remaining.`); return; }
    state.activeSide = enemy;
    state.turn += 1;
    busy = false;
    render();
    if (!hasAnyMoves(state.activeSide)) endGame(other(state.activeSide), `${cap(state.activeSide)} has no movable legal pieces remaining.`);
    else maybeRunAI();
  }

  function hasAnyMoves(side) { return allValidMoves(side).length > 0; }

  function decayAIMemory() {
    for (const side of ["red", "blue"]) {
      if (state.players[side]?.type !== "ai") continue;
      const profile = AI_PROFILES[state.aiDifficulty] || AI_PROFILES.normal;
      for (const [id, m] of Object.entries(state.memory[side] || {})) {
        if (!state.pieces[id]?.alive) delete state.memory[side][id];
        else m.confidence = Math.max(0, m.confidence - profile.decay);
      }
    }
  }

  function endGame(winner, reason) {
    state.phase = "gameover";
    state.winner = winner;
    busy = false;
    selected = null;
    addLog(`Victory: ${state.players[winner].name}. ${reason}`);
    saveSnapshot("victory");
    render();
    $("#victoryTitle").textContent = `${state.players[winner].name} wins`;
    $("#victoryText").textContent = reason;
    $("#victoryModal").classList.add("visible");
    confetti();
  }

  function confetti() {
    for (let i = 0; i < 120; i++) {
      const d = document.createElement("div");
      d.className = "confetti";
      d.style.left = `${Math.random() * 100}vw`;
      d.style.background = i % 4 === 0 ? "#d6aa50" : i % 4 === 1 ? "#ef7870" : i % 4 === 2 ? "#73a2ff" : "#f4ead4";
      d.style.setProperty("--dx", `${(Math.random() - 0.5) * 180}px`);
      d.style.setProperty("--dur", `${2.2 + Math.random() * 2.2}s`);
      document.body.appendChild(d);
      setTimeout(() => d.remove(), 4800);
    }
  }

  function saveSnapshot(label) {
    const compactPieces = Object.fromEntries(Object.values(state.pieces).map(p => [p.id, {
      side: p.side, ch: p.ch, x: p.x, y: p.y, alive: p.alive, revealedTo: p.revealedTo
    }]));
    state.history.push({ label, turn: state.turn, activeSide: state.activeSide, at: new Date().toISOString(), board: [...state.board], pieces: compactPieces });
  }

  function addLog(entry) {
    const turn = state?.turn || 0;
    state.log.push(typeof entry === "string" ? { type: "text", turn, text: entry } : { turn, ...entry });
  }

  function renderLogEntry(entry, viewer) {
    if (typeof entry === "string") return escapeHtml(entry); // compatibility with old exported saves
    const prefix = `[${String(entry.turn || 0).padStart(3, "0")}]`;
    if (entry.type === "text") return escapeHtml(`${prefix} ${entry.text}`);
    if (entry.type === "setup-swap") {
      return escapeHtml(`${prefix} ${cap(entry.side)} swapped two deployment pieces at ${entry.a.x} ${entry.a.y} and ${entry.b.x} ${entry.b.y}.`);
    }
    if (entry.type === "move") {
      const p = state.pieces[entry.pieceId];
      const label = pieceLogLabel(p, viewer, entry.side);
      return escapeHtml(`${prefix} ${label} moved from ${entry.from.x} ${entry.from.y} to ${entry.to.x} ${entry.to.y}.`);
    }
    if (entry.type === "attack") {
      const att = state.pieces[entry.attackerId];
      const def = state.pieces[entry.defenderId];
      const attLabel = pieceLogLabel(att, viewer, entry.attackerSide);
      const defLabel = pieceLogLabel(def, viewer, entry.defenderSide);
      const outcome = redactedCombatOutcome(att, def, entry, viewer);
      return escapeHtml(`${prefix} ${attLabel} attacked ${defLabel} from ${entry.from.x} ${entry.from.y} to ${entry.to.x} ${entry.to.y}. ${outcome}`);
    }
    return escapeHtml(`${prefix} ${entry.text || "Log entry."}`);
  }

  function pieceLogLabel(piece, viewer, fallbackSide = "") {
    const side = piece?.side || fallbackSide || "unknown";
    if (!piece) return `${cap(side)} piece`;
    if (piece.side === viewer) return `${cap(piece.side)} ${pieceName(piece.ch)}`;
    const known = knownCharFor(viewer, piece);
    return known ? `${cap(piece.side)} ${pieceName(known)}` : `${cap(piece.side)} unidentified piece`;
  }

  function redactedCombatOutcome(att, def, entry, viewer) {
    if (!att || !def) return "Combat was resolved.";
    const attLabel = pieceLogLabel(att, viewer, entry.attackerSide);
    const defLabel = pieceLogLabel(def, viewer, entry.defenderSide);
    if (!att.alive && !def.alive) return "Both pieces were removed.";
    if (att.alive && !def.alive) return `${attLabel} took the square.`;
    if (!att.alive && def.alive) return `${defLabel} held the square.`;
    return "Combat was resolved.";
  }

  function battleOutcomeKnown(attCh, defCh) {
    if (defCh === "¶") return "win";
    if (defCh === "o") return attCh === "²" ? "win" : "lose";
    if (attCh === "s" && defCh === "9") return "win";
    const ap = META[attCh].power, dp = META[defCh].power;
    if (ap > dp) return "win";
    if (ap < dp) return "lose";
    return "both";
  }

  function evaluateMove(move, side) {
    const profile = AI_PROFILES[state.aiDifficulty] || AI_PROFILES.normal;
    const p = state.pieces[move.id];
    const target = pieceAt(move.to.x, move.to.y);
    let score = 0;
    const reasons = [];
    const add = (n, r) => { score += n; if (r) reasons.push(r); };

    if (target) {
      const known = knownCharFor(side, target);
      if (known) {
        if (known === "¶") add(10000, "capture known flag");
        else if (known === "o") add(p.ch === "²" ? 120 : -150 * profile.caution, p.ch === "²" ? "miner defuses known bomb" : "avoid known bomb");
        else {
          const outcome = battleOutcomeKnown(p.ch, known);
          if (p.ch === "s" && known === "9") add(190, "spy ambushes known marshal");
          else if (outcome === "win") add(70 + META[known].power * 4 - META[p.ch].power, `attack weaker known ${pieceName(known)}`);
          else if (outcome === "both") add(18 + META[known].power * 2, `trade with known ${pieceName(known)}`);
          else add(-70 * profile.caution - META[p.ch].power * 5, `avoid stronger known ${pieceName(known)}`);
        }
      } else {
        add(14 * profile.aggression + Math.min(28, META[p.ch].power * 2.2), "probe unknown enemy");
        if (p.ch === "¹") add(10, "scout reconnaissance");
        if (p.ch === "²") add(8, "miner tests defensive line");
        if (["8", "9"].includes(p.ch)) add(-8 * profile.caution, "preserve senior officer against unknown");
      }
    } else {
      add(progressScore(p, move.to, side), "improve position");
      add(centerScore(move.to), "central pressure");
      add(targetHuntScore(p, move, side), null);
      add(flagShieldPenalty(p, move), null);
    }

    add(Math.random() * profile.noise, null);
    return { move, score, reason: reasons.slice(0, 3).join("; ") || "positional move" };
  }

  function progressScore(p, to, side) {
    const direction = side === "red" ? -1 : 1;
    const dy = (to.y - p.y) * direction;
    return dy * (p.ch === "²" ? 7 : p.ch === "s" ? 4 : 5);
  }

  function centerScore(to) {
    const d = Math.abs(4.5 - to.x) + Math.abs(4.5 - to.y);
    return Math.max(0, 10 - d * 1.6);
  }

  function targetHuntScore(p, move, side) {
    let bonus = 0;
    const enemyPieces = Object.values(state.pieces).filter(q => q.alive && q.side !== side);
    for (const q of enemyPieces) {
      const known = knownCharFor(side, q);
      if (!known) continue;
      const before = manhattan(p, q);
      const after = Math.abs(move.to.x - q.x) + Math.abs(move.to.y - q.y);
      if (p.ch === "²" && (known === "o" || known === "¶")) bonus += (before - after) * 15;
      if (p.ch === "s" && known === "9") bonus += (before - after) * 24;
      if (["8", "9"].includes(p.ch) && ["s", "¹", "²", "3", "4", "5"].includes(known)) bonus += (before - after) * 4;
    }
    return bonus;
  }

  function flagShieldPenalty(p, move) {
    const ownFlag = Object.values(state.pieces).find(q => q.alive && q.side === p.side && q.ch === "¶");
    if (!ownFlag) return 0;
    const before = manhattan(p, ownFlag);
    const after = Math.abs(move.to.x - ownFlag.x) + Math.abs(move.to.y - ownFlag.y);
    if (["o", "¶"].includes(p.ch)) return 0;
    return after > before && before <= 2 ? -5 : 0;
  }

  function manhattan(a, b) { return Math.abs(a.x - b.x) + Math.abs(a.y - b.y); }

  function pickMove(side) {
    const moves = allValidMoves(side);
    if (!moves.length) return null;
    return moves.map(m => evaluateMove(m, side)).sort((a, b) => b.score - a.score)[0];
  }

  async function maybeRunAI() {
    if (!state || state.phase !== "play" || busy) return;
    if (state.players[state.activeSide]?.type !== "ai") return;
    busy = true;
    selected = null;
    render();
    await sleep(620);
    busy = false;
    const choice = pickMove(state.activeSide);
    if (!choice) return endGame(other(state.activeSide), `${cap(state.activeSide)} has no legal move.`);
    $("#suggestionText").textContent = `${state.players[state.activeSide].name}: ${choice.reason}.`;
    await sleep(320);
    performMove(choice.move, "ai");
  }

  function suggestMove() {
    if (!state || state.phase !== "play" || !isHuman(state.activeSide)) return;
    const choice = pickMove(state.activeSide);
    if (!choice) return;
    selected = { ...choice.move.from, id: choice.move.id, side: state.activeSide };
    $("#suggestionText").textContent = `Suggested: ${coord(choice.move.from)} → ${coord(choice.move.to)} (${choice.reason}).`;
    render();
  }

  function confirmReady() {
    if (!state || state.phase !== "setup") return;
    state.ready[state.setupSide] = true;
    addLog(`${cap(state.setupSide)} commander confirmed readiness.`);
    selected = null;

    if (!state.ready.red) state.setupSide = "red";
    else if (!state.ready.blue) state.setupSide = "blue";
    else {
      state.phase = "play";
      state.activeSide = "red";
      addLog("Battle begins. Red moves first.");
      saveSnapshot("battle begins");
    }
    render();
    maybeRunAI();
  }

  function switchSetupSide() {
    if (!state || state.phase !== "setup" || state.opponentType !== "human") return;
    state.setupSide = other(state.setupSide);
    selected = null;
    render();
  }

  function exportSave() {
    if (!state) return;
    const save = { kind: "stratego-save", app: "flask-stratego", exportedAt: new Date().toISOString(), state };
    const blob = new Blob([JSON.stringify(save, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `stratego-save-turn-${state.turn}.json`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  async function loadTinyDemoSave() {
    await createNewGame({ opponentType: "ai", humanSide: "red", redName: "Red Marshal", blueName: "Blue AI", aiDifficulty: "normal", infoMode: "classic" });
  }

  function wireEvents() {
    $("#menuForm").addEventListener("submit", async ev => {
      ev.preventDefault();
      const opponentType = $("#opponentType").value;
      const humanSide = $("#humanSide").value;
      const aiSide = other(humanSide);
      const redName = $("#redName").value.trim() || (aiSide === "red" ? "Red AI" : "Red Marshal");
      const blueName = $("#blueName").value.trim() || (aiSide === "blue" ? "Blue AI" : "Blue Marshal");
      await createNewGame({ opponentType, humanSide, redName, blueName, aiDifficulty: $("#aiDifficulty").value, infoMode: $("#infoMode").value });
    });

    $("#fileInput").addEventListener("change", async ev => {
      const file = ev.target.files?.[0];
      if (!file) return;
      const text = await file.text();
      try {
        const parsed = parseSetupLibrary(text);
        if (parsed.save) {
          hydrateSave(parsed.save);
          showToast("Savegame loaded.");
        } else if (parsed.setups?.length) {
          localSetupLibrary = parsed.setups;
          setupSourceCount = localSetupLibrary.length;
          updateSetupHint();
          showToast(`${setupSourceCount.toLocaleString()} local setup patterns loaded.`);
        } else {
          showToast("No setup patterns or savegame found in that file.");
        }
      } catch (err) {
        showToast(err.message || "Could not load file.");
      } finally {
        ev.target.value = "";
      }
    });

    $("#loadSampleSave").addEventListener("click", loadTinyDemoSave);
    $("#readyBtn").addEventListener("click", confirmReady);
    $("#randomizeBtn").addEventListener("click", () => randomizeArmy(state.setupSide));
    $("#switchSetupBtn").addEventListener("click", switchSetupSide);
    $("#suggestBtn").addEventListener("click", suggestMove);
    $("#saveBtn").addEventListener("click", exportSave);
    $("#restartBtn").addEventListener("click", showMenu);
    $("#victoryMenuBtn").addEventListener("click", showMenu);

    document.addEventListener("keydown", ev => {
      if (ev.key === "Escape") { selected = null; render(); }
      if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "s") { ev.preventDefault(); exportSave(); }
    });
  }

  buildBoardCells();
  formationArt();
  updateSetupHint();
  wireEvents();
})();
</script>
</body>
</html>
'''


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
