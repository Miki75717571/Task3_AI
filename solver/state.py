MOVES = {
'U': (-1, 0),
'D': (1, 0),
'L': (0, -1),
'R': (0, 1)
}


def idx_to_rc(idx, C):
    return divmod(idx, C)


def rc_to_idx(r, c, C):
    return r * C + c


def goal_state(R, C):
    vals = list(range(1, R*C))
    vals.append(0)
    return tuple(vals)