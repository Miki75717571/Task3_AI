#!/usr/bin/env python3
"""
Comprehensive test suite for 15-puzzle solver.
Tests all algorithms with all heuristics across 3 difficulty levels.
Measures: time, solution length, and optimality.
"""

import subprocess
import sys
import os
import time
import random
from state import goal_state
from utils import generate_shuffled, inversion_count

class TestResult:
    def __init__(self, algo_name, heur_id, difficulty, shuffle_moves, seed):
        self.algo_name = algo_name
        self.heur_id = heur_id
        self.difficulty = difficulty
        self.shuffle_moves = shuffle_moves
        self.seed = seed
        self.solution_length = None
        self.execution_time = None
        self.success = False
        self.error = None

def generate_test_case(difficulty, seed=None):
    """Generate a shuffled puzzle based on difficulty.
    Easy: 5-12 moves, Medium: 12-18 moves, Hard: 18-25 moves.
    (Adjusted for practical testing with uninformed search.)"""
    
    if seed is not None:
        random.seed(seed)
    
    difficulty_ranges = {
        'Easy': (5, 12),
        'Medium': (12, 18),
        'Hard': (18, 25),
    }
    
    min_moves, max_moves = difficulty_ranges.get(difficulty, (5, 15))
    shuffle_count = random.randint(min_moves, max_moves)
    
    R, C = 4, 4
    goal = goal_state(R, C)
    shuffled_state, moves = generate_shuffled(goal, R, C, shuffle_count)
    
    return shuffled_state, shuffle_count

def format_puzzle_input(state, R=4, C=4):
    """Format puzzle state as stdin input."""
    lines = [f"{R} {C}"]
    for i in range(R):
        row = state[i*C:(i+1)*C]
        lines.append(' '.join(map(str, row)))
    return '\n'.join(lines)

