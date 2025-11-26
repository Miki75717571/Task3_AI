#!/usr/bin/env python3
# test_suite.py
"""
Kompleksowy zestaw testów dla solvera łamigłówki 15.
Każdy algorytm testowany z każdą heurystyką na 3 poziomach trudności.
"""

import subprocess
import sys
import os
import time
from collections import defaultdict

class TestCase:
    def __init__(self, name, puzzle_input, algorithm, params, heuristic=None, difficulty=None):
        self.name = name
        self.puzzle_input = puzzle_input
        self.algorithm = algorithm
        self.params = params
        self.heuristic = heuristic
        self.difficulty = difficulty

def run_test(test_case, main_script_path):
    """Uruchamia pojedynczy test i mierzy czas."""
    try:
        cmd = [sys.executable, main_script_path] + test_case.params
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            input=test_case.puzzle_input,
            capture_output=True,
            text=True,
            timeout=60
        )
        elapsed_time = (time.time() - start_time) * 1000  # ms
        
        output_lines = result.stdout.strip().split('\n')
        moves_count = int(output_lines[0]) if output_lines[0] else -1
        
        is_solvable = moves_count >= 0
        return is_solvable, moves_count, elapsed_time
        
    except subprocess.TimeoutExpired:
        return False, -1, 60000
    except Exception as e:
        return False, -1, 0

def print_test_section(title):
    """Drukuje nagłówek sekcji."""
    print("\n" + "="*120)
    print(f"  {title}")
    print("="*120)
    print(f"{'Test Name':<50} | {'Difficulty':<12} | {'Status':<6} | {'Moves':<6} | {'Time (ms)':<12}")
    print("-"*120)

def print_test_result(test_name, difficulty, success, moves, elapsed_time):
    """Drukuje wynik pojedynczego testu."""
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{test_name:<50} | {difficulty:<12} | {status:<6} | {moves:<6} | {elapsed_time:<12.2f}")

def get_test_cases():
    """Zwraca wszystkie przypadki testowe."""
    
    # Trzy poziomy trudności
    puzzles = {
        'Easy': {
            'BFS': "4 4\n1 0 2 3\n4 5 6 7\n8 9 10 11\n12 13 14 15\n",
            'DFS': "4 4\n1 0 2 3\n4 5 6 7\n8 9 10 11\n12 13 14 15\n",
            'IDFS': "4 4\n1 0 2 3\n4 5 6 7\n8 9 10 11\n12 13 14 15\n",
            'BF': "4 4\n1 0 2 3\n4 5 6 7\n8 9 10 11\n12 13 14 15\n",
            'AStar': "4 4\n1 0 2 3\n4 5 6 7\n8 9 10 11\n12 13 14 15\n",
            'SMA': "4 4\n1 0 2 3\n4 5 6 7\n8 9 10 11\n12 13 14 15\n",
        },
        'Medium': {
            'BFS': "4 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n13 14 0 15\n",
            'DFS': "4 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n13 14 0 15\n",
            'IDFS': "4 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n13 14 0 15\n",
            'BF': "4 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n13 14 0 15\n",
            'AStar': "4 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n13 14 0 15\n",
            'SMA': "4 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n13 14 0 15\n",
        },
        'Hard': {
            'BFS': "4 4\n5 1 2 3\n4 6 7 8\n9 10 11 12\n13 14 0 15\n",
            'DFS': "4 4\n5 1 2 3\n4 6 7 8\n9 10 11 12\n13 14 0 15\n",
            'IDFS': "4 4\n5 1 2 3\n4 6 7 8\n9 10 11 12\n13 14 0 15\n",
            'BF': "4 4\n5 1 2 3\n4 6 7 8\n9 10 11 12\n13 14 0 15\n",
            'AStar': "4 4\n5 1 2 3\n4 6 7 8\n9 10 11 12\n13 14 0 15\n",
            'SMA': "4 4\n5 1 2 3\n4 6 7 8\n9 10 11 12\n13 14 0 15\n",
        }
    }
    
    heuristics = ['0', 'misplaced', 'manhattan']
    tests = {}
    
    # BFS - bez heurystyk, tylko różne kolejności
    tests['BFS'] = []
    for difficulty in ['Easy', 'Medium', 'Hard']:
        tests['BFS'].append(TestCase(
            f"BFS ({difficulty})", puzzles[difficulty]['BFS'], 
            "BFS", ["-b", "DULR"], heuristic=None, difficulty=difficulty
        ))
    
    # DFS - bez heurystyk, tylko różne kolejności
    tests['DFS'] = []
    for difficulty in ['Easy', 'Medium', 'Hard']:
        tests['DFS'].append(TestCase(
            f"DFS ({difficulty})", puzzles[difficulty]['DFS'],
            "DFS", ["-d", "DULR"], heuristic=None, difficulty=difficulty
        ))
    
    # IDFS - bez heurystyk
    tests['IDFS'] = []
    for difficulty in ['Easy', 'Medium', 'Hard']:
        tests['IDFS'].append(TestCase(
            f"IDFS ({difficulty})", puzzles[difficulty]['IDFS'],
            "IDFS", ["-i", "DULR", "--max-depth", "50"], heuristic=None, difficulty=difficulty
        ))
    
    # Best-First - z wszystkimi heurystykami
    tests['Best-First'] = []
    for heur in heuristics:
        for difficulty in ['Easy', 'Medium', 'Hard']:
            heur_name = f"h={heur}" if heur != '0' else "h=0"
            tests['Best-First'].append(TestCase(
                f"Best-First + {heur_name} ({difficulty})", puzzles[difficulty]['BF'],
                "Best-First", ["-f", heur], heuristic=heur_name, difficulty=difficulty
            ))
    
    # A* - z wszystkimi heurystykami
    tests['A*'] = []
    for heur in heuristics:
        for difficulty in ['Easy', 'Medium', 'Hard']:
            heur_name = f"h={heur}" if heur != '0' else "h=0"
            tests['A*'].append(TestCase(
                f"A* + {heur_name} ({difficulty})", puzzles[difficulty]['AStar'],
                "A*", ["-a", heur], heuristic=heur_name, difficulty=difficulty
            ))
    
    # SMA* - z wszystkimi heurystykami
    tests['SMA*'] = []
    for heur in heuristics:
        for difficulty in ['Easy', 'Medium', 'Hard']:
            heur_name = f"h={heur}" if heur != '0' else "h=0"
            tests['SMA*'].append(TestCase(
                f"SMA* + {heur_name} ({difficulty})", puzzles[difficulty]['SMA'],
                "SMA*", ["-s", heur], heuristic=heur_name, difficulty=difficulty
            ))
    
    return tests

