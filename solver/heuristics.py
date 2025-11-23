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