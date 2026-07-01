# main.py

import sys
from temple_trap.config import LEVELS
from temple_trap.engine import GameState
from temple_trap.solver import astar_solver
from temple_trap.visualizer import GameVisualizer

def run_level(level_name):
    if level_name not in LEVELS:
        print(f"Error: Layout identifier '{level_name}' matches no presets.")
        return

    lvl = LEVELS[level_name]
    solver_state = GameState(lvl['board'].copy(), lvl['pawn_pos'], "Ground", lvl['orientation'].copy())
    vis_state = GameState(lvl['board'].copy(), lvl['pawn_pos'], "Ground", lvl['orientation'].copy())

    print(f"\nProcessing structural map: {level_name}...")
    solution_path, total_cost, nodes_expanded = astar_solver(solver_state)

    if solution_path:
        # --- Print out steps to console (Matches your exact final.py format) ---
        print("\nSolution Path Found:")
        path_cost_verification = 0
        for i, (action, arg) in enumerate(solution_path, 1):
            if action == "slide":
                print(f"Step {i}: SLIDE tile at {arg} (cost = 1)")
                path_cost_verification += 1
            elif action == "walk":
                idx, layer, wcost = arg
                print(f"Step {i}: WALK pawn to cell {idx} on {layer} (cost = {wcost})")
                path_cost_verification += wcost

        print(f"\nTOTAL COST = {total_cost}  (nodes expanded: {nodes_expanded})")
        print("-----------------------------------------------------------------")
        print("💡 Click on the Pygame display window and press [SPACEBAR] or")
        print("   [RIGHT ARROW] to advance the moves visually step-by-step.")
        print("-----------------------------------------------------------------\n")
        
        # Launch Pygame Visualizer
        viz = GameVisualizer()
        viz.play_solution(vis_state, solution_path)
    else:
        print("❌ Search constraints exceeded. No valid solutions mapped.")

if __name__ == "__main__":
    available = list(LEVELS.keys())
    if len(sys.argv) > 1:
        run_level(sys.argv[1])
    else:
        print("Available Puzzle Levels Layouts:")
        for idx, lvl in enumerate(available, 1):
            print(f" [{idx}] {lvl}")
        choice = input("\nSelect level index or type string key layout: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(available):
            run_level(available[int(choice) - 1])
        elif choice in available:
            run_level(choice)