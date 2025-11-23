import sys
from state import idx_to_rc, rc_to_idx, MOVES
import random


# Wczytuje R i C, a następnie R*C liczb
def read_input():
    try:
        # Czytamy R i C z pierwszej linii
        line1 = sys.stdin.readline().strip().split()
        if not line1 or len(line1) != 2:
            print("Error: expected R and C in the first line.", file=sys.stderr)
            sys.exit(1)
        R = int(line1[0])
        C = int(line1[1])
        
        # Czytamy pozostałe dane - R*C liczb
        data = sys.stdin.read().strip().split()
        if len(data) != R * C:
            print(f"Error: expected {R * C} numbers for the puzzle, got {len(data)}", file=sys.stderr)
            sys.exit(1)
        arr = list(map(int, data))
        
        # W kontekście 15-tki (4x4), upewniamy się, że to 4x4
        if R != 4 or C != 4:
            print("Warning: This project focuses on the 15-puzzle (4x4). R and C were read, but R=4 and C=4 are assumed.", file=sys.stderr)
        
        return R, C, tuple(arr)

    except EOFError:
        print("No input", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Invalid input format (expected integers)", file=sys.stderr)
        sys.exit(1)

# generowanie następców (order_spec: np. 'DULR' lub 'R...' dla losowego)
def gen_successors(state, R, C, order_spec=None):
    zero_idx = state.index(0)
    zr, zc = idx_to_rc(zero_idx, C)
    if order_spec and order_spec[0] == 'R':
        order = ['L','R','U','D']
        random.shuffle(order)
    else:
        order = list(order_spec) if order_spec else ['L','R','U','D']
    succ = []
    for m in order:
        dr, dc = MOVES[m]
        nr, nc = zr + dr, zc + dc
        if 0 <= nr < R and 0 <= nc < C:
            nidx = rc_to_idx(nr, nc, C)
            lst = list(state)
            lst[zero_idx], lst[nidx] = lst[nidx], lst[zero_idx]
            succ.append((m, tuple(lst)))
    return succ


# inwersje i sprawdzenie wykonalności (specjalizacja 4x4 działa poprawnie)
def inversion_count(state):
    arr = [x for x in state if x != 0]
    inv = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1
    return inv


def is_solvable(state, R, C, goal=None):
    inv = inversion_count(state)
    if C % 2 == 1:
        if goal is None:
            return inv % 2 == 0
        else:
            return (inv % 2) == (inversion_count(goal) % 2)
    else:
        zr, _ = idx_to_rc(state.index(0), C)
        blank_row_from_bottom = R - zr
        if goal is None:
            return (inv + blank_row_from_bottom) % 2 == 0
        else:
            g_inv = inversion_count(goal)
            gr, _ = idx_to_rc(goal.index(0), C)
            g_blank_row_from_bottom = R - gr
            return ((inv + blank_row_from_bottom) % 2) == ((g_inv + g_blank_row_from_bottom) % 2)