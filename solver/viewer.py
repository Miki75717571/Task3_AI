# viewer.py
import sys
import time
from state import idx_to_rc, rc_to_idx, MOVES
from utils import read_input, gen_successors # Wykorzystujemy te same funkcje pomocnicze

def apply_move(state, move, R, C):
    """Zwraca nowy stan po wykonaniu pojedynczego ruchu."""
    zero_idx = state.index(0)
    zr, zc = idx_to_rc(zero_idx, C)
    
    if move not in MOVES:
        return state, False # Niepoprawny ruch
        
    dr, dc = MOVES[move]
    nr, nc = zr + dr, zc + dc
    
    if 0 <= nr < R and 0 <= nc < C:
        nidx = rc_to_idx(nr, nc, C)
        lst = list(state)
        # Zamiana 0 z sąsiednią płytką
        lst[zero_idx], lst[nidx] = lst[nidx], lst[zero_idx]
        return tuple(lst), True
    else:
        return state, False # Nie można wykonać ruchu (poza ramką)

def print_state(state, R, C):
    """Wypisuje stan łamigłówki w formie siatki."""
    print("+" + "----" * C + "+")
    for r in range(R):
        row_str = "| "
        for c in range(C):
            idx = rc_to_idx(r, c, C)
            val = state[idx]
            row_str += f"{val:2} " if val != 0 else "   "
        print(row_str + "|")
    print("+" + "----" * C + "+")

def viewer_main():
    """Główna funkcja viewera."""
    if len(sys.argv) < 3:
        print("Użycie: python3 viewer.py <ścieżka_do_pliku_wejściowego> <ciąg_ruchów>")
        print("np. python3 viewer.py input.txt DDRR")
        sys.exit(1)
        
    input_file_path = sys.argv[1]
    solution_path = sys.argv[2].strip()

    # Wczytanie stanu początkowego z pliku
    try:
        with open(input_file_path, 'r') as f:
            # Prowizoryczne wczytywanie, musimy nadpisać stdin dla read_input
            sys.stdin = f
            R, C, current_state = read_input()
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {input_file_path}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Przywrócenie stdin do standardowego wejścia
        sys.stdin = sys.__stdin__

    print(f"--- START WIZUALIZACJI (Ruchów: {len(solution_path)}) ---")
    print(f"Ruch: Start (0/{len(solution_path)})")
    print_state(current_state, R, C)
    
    # Opcja dla interaktywnego przejścia lub przejścia ze skokami (jak w poleceniu)
    
    step = 0
    # Główna pętla viewera
    while step < len(solution_path):
        next_move = solution_path[step]
        
        # Oczekiwanie na akcję użytkownika (Enter - następny ruch, J<liczba> - skok)
        user_input = input("Wciśnij [Enter] (następny ruch), [J<liczba>] (skok), lub [Q] (wyjdź): ").strip().upper()
        
        if user_input == 'Q':
            break
        
        target_step = step + 1 # Domyślnie - następny krok
        
        if user_input.startswith('J'):
            try:
                # Wczytanie docelowego kroku do skoku
                jump_target = int(user_input[1:])
                if 0 <= jump_target <= len(solution_path):
                    target_step = jump_target
                else:
                    print(f"Niepoprawny numer kroku dla skoku. Podaj liczbę od 0 do {len(solution_path)}.", file=sys.stderr)
                    continue
            except ValueError:
                print("Niepoprawny format skoku. Użyj formatu J<liczba> (np. J5).", file=sys.stderr)
                continue
        
        # Iteracyjne wykonanie ruchów do osiągnięcia target_step
        while step < target_step:
            if step >= len(solution_path):
                break # Doszliśmy do końca
                
            next_move = solution_path[step]
            
            new_state, success = apply_move(current_state, next_move, R, C)
            if success:
                current_state = new_state
                step += 1
            else:
                print(f"Błąd: Niepoprawny ruch '{next_move}' w kroku {step+1}. Przerywam.", file=sys.stderr)
                return

        # Wyświetlenie aktualnego stanu po skoku/kroku
        print(f"\n--- KROK {step}/{len(solution_path)} ---")
        if step > 0:
            print(f"Ostatni ruch: {solution_path[step-1]}")
        print_state(current_state, R, C)
        
        if step == len(solution_path):
            print("\n--- ROZWIĄZANIE OSIĄGNIĘTE ---")


if __name__ == '__main__':
    viewer_main()