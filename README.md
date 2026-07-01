<div align="center">

# 🏛️ Temple Trap Solver

**A logical tile-sliding maze — formalized as a state-space search problem and solved with A\*.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Pygame](https://img.shields.io/badge/Pygame-2.6%2B-green?logo=python)](https://pygame.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?logo=flask)](https://flask.palletsprojects.com)
[![pytest](https://img.shields.io/badge/Tests-43%20passing-brightgreen?logo=pytest)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[▶ Run Locally](#-running-locally) · [🌐 Web UI](#-web-ui) · [🧩 How It Works](#-how-it-works) · [📊 Performance](#-performance) · [🗺️ Levels](#️-levels)

</div>

---

## 🎯 What Is Temple Trap?

Temple Trap is a two-layer sliding-tile puzzle. You have a **3 × 3 grid** of tiles (plus one blank slot) and a **pawn** that must escape through the exit at cell 0. Two types of moves are available at each turn:

- **Slide** — swap any tile adjacent to the blank with the blank (the pawn's tile is locked in place).
- **Walk** — move the pawn to an adjacent tile, but only if both tiles have their shared wall open *and* they are on the same floor (or connected via a stair tile).

The puzzle has **two floors**: Ground and Top. Pawn location, tile arrangement, and tile rotation all affect which moves are legal.

---

## 🧩 How It Works

### Tiles

| Symbol | Letter | Type | Floors | Has Holes | Stair |
|--------|--------|------|--------|-----------|-------|
| `=` | A | Top-only | Top: I, II | ✗ | ✗ |
| `◻` | B | Top-only | Top: I, II | ✗ | ✗ |
| `+` | C | Top-only | Top: II, IV | ✗ | ✗ |
| `◊` | D | Stair | Top: IV · Ground: II | ✓ | ✓ |
| `∗` | E | Stair | Top: IV · Ground: II | ✓ | ✓ |
| `▷` | F | Ground-only | Ground: I, II | ✓ | ✗ |
| `X` | G | Ground-only | Ground: I, II | ✓ | ✗ |
| `O` | H | Ground-only | Ground: I, II | ✓ | ✗ |

Side labels (I = North, II = East, III = South, IV = West) rotate with the tile.

### Goal Condition

The puzzle is **solved** when the pawn reaches **cell 0** while on the **Top floor**, and tile at cell 0 has its **West side (IV) open** — meaning there is a walkable exit to the left.

### Walk Connectivity

Two adjacent tiles are walkable between if both have the shared wall open on the active layer. Stair tiles (`◊`, `∗`) additionally let the pawn switch floors for free while standing on them.

---

## 🔍 Search Algorithms

### A\* (Primary — used to generate solutions)

Uses the evaluation function **f(s) = g(s) + h(s)** where:
- **g(s)** = cost paid so far (each slide or walk step = 1).
- **h(s)** = heuristic estimate of remaining cost (see below).

Two key optimizations are applied:
1. **Single BFS pass per node** — `pawn_distances()` runs a 0-1-BFS once and is shared between the goal check and successor generation, eliminating redundant traversals.
2. **Nodes-expanded counter** — every solve reports `nodes_expanded` so you can compare heuristic quality at a glance.

### Heuristics

| Name | Formula | Admissible | Notes |
|------|---------|-----------|-------|
| **Manhattan** | `row(pawn) + col(pawn)` | ✓ | Baseline lower bound |
| **Walk + Floor** | Manhattan + 2 if on Ground at cell 0 | ✓ | Goal requires Top floor, so a ground pawn at exit needs ≥ 2 extra moves |
| **Combined** | Walk/Floor + min-slide-distance of nearest valid exit tile | ✓ | Tightest bound; exit tile must have side IV open on rotation |

### Other Algorithms (for benchmarking)

| Algorithm | Optimal | Space | Notes |
|-----------|---------|-------|-------|
| **BFS** | ✓ | O(b^d) | Uniform cost, high memory |
| **IDS** | ✓ | O(d) | Re-explores shallow levels; uses transposition table |
| **A\* (Manhattan)** | ✓ | O(b^d) | Weak heuristic, more nodes than Combined |
| **A\* (Combined)** | ✓ | O(b^d) | Best performance in practice |

---

## 📊 Performance

Benchmark on a 12-move optimal puzzle:

| Algorithm | Path Length | Nodes Expanded | Notes |
|-----------|-------------|----------------|-------|
| **A\* Combined** | 12 ✓ | **52** | Best — guided directly to goal |
| **A\* Manhattan** | 12 ✓ | ~80 | Weaker heuristic, more exploration |
| **BFS** | 12 ✓ | 99 | Optimal but unguided |
| **IDS** | 12 ✓ | 775 | Optimal + low memory, but re-expands shallow levels |

Full results across all 12 preset levels (A\* with Manhattan, after solver refactor):

| Level | Optimal Cost | Nodes Expanded |
|-------|-------------|----------------|
| starter-1 | 11 | 93 |
| starter-2 | 9 | 58 |
| starter-3 | 10 | 121 |
| starter-4 | 12 | 215 |
| junior-1 | 14 | 501 |
| junior-2 | 15 | 306 |
| junior-3 | 15 | 299 |
| junior-4 | 17 | 726 |
| expert-1 | 12 | 228 |
| expert-2 | 14 | 151 |
| expert-3 | 15 | 484 |
| expert-4 | 14 | 321 |

---

## 🗺️ Levels

Three difficulty tiers, four levels each:

```
Starter  →  starter-1, starter-2, starter-3, starter-4
Junior   →  junior-1,  junior-2,  junior-3,  junior-4
Expert   →  expert-1,  expert-2,  expert-3,  expert-4
```

Each level specifies the initial tile layout, each tile's rotation (0–3 = 0°–270°), and the pawn's starting cell.

---

## 🚀 Running Locally

**Prerequisites:** Python 3.8+

```bash
git clone https://github.com/Rohitmehtre18/templetrapsolver.git
cd templetrapsolver
pip install -r requirements.txt
```

### Option 1 — Web UI (browser, no display server needed)

```bash
python webapp/app.py
```

Open **http://127.0.0.1:5000** — pick a level, it auto-solves, then play / pause / step / scrub through the solution on canvas.

### Option 2 — Pygame Visualizer (local display required)

```bash
python main.py starter-1
# or just: python main.py   (interactive level picker)
```

Controls: `→` next step · `←` previous step · `Space` auto-play · `R` reset

### Option 3 — Benchmark all algorithms

```bash
python main.py --benchmark
```

Prints a table comparing BFS, IDS, and all three A\* heuristic variants (path length, nodes expanded, time in ms).

---

## 🌐 Web UI

A Flask + canvas frontend replaces the need for Pygame or a local display.

**API endpoints:**

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/levels` | Returns sorted list of all level names |
| GET | `/api/solve/<level>` | Runs A\*, returns board state + move list + stats (cached) |

**Frontend features:**
- Dark stone/gold temple theme
- Canvas board renders using the same tile PNGs as Pygame
- Pawn shown as 🔴 (Ground) or 🟡 (Top)
- Play · Pause · Step forward/back · Reset · Scrub slider
- Live move log synced to the current step
- Keyboard: `Space` play/pause · `→`/`←` step

---

## ✅ Tests

```bash
pytest tests/ -q
# 43 passed in ~0.4s
```

| File | What it covers |
|------|---------------|
| `tests/test_engine.py` | Tile rotation, side connectivity, the slide lock rule, stair layer transitions |
| `tests/test_levels.py` | All 12 levels solve; optimal costs pinned; replayed path cost matches; final state satisfies the escape condition |

---

## 📁 Repository Structure

```
templetrapsolver/
│
├── temple_trap/              # Core package
│   ├── assets/               # Tile images (tile_A.png … tile_H.png)
│   ├── __init__.py
│   ├── config.py             # Tile definitions, level layouts, rotation rules
│   ├── engine.py             # GameState, slide/walk mechanics, 0-1-BFS
│   ├── solver.py             # A* (+ BFS / IDS), heuristics, serialization
│   └── visualizer.py         # Pygame rendering pipeline
│
├── webapp/                   # Browser-based visualizer
│   ├── app.py                # Flask backend (API + static file serving)
│   └── static/
│       ├── index.html
│       ├── style.css
│       ├── script.js
│       └── assets/           # Tile images (copied from temple_trap/assets)
│
├── tests/
│   ├── test_engine.py        # Unit tests — engine mechanics
│   └── test_levels.py        # Regression tests — all 12 levels
│
├── docs/
│   └── details_of_temple_trap.pdf
│
├── main.py                   # CLI entry point
├── requirements.txt
└── README.md
```

---

## 🛠️ Key Design Decisions

**Why A\* over plain BFS?**
BFS guarantees optimality but explores uniformly — it can't exploit knowledge of where the exit is. A\* with even a simple Manhattan heuristic cuts nodes expanded by ~40%; the Combined heuristic (accounting for floor + tile orientation) cuts it further.

**Why deduplicate `pawn_distances()` per node?**
The original solver called `reachable_layer_states()` *and then* `pawn_distances()` for every popped node — two full graph traversals producing overlapping information. After the refactor, `pawn_distances()` runs once per node and feeds both the goal check and the successor generator, halving traversal overhead.

**Why a web UI alongside Pygame?**
Pygame requires a local display server, which blocks headless/server/CI use. The Flask + canvas UI exposes the same step-by-step playback without any native window dependency.

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
Made by <a href="https://github.com/Rohitmehtre18">Rohit Mehtre</a>
</div>