def main():
    """Główna funkcja testowa."""
    if len(sys.argv) < 2:
        print("Użycie: python test_suite.py <ścieżka_do_main.py>")
        sys.exit(1)
    
    main_script = sys.argv[1]
    
    if not os.path.exists(main_script):
        print(f"Błąd: Plik {main_script} nie istnieje!")
        sys.exit(1)
    
    test_cases = get_test_cases()
    results = defaultdict(lambda: {'solved': 0, 'total': 0, 'total_moves': 0, 'total_time': 0.0})
    
    print("\n" + "="*120)
    print("  COMPREHENSIVE 15-PUZZLE TEST SUITE")
    print("  Each Algorithm × Each Heuristic × 3 Difficulty Levels")
    print("="*120)
    
    # ==================== UNINFORMED SEARCH ====================
    print_test_section("1. UNINFORMED SEARCH (No Heuristics)")
    
    for algo in ['BFS', 'DFS', 'IDFS']:
        for test in test_cases[algo]:
            success, moves, elapsed = run_test(test, main_script)
            print_test_result(test.name, test.difficulty, success, moves, elapsed)
            
            # Zapis wyniku
            key = f"{algo}"
            results[key]['total'] += 1
            results[key]['total_time'] += elapsed
            if success:
                results[key]['solved'] += 1
                results[key]['total_moves'] += moves
    
    # ==================== INFORMED SEARCH ====================
    for algo in ['Best-First', 'A*', 'SMA*']:
        print_test_section(f"2. {algo} SEARCH (All Heuristics × All Difficulties)")
        
        for test in test_cases[algo]:
            success, moves, elapsed = run_test(test, main_script)
            print_test_result(test.name, test.difficulty, success, moves, elapsed)
            
            # Wyodrębnianie heurystyki
            heur = test.heuristic if test.heuristic else 'N/A'
            key = f"{algo} ({heur})"
            
            results[key]['total'] += 1
            results[key]['total_time'] += elapsed
            if success:
                results[key]['solved'] += 1
                results[key]['total_moves'] += moves
    
    # ==================== OVERALL PERFORMANCE SUMMARY ====================
    print("\n" + "="*120)
    print("OVERALL PERFORMANCE SUMMARY")
    print("="*120)
    print(f"{'Algorithm':<30} | {'Total Solved':<15} | {'Avg Moves':<12} | {'Avg Time (ms)':<12}")
    print("-"*120)
    
    # Porządek wyświetlania
    display_order = [
        'BFS', 'DFS', 'IDFS',
        'Best-First (h=0)', 'Best-First (h=misplaced)', 'Best-First (h=manhattan)',
        'A* (h=0)', 'A* (h=misplaced)', 'A* (h=manhattan)',
        'SMA* (h=0)', 'SMA* (h=misplaced)', 'SMA* (h=manhattan)'
    ]
    
    for key in display_order:
        if key in results:
            data = results[key]
            solved = data['solved']
            total = data['total']
            avg_moves = data['total_moves'] / solved if solved > 0 else 0
            avg_time = data['total_time'] / total if total > 0 else 0
            
            print(f"{key:<30} | {solved}/{total:<13} | {avg_moves:<12.1f} | {avg_time:<12.4f}")
    
    print("="*120)
    
    # ==================== FINAL STATISTICS ====================
    print("\n" + "="*120)
    print("FINAL STATISTICS")
    print("="*120)
    
    total_tests = sum(data['total'] for data in results.values())
    total_solved = sum(data['solved'] for data in results.values())
    total_execution_time = sum(data['total_time'] for data in results.values())
    
    print(f"Total tests: {total_tests}")
    print(f"Total solved: {total_solved}/{total_tests}")
    print(f"Success rate: {(total_solved/total_tests*100):.1f}%")
    print(f"Total execution time: {total_execution_time:.2f} ms")
    print(f"Average time per test: {(total_execution_time/total_tests):.2f} ms")
    print("="*120 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())