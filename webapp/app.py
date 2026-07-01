"""
Flask backend for the Temple Trap web UI.

Exposes the existing solver (temple_trap.solver.astar_solver) as a small
JSON API and serves a static single-page frontend that animates the
solution on an HTML canvas -- a browser-based replacement for the
Pygame visualizer, usable without a local display / Pygame install.

Run with:
    python webapp/app.py
then open http://127.0.0.1:5000
"""
import os
import sys
import time

from flask import Flask, jsonify, send_from_directory

# Allow running this file directly (python webapp/app.py) by adding the
# project root to sys.path so `import temple_trap` works either way.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from temple_trap.config import LEVELS
from temple_trap.engine import GameState
from temple_trap.solver import astar_solver

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

SYMBOL_TO_LETTER = {
    "=": "A", "◻": "B", "+": "C", "◊": "D",
    "∗": "E", "▷": "F", "X": "G", "O": "H", " ": None,
}

# Simple in-process cache so repeated requests for the same level don't
# re-run A* every time (the levels are small but no reason to redo work).
_solve_cache = {}


def build_state(level_name):
    lvl = LEVELS[level_name]
    return GameState(lvl["board"].copy(), lvl["pawn_pos"], "Ground", lvl["orientation"].copy())


def solve_level(level_name):
    if level_name in _solve_cache:
        return _solve_cache[level_name]

    gs = build_state(level_name)
    t0 = time.perf_counter()
    path, cost, nodes_expanded = astar_solver(gs)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    lvl = LEVELS[level_name]
    result = {
        "level": level_name,
        "board": lvl["board"],
        "orientation": lvl["orientation"],
        "pawn_pos": lvl["pawn_pos"],
        "symbol_to_letter": SYMBOL_TO_LETTER,
        "solved": path is not None,
        "total_cost": cost,
        "nodes_expanded": nodes_expanded,
        "solve_time_ms": round(elapsed_ms, 2),
        "steps": [],
    }

    if path:
        for action, arg in path:
            if action == "slide":
                result["steps"].append({"action": "slide", "tile_idx": arg})
            else:
                dest_idx, dest_layer, walk_cost = arg
                result["steps"].append({
                    "action": "walk",
                    "dest_idx": dest_idx,
                    "dest_layer": dest_layer,
                    "cost": walk_cost,
                })

    _solve_cache[level_name] = result
    return result


@app.get("/api/levels")
def api_levels():
    return jsonify(sorted(LEVELS.keys()))


@app.get("/api/solve/<level_name>")
def api_solve(level_name):
    if level_name not in LEVELS:
        return jsonify({"error": f"unknown level '{level_name}'"}), 404
    return jsonify(solve_level(level_name))


@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
