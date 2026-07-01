import itertools
import heapq
from .config import TILES_DEF
from .engine import GameState

def manhattan(idx1, idx2):
    r1, c1 = divmod(idx1, 3)
    r2, c2 = divmod(idx2, 3)
    return abs(r1 - r2) + abs(c1 - c2)

def heuristic(gs: GameState):
    return manhattan(gs.pawn, 0)

def serialize_state(gs: GameState):
    return tuple(gs.tiles), tuple(gs.rotations), gs.pawn, gs.layer

def is_goal(gs: GameState, dist_map=None):
    """Checks whether the exit (cell 0, side IV open) is reachable for the
    pawn given the current board. Reuses a single BFS/0-1-BFS pass
    (pawn_distances) for both the reachability check and the walk-cost
    lookup, rather than doing a second full graph traversal."""
    if dist_map is None:
        dist_map = gs.pawn_distances()

    tile0 = gs.tile_at(0)
    best_cost = None
    best_layer = None

    for layer in ("Ground", "Top"):
        key = (0, layer)
        if key not in dist_map:
            continue
        if "IV" not in gs.tile_sides_open(tile0, layer, gs.rotations[0]):
            continue
        cost = dist_map[key]
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_layer = layer

    if best_cost is None:
        return None

    return best_layer, best_cost + 1

def astar_solver(start_gs: GameState, max_steps=200000):
    start_key = serialize_state(start_gs)
    counter = itertools.count()
    open_heap = []
    heapq.heappush(open_heap, (heuristic(start_gs), next(counter), 0, start_gs, []))
    visited = {start_key: 0}
    nodes_expanded = 0

    while open_heap:
        f, _, g, gs, path = heapq.heappop(open_heap)
        nodes_expanded += 1

        dist_map = gs.pawn_distances()

        goal = is_goal(gs, dist_map)
        if goal is not None:
            goal_layer, walk_cost = goal
            final_path = path + [("walk", (0, goal_layer, walk_cost))]
            return final_path, g + walk_cost, nodes_expanded

        if len(visited) > max_steps:
            break

        for (dest_idx, dest_layer), walk_cost in dist_map.items():
            if dest_layer != "Ground" or gs.tile_at(dest_idx) == " ":
                continue
            if not TILES_DEF[gs.tile_at(dest_idx)][2]:
                continue
            if dest_idx == gs.pawn and dest_layer == gs.layer:
                continue

            new_g = g + walk_cost
            new_gs = GameState(gs.tiles.copy(), dest_idx, dest_layer, gs.rotations.copy())
            key = serialize_state(new_gs)
            if key not in visited or new_g < visited[key]:
                visited[key] = new_g
                h = heuristic(new_gs)
                heapq.heappush(open_heap, (new_g + h, next(counter), new_g, new_gs, path + [("walk", (dest_idx, dest_layer, walk_cost))]))

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nidx = gs.neighbor_index(gs.blank, dr, dc)
            if nidx is None or not gs.can_slide(nidx): continue

            new_gs = GameState(gs.tiles.copy(), gs.pawn, gs.layer, gs.rotations.copy())
            new_gs.slide(nidx)
            new_g = g + 1
            key = serialize_state(new_gs)
            if key not in visited or new_g < visited[key]:
                visited[key] = new_g
                h = heuristic(new_gs)
                heapq.heappush(open_heap, (new_g + h, next(counter), new_g, new_gs, path + [("slide", nidx)]))

    return None, -1, nodes_expanded