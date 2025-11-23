# main.py
import sys
import argparse
from state import goal_state
from utils import read_input, is_solvable
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
    
    args = parser.parse_args()

    # 2. Wczytanie Danych
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
        solution_path = bfs(start_state, goal_state_tuple, R, C, args.bfs, args.max_nodes)

    elif args.dfs:
        print(f"Uruchamiam DFS z kolejnością: {args.dfs}", file=sys.stderr)
        solution_path = dfs(start_state, goal_state_tuple, R, C, args.dfs, args.max_nodes)

    elif args.idfs:
        print(f"Uruchamiam IDFS z kolejnością: {args.idfs}, Max głębokość: {args.max_depth}", file=sys.stderr)
        solution_path = iddfs(start_state, goal_state_tuple, R, C, args.idfs, args.max_depth, args.max_nodes)

    elif args.bf:
        heur_fn = get_heuristic_fn(args.bf)
        print(f"Uruchamiam Best-First z heurystyką: {args.bf}", file=sys.stderr)
        solution_path = best_first(start_state, goal_state_tuple, R, C, heur_fn, goal_pos, None, args.max_nodes)

    elif args.astar:
        heur_fn = get_heuristic_fn(args.astar)
        print(f"Uruchamiam A* z heurystyką: {args.astar}", file=sys.stderr)
        solution_path = astar(start_state, goal_state_tuple, R, C, heur_fn, goal_pos, None, args.max_nodes)
        
    elif args.sma:
        heur_fn = get_heuristic_fn(args.sma)
        print(f"Uruchamiam SMA* z heurystyką: {args.sma}, Max pamięć: {args.max_memory}", file=sys.stderr)
        solution_path = sma_star(start_state, goal_state_tuple, R, C, heur_fn, goal_pos, None, args.max_nodes, args.max_memory)
        
    # 5. Wypisanie Wyniku
    if solution_path is not None:
        print(len(solution_path))
        print(solution_path)
    else:
        print("-1")
        print("")

if __name__ == '__main__':
    main()