"""
Regression tests for the preset levels in temple_trap.config.LEVELS.

These costs were captured from a known-good run of astar_solver and are
pinned here so future refactors of engine.py / solver.py can't silently
change the optimal cost (or break solvability) without a test failing.
"""
import pytest

from temple_trap.config import LEVELS
from temple_trap.engine import GameState
from temple_trap.solver import astar_solver, serialize_state

EXPECTED_COSTS = {
    "starter-1": 11,
    "starter-2": 9,
    "starter-3": 10,
    "starter-4": 12,
    "junior-1": 14,
    "junior-2": 15,
    "junior-3": 15,
    "junior-4": 17,
    "expert-1": 12,
    "expert-2": 14,
    "expert-3": 15,
    "expert-4": 14,
}


def make_state(level_name):
    lvl = LEVELS[level_name]
    return GameState(lvl["board"].copy(), lvl["pawn_pos"], "Ground", lvl["orientation"].copy())


@pytest.mark.parametrize("level_name", list(LEVELS.keys()))
def test_level_is_solvable_with_expected_cost(level_name):
    gs = make_state(level_name)
    path, cost, nodes_expanded = astar_solver(gs)

    assert path is not None, f"{level_name} should be solvable"
    assert cost == EXPECTED_COSTS[level_name], (
        f"{level_name}: expected optimal cost {EXPECTED_COSTS[level_name]}, got {cost}"
    )
    assert nodes_expanded > 0


@pytest.mark.parametrize("level_name", list(LEVELS.keys()))
def test_solution_path_cost_matches_reported_total(level_name):
    """Re-walk the returned path step by step and check the sum of
    individual step costs equals the solver's reported total cost."""
    gs = make_state(level_name)
    path, total_cost, _ = astar_solver(gs)
    assert path is not None

    running_cost = 0
    for action, arg in path:
        if action == "slide":
            assert gs.can_slide(arg), f"{level_name}: illegal slide in solution path"
            gs.slide(arg)
            running_cost += 1
        elif action == "walk":
            dest_idx, dest_layer, walk_cost = arg
            gs.pawn = dest_idx
            gs.layer = dest_layer
            running_cost += walk_cost
        else:
            pytest.fail(f"Unknown action type: {action}")

    assert running_cost == total_cost


@pytest.mark.parametrize("level_name", list(LEVELS.keys()))
def test_final_state_is_at_exit(level_name):
    """After replaying the solution, the pawn should be at cell 0 with
    its 'IV' (left) side open on its current layer -- the actual escape
    condition, not just 'index 0'."""
    gs = make_state(level_name)
    path, _, _ = astar_solver(gs)
    assert path is not None

    for action, arg in path:
        if action == "slide":
            gs.slide(arg)
        elif action == "walk":
            dest_idx, dest_layer, _ = arg
            gs.pawn = dest_idx
            gs.layer = dest_layer

    assert gs.pawn == 0
    tile0 = gs.tile_at(0)
    assert "IV" in gs.tile_sides_open(tile0, gs.layer, gs.rotations[0])
