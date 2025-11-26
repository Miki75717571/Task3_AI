from state import idx_to_rc


def h_zero(state, R, C, goal_pos):
    return 0


def h_misplaced(state, R, C, goal_pos):
    count = 0
    for idx, val in enumerate(state):
        if val != 0 and goal_pos[val] != idx:
            count += 1
    return count


def h_manhattan(state, R, C, goal_pos):
    s = 0
    for idx, val in enumerate(state):
        if val != 0:
            gr, gc = idx_to_rc(goal_pos[val], C)
            r, c = idx_to_rc(idx, C)
            s += abs(r - gr) + abs(c - gc)
    return s

def h_linear_conflict(state, R, C, goal_pos):
    """
    Linear Conflict = Manhattan Distance + 2 * (#conflicts)
    """
    manhattan = h_manhattan(state, R, C, goal_pos)
    conflicts = 0

    # --- Row conflicts ---
    for row in range(R):
        tiles = []
        for col in range(C):
            idx = row * C + col
            val = state[idx]
            if val != 0:
                gr, gc = idx_to_rc(goal_pos[val], C)
                if gr == row:  # tile belongs to this row
                    tiles.append((col, gc))

        # Now detect conflicts in tiles: (current_col, goal_col)
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                _, goal_i = tiles[i]
                _, goal_j = tiles[j]
                if goal_i > goal_j:  # reversed order
                    conflicts += 1

    # --- Column conflicts ---
    for col in range(C):
        tiles = []
        for row in range(R):
            idx = row * C + col
            val = state[idx]
            if val != 0:
                gr, gc = idx_to_rc(goal_pos[val], C)
                if gc == col:  # tile belongs to this column
                    tiles.append((row, gr))

        # Detect conflicts: (current_row, goal_row)
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                _, goal_i = tiles[i]
                _, goal_j = tiles[j]
                if goal_i > goal_j:
                    conflicts += 1

    return manhattan + 2 * conflicts