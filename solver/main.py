# main.py
import sys
import argparse
import time
from state import goal_state
from utils import read_input, is_solvable, generate_shuffled
from heuristics import h_zero, h_misplaced, h_manhattan
from search_bfs import bfs
from search_dfs import dfs
from search_iddfs import iddfs
from search_bestfirst import best_first
from search_astar import astar
from search_sma import sma_star

def get_heuristic_fn(heuristic_id):
    """Zwraca funkcję heurystyczną na podstawie ID."""
    if heuristic_id == '0':
        return h_zero
    elif heuristic_id == 'misplaced':
        return h_misplaced
    elif heuristic_id == 'manhattan':
        return h_manhattan
    else:
        # Możesz rozszerzyć to o bardziej zaawansowane heurystyki
        raise ValueError(f"Nieznany identyfikator heurystyki: {heuristic_id}. Użyj '0', 'misplaced', lub 'manhattan'.")

def get_goal_pos(goal):
    """Tworzy słownik mapujący wartość płytki na jej docelową pozycję (indeks)."""
    return {val: idx for idx, val in enumerate(goal)}

def main():
    """Główna funkcja programu do rozwiązywania łamigłówki 15."""
    
    # 1. Parsowanie Argumentów Wiersza Poleceń
    parser = argparse.ArgumentParser(description="Program rozwiązujący łamigłówkę 15 za pomocą różnych strategii przeszukiwania.")
    
    # Grupa wzajemnie wykluczających się argumentów dla wyboru strategii
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--bfs', type=str, metavar='order', help="Breadth-first search. 'order' definiuje kolejność następców (np. DULR).")
    group.add_argument('-d', '--dfs', type=str, metavar='order', help="Depth-first search. 'order' definiuje kolejność następców (np. DULR).")
    group.add_argument('-i', '--idfs', type=str, metavar='order', help="Iterative deepenening DFS. 'order' definiuje kolejność następców (np. DULR).")
    group.add_argument('-f', '--bf', type=str, metavar='id_of_heuristic', help="Best-first search. 'id_of_heuristic' to id heurystyki.")   
    group.add_argument('-a', '--astar', type=str, metavar='id_of_heuristic', help="A* search. 'id_of_heuristic' to id heurystyki.")
    group.add_argument('-s', '--sma', type=str, metavar='id_of_heuristic', help="SMA* search. 'id_of_heuristic' to id heurystyki.")
    
    # Argumenty opcjonalne dla Best-first, A*, SMA*
    parser.add_argument('--max-nodes', type=int, default=None, help="Maksymalna liczba węzłów do rozwinięcia (opcjonalne).")
    parser.add_argument('--max-depth', type=int, default=50, help="Maksymalna głębokość dla IDFS (domyślnie 50).")
    parser.add_argument('--max-memory', type=int, default=10000, help="Maksymalny limit pamięci dla SMA* (domyślnie 10000).")
    parser.add_argument('-r', '--randomize', type=int, default=None, help="Liczba losowych ruchów do wykonania od stanu docelowego, aby wygenerować startowy (zapewnia wykonalność).")
    parser.add_argument('--save-viewer', type=str, default=None, help="Ścieżka pliku JSON, do którego zapisać dane do viewer (initial, solution).")
    parser.add_argument('--open-viewer', action='store_true', help="Otwórz przeglądarkę z viewerem i przekaż dane jako payload (base64).")
    
    args = parser.parse_args()

    # 2. Przygotowanie danych: wczytanie lub wygenerowanie losowego startu
    if args.randomize is not None:
        # generujemy 4x4 puzzle od stanu docelowego
        R, C = 4, 4
        goal_state_tuple = goal_state(R, C)
        start_state, shuffle_seq = generate_shuffled(goal_state_tuple, R, C, args.randomize)
        goal_pos = get_goal_pos(goal_state_tuple)
        # pokażemy użytkownikowi w stderr wygenerowaną planszę i sekwencję mieszania
        print("Shuffled grid (generated from goal by random moves):", file=sys.stderr)
        for i in range(R):
            row = start_state[i*C:(i+1)*C]
            print(' '.join(map(str, row)), file=sys.stderr)
        print(f"Shuffle moves ({len(shuffle_seq)}): {shuffle_seq}", file=sys.stderr)
    else:
        # 2. Wczytanie Danych z wejścia
        R, C, start_state = read_input()
        goal_state_tuple = goal_state(R, C)
        goal_pos = get_goal_pos(goal_state_tuple)

    # 3. Sprawdzenie Rozwiązywalności
    if not is_solvable(start_state, R, C, goal_state_tuple):
        print("0")
        print("")
        print("Puzzle nie jest rozwiązywalne!")
        return

    # 4. Wybór i Uruchomienie Strategii
    
    solution_path = None
    
    if args.bfs:
        print(f"Uruchamiam BFS z kolejnością: {args.bfs}", file=sys.stderr)
        t0 = time.time()
        solution_path = bfs(start_state, goal_state_tuple, R, C, args.bfs, args.max_nodes)
        elapsed = time.time() - t0
        print(f"Time taken: {elapsed:.6f} s", file=sys.stderr)

    elif args.dfs:
        print(f"Uruchamiam DFS z kolejnością: {args.dfs}", file=sys.stderr)
        t0 = time.time()
        solution_path = dfs(start_state, goal_state_tuple, R, C, args.dfs, args.max_nodes)
        elapsed = time.time() - t0
        print(f"Time taken: {elapsed:.6f} s", file=sys.stderr)

    elif args.idfs:
        print(f"Uruchamiam IDFS z kolejnością: {args.idfs}, Max głębokość: {args.max_depth}", file=sys.stderr)
        t0 = time.time()
        solution_path = iddfs(start_state, goal_state_tuple, R, C, args.idfs, args.max_depth, args.max_nodes)
        elapsed = time.time() - t0
        print(f"Time taken: {elapsed:.6f} s", file=sys.stderr)

    elif args.bf:
        heur_fn = get_heuristic_fn(args.bf)
        print(f"Uruchamiam Best-First z heurystyką: {args.bf}", file=sys.stderr)
        t0 = time.time()
        solution_path = best_first(start_state, goal_state_tuple, R, C, heur_fn, goal_pos, None, args.max_nodes)
        elapsed = time.time() - t0
        print(f"Time taken: {elapsed:.6f} s", file=sys.stderr)

    elif args.astar:
        heur_fn = get_heuristic_fn(args.astar)
        print(f"Uruchamiam A* z heurystyką: {args.astar}", file=sys.stderr)
        t0 = time.time()
        solution_path = astar(start_state, goal_state_tuple, R, C, heur_fn, goal_pos, None, args.max_nodes)
        elapsed = time.time() - t0
        print(f"Time taken: {elapsed:.6f} s", file=sys.stderr)
        
    elif args.sma:
        heur_fn = get_heuristic_fn(args.sma)
        print(f"Uruchamiam SMA* z heurystyką: {args.sma}, Max pamięć: {args.max_memory}", file=sys.stderr)
        t0 = time.time()
        solution_path = sma_star(start_state, goal_state_tuple, R, C, heur_fn, goal_pos, None, args.max_nodes, args.max_memory)
        elapsed = time.time() - t0
        print(f"Time taken: {elapsed:.6f} s", file=sys.stderr)
        
    # 5. Wypisanie Wyniku
    if solution_path is not None:
        print(len(solution_path))
        print(solution_path)
    else:
        print("-1")
        print("")

    # 6. Integracja z viewerem: zapisz JSON i (opcjonalnie) otwórz viewer z payload
    try:
        import json, base64, webbrowser, urllib.parse, os
        viewer_payload = {
            'R': R,
            'C': C,
            'initial': list(start_state),
            'solution_moves': solution_path if solution_path is not None else '',
            'solution_length': len(solution_path) if solution_path is not None else -1,
        }
        # include shuffle sequence if present
        if 'shuffle_seq' in locals():
            viewer_payload['shuffle_seq'] = shuffle_seq

        if args.save_viewer:
            try:
                with open(args.save_viewer, 'w', encoding='utf-8') as f:
                    json.dump(viewer_payload, f, ensure_ascii=False, indent=2)
                print(f"Viewer JSON saved to: {args.save_viewer}", file=sys.stderr)
            except Exception as e:
                print(f"Failed to save viewer JSON: {e}", file=sys.stderr)

        if args.open_viewer:
            # build base64 payload and open viewer/index.html with ?payload=...
            json_bytes = json.dumps(viewer_payload).encode('utf-8')
            b64 = base64.b64encode(json_bytes).decode('ascii')
            # percent-encode to be safe in file:// URL
            b64q = urllib.parse.quote(b64, safe='')
            # compute file:// URL to viewer/index.html relative to this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # viewer is sibling folder ../viewer/index.html
            viewer_path = os.path.normpath(os.path.join(script_dir, '..', 'viewer', 'index.html'))
            viewer_url = 'file:///' + viewer_path.replace('\\', '/') + '?payload=' + b64q
            print(f"Opening viewer: {viewer_url}", file=sys.stderr)
            webbrowser.open(viewer_url)
    except Exception:
        pass

if __name__ == '__main__':
    main()