def run_single_test(algo_cmd, puzzle_input, timeout=100):
    """Run a single test case and measure time."""
    try:
        start_time = time.time()
        result = subprocess.run(
            algo_cmd,
            input=puzzle_input,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start_time
        
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            try:
                sol_len = int(lines[0])
                if sol_len < 0:
                    return -1, elapsed, False, "No solution"
                return sol_len, elapsed, True, None
            except ValueError:
                return -1, elapsed, False, "Invalid output format"
        else:
            return -1, elapsed, False, "Incomplete output"
    except subprocess.TimeoutExpired:
        return -1, timeout, False, f"Timeout ({timeout}s)"
    except Exception as e:
        return -1, 0.0, False, str(e)

def run_tests():
    """Run comprehensive test suite."""
    print("=" * 180)
    print("COMPREHENSIVE 15-PUZZLE SOLVER TEST SUITE")
    print("Testing all algorithms × all heuristics × 3 difficulty levels")
    print("=" * 180)
    
    # Define test matrix
    difficulties = ['Easy', 'Medium', 'Hard']
    
    # Uninformed search algorithms (order_spec = 'DULR')
    uninformed_algos = [
        ('BFS', ['-b', 'DULR']),
        ('DFS', ['-d', 'DULR']),
        ('IDFS', ['-i', 'DULR']),
    ]
    
    # Heuristics for informed search
    heuristics = ['0', 'misplaced', 'manhattan']
    
    # Informed search algorithms
    informed_algos = [
        ('Best-First', '-f'),
        ('A*', '-a'),
        ('SMA*', '-s'),
    ]
    
    main_script = os.path.join(os.path.dirname(__file__), 'main.py')
    results_by_algo = {}
    all_results = []
    
    test_count = 0
    
    # Generate test cases per difficulty
    test_cases = {}
    for difficulty in difficulties:
        test_cases[difficulty] = []
        for test_num in range(10):  # 10 tests per difficulty
            state, moves = generate_test_case(difficulty, seed=test_num + difficulty.__hash__())
            test_cases[difficulty].append((state, moves))
    
    # ==================== UNINFORMED SEARCH ====================
    print("\n" + "=" * 180)
    print("UNINFORMED SEARCH (No Heuristics)")
    print("=" * 180)
    print(f"{'Algorithm':<12} | {'Difficulty':<10} | {'Test':<4} | {'Shuffle':<8} | {'Solution':<10} | {'Time (s)':<10} | {'Status':<8}")
    print("-" * 180)
    
    for algo_name, cmd_args in uninformed_algos:
        results_by_algo[algo_name] = []
        
        for difficulty in difficulties:
            for test_idx, (state, shuffle_count) in enumerate(test_cases[difficulty]):
                puzzle_input = format_puzzle_input(state)
                full_cmd = [sys.executable, main_script] + cmd_args
                
                # DFS can be slow; use shorter timeout for uninformed search
                timeout_val = 15 if algo_name in ['DFS', 'IDFS'] else 30
                sol_len, exec_time, success, error = run_single_test(full_cmd, puzzle_input, timeout=timeout_val)
                
                result = TestResult(algo_name, 'N/A', difficulty, shuffle_count, test_idx)
                result.solution_length = sol_len
                result.execution_time = exec_time
                result.success = success
                result.error = error
                
                results_by_algo[algo_name].append(result)
                all_results.append(result)
                
                status = "✓ OK" if success else f"✗ {error[:6]}"
                print(f"{algo_name:<12} | {difficulty:<10} | {test_idx:<4} | {shuffle_count:<8} | {sol_len:<10} | {exec_time:<10.4f} | {status:<8}")
                test_count += 1
    
    # ==================== INFORMED SEARCH ====================
    print("\n" + "=" * 180)
    print("INFORMED SEARCH (All Heuristics × All Difficulties)")
    print("=" * 180)
    print(f"{'Algorithm':<15} | {'Heuristic':<12} | {'Difficulty':<10} | {'Test':<4} | {'Shuffle':<8} | {'Solution':<10} | {'Time (s)':<10} | {'Status':<8}")
    print("-" * 180)
    
    for algo_name, algo_flag in informed_algos:
        key = f"{algo_name}"
        results_by_algo[key] = []
        
        for heur in heuristics:
            for difficulty in difficulties:
                for test_idx, (state, shuffle_count) in enumerate(test_cases[difficulty]):
                    puzzle_input = format_puzzle_input(state)
                    
                    # Handle SMA* memory option
                    cmd_args = [algo_flag, heur]
                    if algo_name == 'SMA*':
                        cmd_args.extend(['--max-memory', '10000'])
                    
                    full_cmd = [sys.executable, main_script] + cmd_args
                    
                    # Informed search usually faster; longer timeout for hard cases
                    timeout_val = 30
                    sol_len, exec_time, success, error = run_single_test(full_cmd, puzzle_input, timeout=timeout_val)
                    
                    result = TestResult(algo_name, heur, difficulty, shuffle_count, test_idx)
                    result.solution_length = sol_len
                    result.execution_time = exec_time
                    result.success = success
                    result.error = error
                    
                    if key not in results_by_algo:
                        results_by_algo[key] = []
                    results_by_algo[key].append(result)
                    all_results.append(result)
                    
                    heur_display = 'h=0' if heur == '0' else f'h={heur}'
                    status = "✓ OK" if success else f"✗ {error[:6]}"
                    print(f"{algo_name:<15} | {heur_display:<12} | {difficulty:<10} | {test_idx:<4} | {shuffle_count:<8} | {sol_len:<10} | {exec_time:<10.4f} | {status:<8}")
                    test_count += 1
    
    # ==================== SUMMARY STATISTICS ====================
    print("\n" + "=" * 180)
    print("SUMMARY STATISTICS BY ALGORITHM AND HEURISTIC")
    print("=" * 180)
    print(f"{'Algorithm':<25} | {'Tests':<6} | {'Solved':<6} | {'Avg Time (s)':<12} | {'Avg Solution':<14} | {'Min/Max':<12} | {'Avg Gap %':<10}")
    print("-" * 180)
    
    for algo_key in sorted(results_by_algo.keys()):
        results = results_by_algo[algo_key]
        successful = [r for r in results if r.success and r.solution_length > 0]
        
        total_tests = len(results)
        solved = len(successful)
        
        if successful:
            avg_time = sum(r.execution_time for r in successful) / len(successful)
            avg_sol = sum(r.solution_length for r in successful) / len(successful)
            min_sol = min(r.solution_length for r in successful)
            max_sol = max(r.solution_length for r in successful)
            
            # Calculate optimality gap for each puzzle and average
            gaps = []
            for r in successful:
                puzzle_key = (r.difficulty, r.shuffle_moves, r.seed)
                # Find optimal (minimum) for this puzzle
                min_in_puzzle = min(
                    (res.solution_length for res in all_results 
                     if res.difficulty == r.difficulty and res.shuffle_moves == r.shuffle_moves 
                     and res.seed == r.seed and res.success and res.solution_length > 0),
                    default=r.solution_length
                )
                gap_pct = 0 if r.solution_length == min_in_puzzle else (r.solution_length - min_in_puzzle) / min_in_puzzle * 100
                gaps.append(gap_pct)
            avg_gap = sum(gaps) / len(gaps) if gaps else 0
        else:
            avg_time = 0
            avg_sol = 0
            min_sol = 0
            max_sol = 0
            avg_gap = 0
        
        min_max_str = f"{min_sol}/{max_sol}" if successful else "N/A"
        print(f"{algo_key:<25} | {total_tests:<6} | {solved:<6} | {avg_time:<12.4f} | {avg_sol:<14.1f} | {min_max_str:<12} | {avg_gap:<10.2f}%")

    
    # ==================== DETAILED PER-DIFFICULTY ANALYSIS ====================
    print("\n" + "=" * 180)
    print("DETAILED ANALYSIS BY DIFFICULTY LEVEL")
    print("=" * 180)
    
    for difficulty in difficulties:
        print(f"\n--- {difficulty.upper()} DIFFICULTY ---")
        print(f"{'Algorithm':<25} | {'Heuristic':<12} | {'Success %':<12} | {'Avg Time (s)':<12} | {'Avg Moves':<12} | {'Avg Gap %':<10} | {'Min/Max':<12}")
        print("-" * 180)
        
        difficulty_results = [r for r in all_results if r.difficulty == difficulty]
        
        # Group by algorithm (and heuristic if applicable)
        grouped = {}
        for r in difficulty_results:
            key = (r.algo_name, r.heur_id)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(r)
        
        for (algo, heur), results in sorted(grouped.items()):
            successful = [r for r in results if r.success and r.solution_length > 0]
            success_rate = len(successful) / len(results) * 100 if results else 0
            
            if successful:
                avg_time = sum(r.execution_time for r in successful) / len(successful)
                avg_moves = sum(r.solution_length for r in successful) / len(successful)
                min_moves = min(r.solution_length for r in successful)
                max_moves = max(r.solution_length for r in successful)
                
                # Calculate optimality gap
                gaps = []
                for r in successful:
                    puzzle_key = (r.difficulty, r.shuffle_moves, r.seed)
                    min_in_puzzle = min(
                        (res.solution_length for res in difficulty_results 
                         if res.shuffle_moves == r.shuffle_moves and res.seed == r.seed 
                         and res.success and res.solution_length > 0),
                        default=r.solution_length
                    )
                    gap_pct = 0 if r.solution_length == min_in_puzzle else (r.solution_length - min_in_puzzle) / min_in_puzzle * 100
                    gaps.append(gap_pct)
                avg_gap = sum(gaps) / len(gaps) if gaps else 0
            else:
                avg_time = 0
                avg_moves = 0
                min_moves = 0
                max_moves = 0
                avg_gap = 0
            
            heur_display = 'N/A' if heur == 'N/A' else ('h=0' if heur == '0' else f'h={heur}')
            moves_range = f"{min_moves}/{max_moves}" if successful else "N/A"
            
            print(f"{algo:<25} | {heur_display:<12} | {success_rate:<11.1f}% | {avg_time:<12.4f} | {avg_moves:<12.1f} | {avg_gap:<10.2f}% | {moves_range:<12}")
    
    # ==================== OPTIMALITY ANALYSIS ====================
    print("\n" + "=" * 180)
    print("OPTIMALITY ANALYSIS - Solution Quality Comparison")
    print("=" * 180)
    print("(Shows how many moves more each algorithm used vs. optimal for the same puzzle)")
    print("-" * 180)
    
    # Build optimal solutions per puzzle
    optimal_per_puzzle = {}
    for r in all_results:
        key = (r.difficulty, r.shuffle_moves, r.seed)
        if key not in optimal_per_puzzle:
            optimal_per_puzzle[key] = float('inf')
        if r.success and r.solution_length > 0:
            optimal_per_puzzle[key] = min(optimal_per_puzzle[key], r.solution_length)
    
    # Display optimality details
    print(f"{'Difficulty':<12} | {'Shuffle#':<10} | {'Algorithm(Heur)':<25} | {'Moves':<8} | {'Optimal':<8} | {'Gap Moves':<12} | {'Gap %':<10} | {'Time (s)':<10}")
    print("-" * 180)
    
    for difficulty in difficulties:
        for test_idx in range(10):
            difficulty_tests = [r for r in all_results if r.difficulty == difficulty and r.seed == test_idx]
            if not difficulty_tests:
                continue
            
            shuffle_moves = difficulty_tests[0].shuffle_moves
            key = (difficulty, shuffle_moves, test_idx)
            optimal = optimal_per_puzzle.get(key, float('inf'))
            
            if optimal == float('inf'):
                continue
            
            for r in sorted(difficulty_tests, key=lambda x: (x.algo_name, x.heur_id)):
                if r.success and r.solution_length > 0:
                    gap_moves = r.solution_length - optimal
                    gap_pct = 0 if gap_moves == 0 else (gap_moves / optimal) * 100
                    algo_heur = f"{r.algo_name}({r.heur_id})" if r.heur_id != 'N/A' else r.algo_name
                    status = "✓ OPT" if gap_moves == 0 else f"  +{gap_moves}"
                    print(f"{difficulty:<12} | {shuffle_moves:<10} | {algo_heur:<25} | {r.solution_length:<8} | {optimal:<8} | {status:<12} | {gap_pct:<10.2f}% | {r.execution_time:<10.4f}")

    
    # ==================== FINAL SUMMARY ====================
    print("\n" + "=" * 180)
    print("FINAL SUMMARY")
    print("=" * 180)
    total_tests = len(all_results)
    total_solved = len([r for r in all_results if r.success])
    total_time = sum(r.execution_time for r in all_results if r.success)
    success_rate = total_solved / total_tests * 100 if total_tests > 0 else 0
    
    print(f"Total tests run: {total_tests}")
    print(f"Total solved: {total_solved}/{total_tests} ({success_rate:.1f}%)")
    print(f"Total execution time: {total_time:.2f} s")
    print(f"Average time per test: {total_time/total_tests:.4f} s")
    print("=" * 180 + "\n")

if __name__ == '__main__':
    run_tests()
