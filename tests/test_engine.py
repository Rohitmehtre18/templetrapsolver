"""
Unit tests for the core mechanics in temple_trap.engine.GameState:
tile rotation, side connectivity, the slide "lock rule" (a tile can't
slide into the blank while the pawn stands on it), and stair-tile
layer transitions.
"""
from temple_trap.engine import GameState, idx_to_rc, rc_to_idx


def simple_board():
    # 3x3 board, blank at center (index 4), pawn elsewhere.
    # Symbols come from config.TILES_DEF.
    return ['=', '◻', '+', '◊', ' ', '∗', '▷', 'X', 'O']


def test_idx_rc_roundtrip():
    for idx in range(9):
        r, c = idx_to_rc(idx)
        assert rc_to_idx(r, c) == idx


def test_tile_sides_open_rotation_cycles_through_four_sides():
    gs = GameState(simple_board())
    # '=' has Top-layer sides {I, II} (its Ground sides are empty).
    # A full 360-degree rotation (4 steps) must return to the original set.
    base = gs.tile_sides_open('=', 'Top', rotation=0)
    assert base == {"I", "II"}
    full_turn = gs.tile_sides_open('=', 'Top', rotation=4)
    assert full_turn == base


def test_can_slide_rejects_blank_and_pawn_and_non_adjacent():
    gs = GameState(simple_board(), pawn_pos=3)
    assert gs.blank == 4
    # Can't "slide" the blank itself.
    assert gs.can_slide(4) is False
    # Pawn is standing on tile 3 (the lock rule): can't slide it into blank.
    assert gs.can_slide(3) is False
    # Tile 0 isn't adjacent to the blank (index 4).
    assert gs.can_slide(0) is False
    # Tile 1 is orthogonally adjacent to blank and pawn isn't on it.
    assert gs.can_slide(1) is True


def test_slide_swaps_tile_and_rotation_and_moves_blank():
    gs = GameState(simple_board(), pawn_pos=0, rotations=[0, 1, 2, 0, 3, 0, 0, 0, 0])
    ok = gs.slide(1)
    assert ok is True
    assert gs.blank == 1
    assert gs.tiles[4] == '◻'  # tile that was at index 1 moved into old blank slot
    assert gs.tiles[1] == ' '
    # rotation travels with the tile
    assert gs.rotations[4] == 1
    assert gs.rotations[1] == 3  # old blank's rotation moved to where the tile used to be


def test_lock_rule_prevents_sliding_tile_pawn_stands_on():
    gs = GameState(simple_board(), pawn_pos=1)
    assert gs.can_slide(1) is False
    assert gs.slide(1) is False
    # Board is unchanged.
    assert gs.blank == 4
    assert gs.tiles == simple_board()


def test_stair_tile_allows_layer_switch_via_pawn_distances():
    # Tile 'D' (◊) and 'E' (∗) are marked as stairs (has_stairs=True in TILES_DEF).
    gs = GameState(simple_board(), pawn_pos=3, pawn_layer="Ground")
    dist = gs.pawn_distances()
    # Standing on a stair tile (idx 3 = '◊'), the Top layer at the same
    # index should be reachable at zero extra walk cost.
    assert (3, "Top") in dist
    assert dist[(3, "Top")] == dist[(3, "Ground")]


def test_non_stair_tile_does_not_offer_layer_switch():
    gs = GameState(simple_board(), pawn_pos=0, pawn_layer="Ground")
    dist = gs.pawn_distances()
    # Tile 0 ('=') is not a stair tile, so no Top-layer entry should exist for it
    # unless reached some other way; here it shouldn't appear at all from idx 0 directly.
    assert (0, "Top") not in dist or dist[(0, "Top")] != dist[(0, "Ground")]
