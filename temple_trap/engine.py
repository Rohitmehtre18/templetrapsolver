from collections import deque
from .config import ROWS, COLS, TILES_DEF, ADJ_SIDES

def idx_to_rc(idx):
    return divmod(idx, COLS)

def rc_to_idx(r, c):
    return r * COLS + c

class GameState:
    def __init__(self, tiles, pawn_pos=4, pawn_layer="Ground", rotations=None):
        self.tiles = list(tiles)
        self.blank = self.tiles.index(" ")
        self.pawn = pawn_pos
        self.layer = pawn_layer  
        self.rotations = list(rotations if rotations is not None else [0]*9)

    def tile_at(self, idx):
        return self.tiles[idx]

    def is_within(self, r, c):
        return 0 <= r < ROWS and 0 <= c < COLS

    def neighbor_index(self, idx, dr, dc):
        r, c = idx_to_rc(idx)
        nr, nc = r + dr, c + dc
        if not self.is_within(nr, nc):
            return None
        return rc_to_idx(nr, nc)

    def tile_sides_open(self, tile_id, layer, rotation=0):
        top_opens, ground_opens, _, _ = TILES_DEF[tile_id]
        order = ["I", "II", "III", "IV"]
        def rotate_set(sides):
            return {order[(order.index(s) + rotation) % 4] for s in sides}
        top_rot = rotate_set(top_opens)
        ground_rot = rotate_set(ground_opens)
        return top_rot if layer == "Top" else ground_rot

    def are_connected(self, idx_from, idx_to, layer):
        t_from = self.tile_at(idx_from)
        t_to = self.tile_at(idx_to)
        if t_from == " " or t_to == " ":
            return False

        r1, c1 = idx_to_rc(idx_from)
        r2, c2 = idx_to_rc(idx_to)
        dr, dc = r2 - r1, c2 - c1
        if (dr, dc) not in ADJ_SIDES:
            return False

        side_from, side_to = ADJ_SIDES[(dr, dc)]
        rot_from = self.rotations[idx_from]
        rot_to = self.rotations[idx_to]

        opens_from = self.tile_sides_open(t_from, layer, rot_from)
        opens_to = self.tile_sides_open(t_to, layer, rot_to)

        return (side_from in opens_from) and (side_to in opens_to)

    def can_slide(self, tile_idx):
        if tile_idx == self.blank or self.pawn == tile_idx:
            return False
        r1, c1 = idx_to_rc(tile_idx)
        r2, c2 = idx_to_rc(self.blank)
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return False
        return True

    def slide(self, tile_idx):
        if not self.can_slide(tile_idx):
            return False
        self.tiles[self.blank], self.tiles[tile_idx] = self.tiles[tile_idx], self.tiles[self.blank]
        self.rotations[self.blank], self.rotations[tile_idx] = self.rotations[tile_idx], self.rotations[self.blank]
        self.blank = tile_idx
        return True

    def pawn_distances(self):
        start = (self.pawn, self.layer)
        dq = deque([start])
        dist = {start: 0}

        while dq:
            idx, layer = dq.popleft()
            d = dist[(idx, layer)]

            tile = self.tile_at(idx)
            if TILES_DEF[tile][3]:
                other = (idx, "Top" if layer == "Ground" else "Ground")
                if other not in dist or d < dist[other]:
                    dist[other] = d
                    dq.appendleft(other)

            r, c = idx_to_rc(idx)
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                if not self.is_within(nr, nc): continue
                nidx = rc_to_idx(nr, nc)
                if self.tile_at(nidx) == " ": continue
                if self.are_connected(idx, nidx, layer):
                    nxt = (nidx, layer)
                    if nxt not in dist or d+1 < dist[nxt]:
                        dist[nxt] = d+1
                        dq.append(nxt)
        return dist

    def __str__(self):
        rows = []
        for r in range(ROWS):
            row = self.tiles[r*COLS:(r+1)*COLS]
            rows.append(" | ".join(row))
        return f"Board:\n" + "\n".join(rows) + f"\nPawn:{self.pawn} Layer:{self.layer} Blank:{self.blank}"