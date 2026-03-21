import threading
import pygame
import random
import time
import tracemalloc
import heapq
from itertools import combinations

pygame.init()

AI_ENABLED = False
CELL_SIZE = 50
CELL_NUMBER = 6
RIGHT_SIDE_SCREEN_TAB = 200
SCREEN_WIDTH = ((CELL_SIZE * CELL_NUMBER) + RIGHT_SIDE_SCREEN_TAB)
SCREEN_HEIGHT = (CELL_SIZE * CELL_NUMBER)
SCREEN_WIDTH_WITHOUT_SIDE_TAB = SCREEN_WIDTH - RIGHT_SIDE_SCREEN_TAB

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Kakurasu Puzzle Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
GOLD = (255, 215, 0)

# Game state data
game_state = {
    "cell_size": CELL_SIZE,
    "cell_number": CELL_NUMBER,
    "problem_cells": {},  # Problem state
    "player_cells": {},  # Player state
    "AI_cells": {},  # AI state
    "row_sums": [],
    "col_sums": []
}

# Gloval variables
AI_can_solve = False
AI_result = False
previous_states = []
TOTAL_CLUES = 0
CLUES_NUMBER = 0
REVEAL_ENABLED = False
AI_ENABLED = False
TEMP = []
show_popup = False
popup_button = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 160, 50)
run = True
popup_text = None
is_win = False
AI_SPEED = 10
AI_STEP_DELAY = 0.05
# seconds between each step shown — change this to speed up/slow down (0 = instant)
PERCENTAGE = 0.0
CURRENT_ALGO = "DFS"

# Display Game Screen
gameScreen = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

_splash = pygame.image.load('images/game_screen.png')
_splash = pygame.transform.scale(_splash, (gameScreen.width, gameScreen.height))
screen.blit(_splash, gameScreen.topleft)
pygame.display.update()
print(f"height: {SCREEN_HEIGHT} width: {SCREEN_WIDTH}")
pygame.time.delay(3000)
screen.fill(GOLD)
pygame.display.update()

# ------------------------------------------------------------------------------------------------
# AI Bot Functions

# Check Ai solution
def check_AI_solution():
    global AI_ENABLED  
    global AI_can_solve
    AI_can_solve = False
    
    for cell, value in game_state["problem_cells"].items():
        if AI_ENABLED:
            if value == 'B' and game_state["player_cells"].get(cell) != 'B':
                # print("Ai can not solve the game")
                AI_can_solve = False
                return False
            if value != 'B' and game_state["player_cells"].get(cell) == 'B':
                # print("Ai can not solve the game")
                AI_can_solve = False
                return False
        else:
            if value == 'B' and game_state["AI_cells"].get(cell) != 'B':
                # print("Ai can not solve the game")
                AI_can_solve = False
                return False
            if value != 'B' and game_state["AI_cells"].get(cell) == 'B':
                # print("Ai can not solve the game")
                AI_can_solve = False
                return False
    AI_ENABLED = False
    AI_can_solve = True
    # print("Ai can solve the game")
    return True

# Generate combinations of numbers from the limited numbers list
def find_combinations(target_sum):
    limited_numbers = range(1, CELL_NUMBER - 1)  # Limited numbers to be used
    possible_combinations = []
    for r in range(1, len(limited_numbers) + 1):
        for combination in combinations(limited_numbers, r):
            if sum(combination) == target_sum:
                possible_combinations.append(combination)
    return possible_combinations

# Remove combination that have X mark in cells
def remove_combination_with_x(combinations, index, axis):
    filtered_combinations = []
    for combination in combinations:
        if AI_ENABLED:
            if not any(game_state["player_cells"][(cell, index)] == 'X' if axis == "row" else game_state["player_cells"][(index, cell)] == 'X' for cell in combination):
                filtered_combinations.append(combination)
        else:
            if not any(game_state["AI_cells"][(cell, index)] == 'X' if axis == "row" else game_state["AI_cells"][(index, cell)] == 'X' for cell in combination):
                filtered_combinations.append(combination)
    return filtered_combinations

# Remove combination that don't have all black cells
def remove_combinations_without_all_black(combinations, black_cells, track):    
    black_combination = []
    if track == "row":
        for cell in black_cells:
            black_combination.append(cell[0])
    elif track == "column":
        for cell in black_cells:
            black_combination.append(cell[1])
            
    filtered_combinations = []
    
    if len(combinations) > 1:
        for combination in combinations:
            if all(cell in combination for cell in black_combination):  # Check if all black cells are present in combination
                filtered_combinations.append(combination)
    else:
        return combinations
    return filtered_combinations

def solve_remaining_combination(rows_combination, cols_combination):
    global game_state
    global AI_ENABLED
    global AI_result
    global previous_states
    global AI_SPEED
    
    AI_result = False
    
    while not AI_result:
        # Remove row combinations with 'X' cells
        new_rows_combination = []
        for row_index, (row_sum, combinations) in enumerate(rows_combination):
            filtered_combinations = None
            if row_sum == 0 or len(combinations) == 1:
                new_rows_combination.append((row_sum, combinations))
            else:
                filtered_combinations = remove_combination_with_x(combinations, row_index + 1, "row")
            
            if filtered_combinations:
                new_rows_combination.append((row_sum, filtered_combinations))
        rows_combination[:] = new_rows_combination

        # Remove column combinations with 'X' cells
        new_cols_combination = []
        for col_index, (col_sum, combinations) in enumerate(cols_combination):
            filtered_combinations = None
            if col_sum == 0 or len(combinations) == 1:
                new_cols_combination.append((col_sum, combinations))
            else:
                filtered_combinations = remove_combination_with_x(combinations, col_index + 1, "col")

            if filtered_combinations:
                new_cols_combination.append((col_sum, filtered_combinations))
        cols_combination[:] = new_cols_combination

        # Remove row combinations without all black cells
        for row_index, (row_sum, combinations) in enumerate(rows_combination):
            black_cells_row = None
            if AI_ENABLED:
                black_cells_row = [cell for cell in game_state["player_cells"] if game_state["player_cells"][cell] == 'B' and cell[1] == row_index + 1]
            else:
                black_cells_row = [cell for cell in game_state["AI_cells"] if game_state["AI_cells"][cell] == 'B' and cell[1] == row_index + 1]
            
            if black_cells_row:
                if filtered_combinations and row_sum != 0 and len(combinations) > 1:
                    filtered_combinations = remove_combinations_without_all_black(combinations, black_cells_row, "row")
                    rows_combination[row_index] = (row_sum, filtered_combinations)
                else:
                    rows_combination[row_index] = (row_sum, combinations)

        # Remove column combinations without all black cells
        for col_index, (col_sum, combinations) in enumerate(cols_combination):
            black_cells_col = None
            if AI_ENABLED:
                black_cells_col = [cell for cell in game_state["player_cells"] if game_state["player_cells"][cell] == 'B' and cell[0] == col_index + 1]
            else:
                black_cells_col = [cell for cell in game_state["AI_cells"] if game_state["AI_cells"][cell] == 'B' and cell[0] == col_index + 1]

            if black_cells_col:
                if filtered_combinations and col_sum != 0:
                    filtered_combinations = remove_combinations_without_all_black(combinations, black_cells_col, "column")
                    cols_combination[col_index] = (col_sum, filtered_combinations)
                else:
                    cols_combination[col_index] = (col_sum, combinations)

        # Check if there's only one remaining combination in a row or column
        for row_index, (row_sum, combinations) in enumerate(rows_combination):
            
            if len(combinations) == 0:
                for col in range(1, CELL_NUMBER - 1):
                    if AI_ENABLED:
                        if game_state["player_cells"][(col, row_index + 1)] == '':
                            game_state["player_cells"][(col, row_index + 1)] = 'X'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
                    else:
                        if game_state["AI_cells"][(col, row_index + 1)] == '':
                            game_state["AI_cells"][(col, row_index + 1)] = 'X'
            
            elif len(combinations) == 1:
                for cell in combinations[0]:
                    if AI_ENABLED:
                        if game_state["player_cells"][(cell, row_index + 1)] == '':
                            game_state["player_cells"][(cell, row_index + 1)] = 'B'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
                    else:
                        if game_state["AI_cells"][(cell, row_index + 1)] == '':
                            game_state["AI_cells"][(cell, row_index + 1)] = 'B'

                # Mark all other cells in the row as 'X'
                for col in range(1, CELL_NUMBER - 1):
                    if col not in combinations[0]:
                        if AI_ENABLED:
                            if game_state["player_cells"][(col, row_index + 1)] == '':
                                game_state["player_cells"][(col, row_index + 1)] = 'X'
                                draw_screen(game_state)
                                pygame.display.update()
                                pygame.time.delay(AI_SPEED)
                        else:
                            if game_state["AI_cells"][(col, row_index + 1)] == '':
                                game_state["AI_cells"][(col, row_index + 1)] = 'X'

        for col_index, (col_sum, combinations) in enumerate(cols_combination):
            if len(combinations) == 0:
                for row in range(1, CELL_NUMBER - 1):
                    if AI_ENABLED:
                        if game_state["player_cells"][(col_index + 1, row)] == '':
                            game_state["player_cells"][(col_index + 1, row)] = 'X'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
                    else:
                        if game_state["AI_cells"][(col_index + 1, row)] == '':
                            game_state["AI_cells"][(col_index + 1, row)] = 'X'
            
            elif len(combinations) == 1:
                for cell in combinations[0]:
                    if AI_ENABLED:
                        if game_state["player_cells"][(col_index + 1, cell)] == '':
                            game_state["player_cells"][(col_index + 1, cell)] = 'B'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
                    else:
                        if game_state["AI_cells"][(col_index + 1, cell)] == '':
                            game_state["AI_cells"][(col_index + 1, cell)] = 'B'
                # Mark all other cells in the column as 'X'
                for row in range(1, CELL_NUMBER - 1):
                    if row not in combinations[0]:
                        if AI_ENABLED:
                            if game_state["player_cells"][(col_index + 1, row)] == '':
                                game_state["player_cells"][(col_index + 1, row)] = 'X'
                                draw_screen(game_state)
                                pygame.display.update()
                                pygame.time.delay(AI_SPEED)
                        else:
                            if game_state["AI_cells"][(col_index + 1, row)] == '':
                                game_state["AI_cells"][(col_index + 1, row)] = 'X'

        # pygame.display.update()
        check_AI_solution()
        previous_states.append(game_state["AI_cells"])
        result = check_last_previous_states(previous_states)

        # Check previous states if same
        if result:
            previous_states = []
            AI_ENABLED = False
            AI_result = True
    return rows_combination, cols_combination

# Check previous state to see if it not changed
def check_last_previous_states(lst):
    if len(lst) < 6:
        return False
    
    # Extract the last 5 elements
    last_five = lst[-6:]
    
    # Check if all elements in last_five are the same
    return all(element == last_five[0] for element in last_five)

def ai_bot():
    global AI_ENABLED
    global AI_SPEED
    
    rows_combination = []
    cols_combination = []

    # Generate all unique combinations for each row and column
    for row_sum in game_state["row_sums"]:
        rows_combination.append((row_sum, find_combinations(row_sum)))

    for col_sum in game_state["col_sums"]:
        cols_combination.append((col_sum, find_combinations(col_sum)))
    
    # Check if only one combination is possible
    for row_index, (row_sum, combinations) in enumerate(rows_combination):
        
        # Mark all other cells in the row as 'X' if no combination have
        if len(combinations) == 0:
            for col in range(1, CELL_NUMBER - 1):
                if AI_ENABLED:
                    if game_state["player_cells"][(col, row_index + 1)] == '':
                        game_state["player_cells"][(col, row_index + 1)] = 'X'
                        draw_screen(game_state)
                        pygame.display.update()
                        pygame.time.delay(AI_SPEED)
                else:
                    if game_state["AI_cells"][(col, row_index + 1)] == '':
                        game_state["AI_cells"][(col, row_index + 1)] = 'X'
        
        elif len(combinations) == 1:
            if AI_ENABLED:
                for cell in combinations[0]:
                    if game_state["player_cells"][(cell, row_index + 1)] == '':
                        game_state["player_cells"][(cell, row_index + 1)] = 'B'
                        draw_screen(game_state)
                        pygame.display.update()
                        pygame.time.delay(AI_SPEED)

                # Mark all other cells in the row as 'X'
                for col in range(1, CELL_NUMBER - 1):
                    if col not in combinations[0]:
                        if game_state["player_cells"][(col, row_index + 1)] == '':
                            game_state["player_cells"][(col, row_index + 1)] = 'X'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
            else:
                for cell in combinations[0]:
                    if game_state["AI_cells"][(cell, row_index + 1)] == '':
                        game_state["AI_cells"][(cell, row_index + 1)] = 'B'

                # Mark all other cells in the row as 'X'
                for col in range(1, CELL_NUMBER - 1):
                    if col not in combinations[0]:
                        if game_state["AI_cells"][(col, row_index + 1)] == '':
                            game_state["AI_cells"][(col, row_index + 1)] = 'X'

    for col_index, (col_sum, combinations) in enumerate(cols_combination):
        # Mark all other cells in the column as 'X' if no combination have
        if len(combinations) == 0:
            if AI_ENABLED:
                for row in range(1, CELL_NUMBER - 1):
                    if game_state["player_cells"][(col_index + 1, row)] == '':
                        game_state["player_cells"][(col_index + 1, row)] = 'X'
                        draw_screen(game_state)
                        pygame.display.update()
                        pygame.time.delay(AI_SPEED)
            else:
                for row in range(1, CELL_NUMBER - 1):
                    if game_state["AI_cells"][(col_index + 1, row)] == '':
                        game_state["AI_cells"][(col_index + 1, row)] = 'X'
        
        elif len(combinations) == 1:
            if AI_ENABLED:
                for cell in combinations[0]:
                    if game_state["player_cells"][(col_index + 1, cell)] == '':
                        game_state["player_cells"][(col_index + 1, cell)] = 'B'
                        draw_screen(game_state)
                        pygame.display.update()
                        pygame.time.delay(AI_SPEED)
                    
                # Mark all other cells in the column as 'X'
                for row in range(1, CELL_NUMBER - 1):
                    if row not in combinations[0]:
                        if game_state["player_cells"][(col_index + 1, row)] == '':
                            game_state["player_cells"][(col_index + 1, row)] = 'X'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
            else:
                for cell in combinations[0]:
                    if game_state["AI_cells"][(col_index + 1, cell)] == '':
                        game_state["AI_cells"][(col_index + 1, cell)] = 'B'
                    
                # Mark all other cells in the column as 'X'
                for row in range(1, CELL_NUMBER - 1):
                    if row not in combinations[0]:
                        if game_state["AI_cells"][(col_index + 1, row)] == '':
                            game_state["AI_cells"][(col_index + 1, row)] = 'X'

    solve_remaining_combination(rows_combination, cols_combination)

# ------------------------------------------------------------------------------------------------

# Class for input size
class TextInput:
    def __init__(self, position, width, height):
        self.position = position
        self.width = width
        self.height = height
        self.text = ""

    def handle_event(self, event):
        global CELL_NUMBER
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() and len(self.text) < 2:
                self.text += event.unicode
                if int(self.text) > 10:
                    self.text = '10'
                CELL_NUMBER = int(self.text) + 2
        if len(self.text) == 0 or int(self.text) < 4 or self.text == "":
            CELL_NUMBER = 6

    def render(self, surface):
        input_image = load_image("images/input.png", (self.width, self.height))
        surface.blit(input_image, self.position)

        font = pygame.font.Font(None, 35)
        text_surface = font.render(self.text, True, BLACK)
        surface.blit(text_surface, (self.position[0] + 70, self.position[1] + 5))

def check_last_previous_rows_states(lst):
    if len(lst) < 5:
        return False
    
    # Extract the last 5 elements
    last_five = lst[-5:]
    
    # Check if all elements in last_five are the same
    return all(element == last_five[0] for element in last_five)

# Initialize all cells to empty state
def initialize_game_state(state):
    state["problem_cells"] = {(i, j): '' for i in range(1, state["cell_number"] - 1) for j in range(1, state["cell_number"] - 1)}
    state["player_cells"] = {(i, j): '' for i in range(1, state["cell_number"] - 1) for j in range(1, state["cell_number"] - 1)}
    
    # Sinh ngẫu nhiên đáp án (Problem cells)
    for j in range(1, state["cell_number"] - 1):
        for i in range(1, state["cell_number"] - 1):
            if random.choice([True, False]): # Random 50% là ô đen
                state["problem_cells"][(i, j)] = 'B'
                
    # Tính toán row_sums và col_sums làm mục tiêu
    state["row_sums"] = [sum(i for (i, j), v in state["problem_cells"].items() if v == 'B' and j == y) for y in range(1, state["cell_number"] - 1)]
    state["col_sums"] = [sum(j for (i, j), v in state["problem_cells"].items() if v == 'B' and i == x) for x in range(1, state["cell_number"] - 1)]
    
    
    global AI_can_solve, AI_result
    AI_can_solve = True
    AI_result = True

# Searching Function — takes a board_cells dict (not the whole game_state)
def make_sum_arrays():
    n = game_state["cell_number"] - 2
    return [0] * (n + 1), [0] * (n + 1)

def get_current_sums(board_cells):
    cell_number = game_state["cell_number"]
    row_sums = [sum(i for (i, j), v in board_cells.items() if v == 'B' and j == y) for y in range(1, cell_number - 1)]
    col_sums = [sum(j for (i, j), v in board_cells.items() if v == 'B' and i == x) for x in range(1, cell_number - 1)]
    return row_sums, col_sums

# Kiểm tra xem tổng hiện tại có vượt quá mục tiêu không (Dùng để Pruning / Cắt tỉa)
def is_valid_state(board_cells):
    """Pruning check: return False if any row/col already exceeds its target."""
    cell_number = game_state["cell_number"]
    row_targets = game_state["row_sums"]
    col_targets = game_state["col_sums"]
    for y in range(1, cell_number - 1):
        curr = sum(i for (i, j), v in board_cells.items() if v == 'B' and j == y)
        if curr > row_targets[y - 1]: return False
    for x in range(1, cell_number - 1):
        curr = sum(i for (i, j), v in board_cells.items() if v == 'B' and j == x)
        if curr > col_targets[x - 1]: return False 
    return True

# Kiểm tra đã đúng đáp án chưa
def is_goal_state(board_cells):
    """Check whether the board fully matches all row/col targets."""
    cell_number = game_state["cell_number"]
    row_targets = game_state["row_sums"]
    col_targets = game_state["col_sums"]
    for y in range(1, cell_number - 1):
        curr = sum(i for (i, j), v in board_cells.items() if v == 'B' and j == y)
        if curr != row_targets[y - 1]: return False
    for x in range(1, cell_number - 1):
        curr = sum(j for (i, j), v in board_cells.items() if v == 'B' and i == x)
        if curr != col_targets[x - 1]: return False
    return True

# --- THUẬT TOÁN DFS ---
def solve_dfs():
    global AI_ENABLED
    n = game_state["cell_number"] - 2
    cells = list(game_state["player_cells"].keys()) # Danh sách tất cả tọa độ ô
    
    # Reset bảng người chơi
    for cell in cells:
        game_state["player_cells"][cell] = ''
    
    # ---- SMART CELL ORDERING ----
    # Sort cells so we fill the most constrained rows/cols first.
    # A row/col is "constrained" when its target is close to the max possible sum,
    # meaning there's little room for choice — we should decide those cells early
    # so we can prune bad branches as soon as possible.
    row_targets = game_state["row_sums"]
    col_targets = game_state["col_sums"]
    max_row_sum = sum(range(1, n + 1))

    # count RAM and time
    tracemalloc.start()
    start_time = time.perf_counter()

    TIME_LIMIT = 60.0
    timeout_flag = False
    total_sleep_time = 0.0  # Track time spent sleeping so we can exclude it from stats

    def cell_priority(cell):
        i, j  = cell 
        row_slack = max_row_sum - row_targets[j - 1]  # lower = more constrained
        col_slack = max_row_sum - col_targets[i - 1]
        return row_slack + col_slack    

    cells = sorted(game_state["player_cells"].keys(), key=cell_priority)
 
    # Incremental row/col sums — updated in O(1) instead of scanning all cells
    curr_row = [0] * (n + 2)  # index 1..n
    curr_col = [0] * (n + 2)

    def dfs(index):
        nonlocal timeout_flag, total_sleep_time
        # Cho phép user ấn tắt AI giữa chừng
        if not AI_ENABLED or timeout_flag: return False
        
        # Kiểm tra điều kiện timeout (excluding sleep time)
        if time.perf_counter() - start_time - total_sleep_time > TIME_LIMIT:
            timeout_flag = True
            return False

         # Fast incremental pruning — O(n) not O(n²)
        for r in range(1, n + 1):
            if curr_row[r] > row_targets[r - 1]: return False
        for c in range(1, n + 1):
            if curr_col[c] > col_targets[c - 1]: return False
 
        if index == len(cells):
            # Check all targets exactly met
            for r in range(1, n + 1):
                if curr_row[r] != row_targets[r - 1]: return False
            for c in range(1, n + 1):
                if curr_col[c] != col_targets[c - 1]: return False
            return True
 
        ci, cj = cells[index]

        # ---- FORWARD CHECKING ----
        # Before trying anything, check if remaining cells can still reach the target.
        # For each row/col, compute max possible addition from unassigned cells.
        remaining = set(cells[index:])
        for r in range(1, n + 1):
            deficit = row_targets[r - 1] - curr_row[r]
            if deficit < 0: return False
            if deficit > 0:
                max_add = sum(x for (x, y) in remaining if y == r)
                if max_add < deficit: return False
        for c in range(1, n + 1):
            deficit = col_targets[c - 1] - curr_col[c]
            if deficit < 0: return False
            if deficit > 0:
                max_add = sum(y for (x, y) in remaining if x == c)
                if max_add < deficit: return False
 
         # Try 'B'
        game_state["player_cells"][(ci, cj)] = 'B'
        curr_row[cj] += ci
        curr_col[ci] += cj
        time.sleep(AI_STEP_DELAY)
        total_sleep_time += AI_STEP_DELAY
        if dfs(index + 1): return True
        curr_row[cj] -= ci
        curr_col[ci] -= cj
 
        # Try 'X'
        game_state["player_cells"][(ci, cj)] = 'X'
        time.sleep(AI_STEP_DELAY)
        total_sleep_time += AI_STEP_DELAY
        if dfs(index + 1): return True
 
        # Backtrack
        game_state["player_cells"][(ci, cj)] = ''
        time.sleep(AI_STEP_DELAY)
        total_sleep_time += AI_STEP_DELAY
        return False

    # Chạy đệ quy DFS từ ô đầu tiên
    success = dfs(0)
    
    # Dừng đo lường
    end_time = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    pure_time_ms = (end_time - start_time - total_sleep_time) * 1000

    if timeout_flag:
        print(f"\n[!] AI đã DỪNG LẠI vì vượt quá {TIME_LIMIT} giây (Timeout).")
    elif success:
        print("\n[+] DFS đã tìm ra giải pháp!")
    else:
        print("\n[-] Đã duyệt hết nhưng Không tìm thấy giải pháp.")
    
    print("="*40)
    print("THỐNG KÊ HIỆU NĂNG - THUẬT TOÁN DFS")
    print(f"Kích thước bảng: {CELL_NUMBER - 2}x{CELL_NUMBER - 2}")
    print(f"Thời gian chạy (thuần): {pure_time_ms:.4f} milliseconds")
    print(f"Bộ nhớ tiêu tốn (Peak): {peak_mem / 1024 / 1024:.6f} MB")
    print("="*40 + "\n")

    AI_ENABLED = False # Tắt nút AI khi chạy xong

# A* heuristic algorithm
# (get_current_sums, is_valid_state, is_goal_state are already defined above and shared by both DFS and A*)

def calculate_heuristic(board_cells, cells, index):
    """
    Improved admissible heuristic for A*.
 
    For each row and column, we compute:
      - current partial sum of black cells already placed
      - the remaining deficit = target - current
      - the remaining cells in that row/col that are still unassigned
 
    If deficit > 0 but no remaining unassigned cells can reach it → inadmissible branch.
    Otherwise h = sum of all deficits (how far we still are from the goal).
    This is admissible because each remaining cell contributes at most its index value.
    """
    cell_number = game_state["cell_number"]
    n = cell_number - 2
    row_targets = game_state["row_sums"]
    col_targets = game_state["col_sums"]

    # Build sets of cells not yet decided (index onward)
    remaining_cells = set(cells[index:])

    h = 0
    for y in range(1, n + 1):
        curr = sum(i for (i, j), v in board_cells.items() if v == 'B' and j == y)
        deficit = row_targets[y - 1] - curr
        if deficit < 0:
            return float('inf')  # Already exceeded — inadmissible state
        if deficit > 0:
            # Max possible contribution from remaining cells in this row
            max_possible = sum(i for i in range(1, n + 1) if (i, y) in remaining_cells)
            if max_possible < deficit:
                return float('inf')  # Can never reach target
            h += deficit
    
    for x in range(1, n + 1):
        curr = sum(j for (i, j), v in board_cells.items() if v == 'B' and i == x)
        deficit = col_targets[x - 1] - curr
        if deficit < 0:
            return float('inf')
        if deficit > 0:
            max_possible = sum(j for j in range(1, n + 1) if (x, j) in remaining_cells)
            if max_possible < deficit:
                return float('inf')
            h += deficit
 
    return h

# Check sum if have a single combination
def check_total_combinations(target_sum):
    possible_combinations = []
    limited_numbers = range(1, CELL_NUMBER -1)
    for r in range(1, len(limited_numbers) + 1):
        for combination in combinations(limited_numbers, r):
            if sum(combination) == target_sum:
                possible_combinations.append(combination)

    return len(possible_combinations)

# --- THUẬT TOÁN A* (A-STAR) ---
def solve_astar():
    global AI_ENABLED
    n = game_state["cell_number"] - 2
 
    for cell in game_state["player_cells"]:
        game_state["player_cells"][cell] = ''
 
    # Same smart cell ordering as DFS — most constrained first
    row_targets = game_state["row_sums"]
    col_targets = game_state["col_sums"]
    max_row_sum = sum(range(1, n + 1))
 
    def cell_priority(cell):
        i, j = cell
        return (max_row_sum - row_targets[j - 1]) + (max_row_sum - col_targets[i - 1])
 
    cells = sorted(game_state["player_cells"].keys(), key=cell_priority)
 
    tracemalloc.start()
    start_time = time.perf_counter()
    TIME_LIMIT = 60.0
    timeout_flag = False
    total_sleep_time = 0.0
 
    pq = []
    count = 0
    visited = set()  # Avoid re-expanding the same (depth, state) pair
 
    # Store board as a compact tuple to save memory and allow hashing
    initial_tuple = tuple('' for _ in cells)
    h0 = calculate_heuristic(game_state["player_cells"], cells, 0)
    heapq.heappush(pq, (h0, count, 0, initial_tuple))
    success = False
 
    def tuple_to_dict(t):
        return {cells[k]: t[k] for k in range(len(cells))}
 
    while pq:
        if not AI_ENABLED: break
 
        if time.perf_counter() - start_time - total_sleep_time > TIME_LIMIT:
            timeout_flag = True
            break
 
        current_f, _, index, current_tuple = heapq.heappop(pq)
 
        state_key = (index, current_tuple)
        if state_key in visited:
            continue
        visited.add(state_key)
 
        current_board = tuple_to_dict(current_tuple)
        game_state["player_cells"] = current_board
        time.sleep(AI_STEP_DELAY)
        total_sleep_time += AI_STEP_DELAY
 
        if index == len(cells):
            if is_goal_state(current_board):
                success = True
            break
 
        ci, cj = cells[index]
 
        for choice in ['B', 'X']:
            new_tuple = current_tuple[:index] + (choice,) + current_tuple[index + 1:]
            new_key = (index + 1, new_tuple)
            if new_key in visited:
                continue
 
            # Fast single-cell pruning before building full board dict
            if choice == 'B':
                row_sum = sum(x for (x, y), v in current_board.items() if v == 'B' and y == cj) + ci
                col_sum = sum(y for (x, y), v in current_board.items() if v == 'B' and x == ci) + cj
                if row_sum > row_targets[cj - 1] or col_sum > col_targets[ci - 1]:
                    continue
 
            new_board = tuple_to_dict(new_tuple)
            new_h = calculate_heuristic(new_board, cells, index + 1)
            if new_h == float('inf'):
                continue  # Heuristic says unreachable — prune
 
            new_f = (index + 1) + new_h
            count += 1
            heapq.heappush(pq, (new_f, count, index + 1, new_tuple))
 
    end_time = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    pure_time_ms = (end_time - start_time - total_sleep_time) * 1000
 
    if timeout_flag:
        print(f"\n[!] A* đã DỪNG LẠI vì vượt quá {TIME_LIMIT} giây (Timeout).")
    elif success:
        print("\n[+] A* đã tìm ra giải pháp!")
    else:
        print("\n[-] Không tìm thấy giải pháp.")
 
    print("="*40)
    print("THỐNG KÊ HIỆU NĂNG - THUẬT TOÁN A*")
    print(f"Kích thước bảng: {n}x{n}")
    print(f"Thời gian chạy (thuần): {pure_time_ms:.4f} milliseconds")
    print(f"Bộ nhớ tiêu tốn (Peak): {peak_mem / 1024 / 1024:.6f} MB")
    print("="*40 + "\n")
 
    AI_ENABLED = False

# Initialize the game state and buttons 
initialize_game_state(game_state)

# Ensure window is tall enough to fit all UI buttons on the right panel
REQUIRED_UI_HEIGHT = 450
GAME_GRID_HEIGHT = CELL_SIZE * CELL_NUMBER
SCREEN_HEIGHT = max(GAME_GRID_HEIGHT, REQUIRED_UI_HEIGHT)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Tọa độ mới cho các nút (căn chỉnh từ trên xuống, tạo khoảng trống cho văn bản size)
check_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 10, 160, 30)
refresh_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 60, 160, 30)
reset_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 110, 160, 30)

# Khối văn bản Size (vị trí y cơ sở cho văn bản và input box)
size_section_y = 160
text_input = TextInput((SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, size_section_y + 25), 160, 30)

# NÚT CHỌN THUẬT TOÁN (Sâu xuống một chút, dưới khối văn bản size)
algo_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 250, 160, 25)

AI_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 300, 160, 30)
reveal_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 350, 160, 30)

def reset_game_state():
    global game_state
    global check_button_rect, refresh_button_rect, reset_button_rect
    global text_input, AI_button_rect, reveal_button_rect, algo_button_rect
    global SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_WIDTH_WITHOUT_SIDE_TAB
    global screen
    global AI_ENABLED, REVEAL_ENABLED, is_win
    global AI_result, AI_can_solve
    global TOTAL_CLUES, CLUES_NUMBER
    global previous_states, TEMP
    global show_popup, popup_text

    TOTAL_CLUES = 0
    CLUES_NUMBER = 0
    AI_can_solve = False
    AI_result = False
    is_win = False
    AI_ENABLED = False
    REVEAL_ENABLED = False
    previous_states = []
    TEMP = []
    show_popup = False
    popup_text = None
    _image_cache.clear()  # Force button images to reload at new sizes

    SCREEN_WIDTH = (CELL_SIZE * CELL_NUMBER) + RIGHT_SIDE_SCREEN_TAB
    SCREEN_WIDTH_WITHOUT_SIDE_TAB = SCREEN_WIDTH - RIGHT_SIDE_SCREEN_TAB
    GAME_GRID_HEIGHT = CELL_SIZE * CELL_NUMBER
    SCREEN_HEIGHT = max(GAME_GRID_HEIGHT, 450)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    game_state = {
        "cell_size": CELL_SIZE,
        "cell_number": CELL_NUMBER,
        "problem_cells": {},
        "player_cells": {},
        "AI_cells": {},
        "row_sums": [],
        "col_sums": []
    }
    initialize_game_state(game_state)

    check_button_rect   = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20,  10, 160, 30)
    refresh_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20,  60, 160, 30)
    reset_button_rect   = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 110, 160, 30)
    text_input          = TextInput((SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 185), 160, 30)
    algo_button_rect    = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 250, 160, 25)
    AI_button_rect      = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 300, 160, 30)
    reveal_button_rect  = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 350, 160, 30)

# Function for cell click event
def toggle_cell_state(state, cell):
    if state["player_cells"][cell] == '':
        state["player_cells"][cell] = 'B'
    elif state["player_cells"][cell] == 'B':
        state["player_cells"][cell] = 'X'
    else:
        state["player_cells"][cell] = ''

def draw_screen(state):
    screen.fill(GOLD)
    for i in range(1, state["cell_number"]):
        for j in range(1, state["cell_number"]):
            cell_state = state["player_cells"].get((i, j), None)  
            if cell_state is not None:
                if cell_state == 'B':
                    pygame.draw.rect(screen, WHITE, (i * state["cell_size"], j * state["cell_size"], state["cell_size"], state["cell_size"]))
                    pygame.draw.rect(screen, BLACK, ((i * state["cell_size"] + 5), (j * state["cell_size"] + 5), state["cell_size"] - 10, state["cell_size"] - 10))
                elif cell_state == 'X':
                    pygame.draw.rect(screen, WHITE, (i * state["cell_size"], j * state["cell_size"], state["cell_size"], state["cell_size"]))
                    font = pygame.font.Font(None, 36)
                    text = font.render('X', True, RED)
                    screen.blit(text, (i * state["cell_size"] + state["cell_size"] // 2 - text.get_width() // 2, j * state["cell_size"] + state["cell_size"] // 2 - text.get_height() // 2))
                else:
                    pygame.draw.rect(screen, WHITE, (i * state["cell_size"], j * state["cell_size"], state["cell_size"], state["cell_size"]))
    
    draw_gridline(state)
    draw_check_button()
    draw_refresh_button()
    draw_reset_button()
    draw_ai_button()
    draw_text()
    draw_reveal_button()
    draw_algo_button()
    text_input.render(screen)

# Draw grid lines and sums
def draw_gridline(state):
    """Vẽ đường kẻ lưới, đường viền và các con số tổng điểm"""
    
    # Tính toán chiều cao thực tế của lưới game (5 ô * 50px = 250px cho bảng 4x4)
    GAME_GRID_HEIGHT = state["cell_size"] * state["cell_number"]
    
    # Vẽ đường kẻ lưới (chỉ trong phạm vi lưới game)
    # Đường kẻ dọc
    for x in range(0, SCREEN_WIDTH_WITHOUT_SIDE_TAB + 1, state["cell_size"]):
        # pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_HEIGHT)) # LỖI CŨ: Vẽ quá dài
        pygame.draw.line(screen, BLACK, (x, 0), (x, GAME_GRID_HEIGHT)) # SỬA: Chỉ vẽ trong phạm vi lưới game
        
    # Đường kẻ ngang
    for y in range(0, GAME_GRID_HEIGHT + 1, state["cell_size"]):
        pygame.draw.line(screen, BLACK, (0, y), (SCREEN_WIDTH_WITHOUT_SIDE_TAB, y))

    # Vẽ đường viền (Border line) (Chỉ bao quanh lưới game)
    # pygame.draw.rect(screen, WHITE, (state["cell_size"], state["cell_size"], (SCREEN_WIDTH_WITHOUT_SIDE_TAB - (state["cell_size"] * 2)), (SCREEN_HEIGHT - (state["cell_size"] * 2))), width=5) # LỖI CŨ
    pygame.draw.rect(screen, WHITE, (state["cell_size"], state["cell_size"], 
                                      (SCREEN_WIDTH_WITHOUT_SIDE_TAB - (state["cell_size"] * 2)), 
                                      (GAME_GRID_HEIGHT - (state["cell_size"] * 2))), width=5) # SỬA: Chỉ viền lưới game

    # --- Phần vẽ tổng điểm và số thứ tự vẫn giữ nguyên ---
    # Draw row sums
    for j, sum_row in enumerate(state["row_sums"]):
        font = pygame.font.Font(None, 24)
        text = font.render(str(sum_row), True, BLACK)
        screen.blit(text, ((state["cell_number"] - 1) * state["cell_size"] + state["cell_size"] // 2 - text.get_width() // 2, (j + 1) * state["cell_size"] + state["cell_size"] // 2 - text.get_height() // 2))

    # Draw column sums
    for i, sum_col in enumerate(state["col_sums"]):
        font = pygame.font.Font(None, 24)
        text = font.render(str(sum_col), True, BLACK)
        screen.blit(text, ((i + 1) * state["cell_size"] + state["cell_size"] // 2 - text.get_width() // 2, (state["cell_number"] - 1) * state["cell_size"] + state["cell_size"] // 2 - text.get_height() // 2))

    # Draw row numbering on the left side outside of the grid
    for j in range(state["cell_number"]):
        if j > 0 and j < (state["cell_number"] - 1):
            font = pygame.font.Font(None, 36)
            text = font.render(str(j), True, BLACK)
            screen.blit(text, (5, (j) * state["cell_size"] + state["cell_size"] // 2 - text.get_height() // 2))

    # Draw column numbering above the grid outside of the grid
    for i in range(state["cell_number"]):
        if i > 0 and i < (state["cell_number"] - 1):
            font = pygame.font.Font(None, 36)
            text = font.render(str(i), True, BLACK)
            screen.blit(text, ((i) * state["cell_size"] + state["cell_size"] // 2 - text.get_width() // 2, 5))

def draw_text():
    """Vẽ văn bản Input Size và thông tin kích thước hiện tại"""
    font = pygame.font.Font('freesansbold.ttf', 15)
    
    # Sử dụng mốc y cơ sở mới đã khai báo ở Bước 1
    # Tọa độ y cơ sở 'size_section_y' là 160
    
    # Nhãn "Input Size:"
    size_label = font.render(f'Input Size: ', True, BLACK)
    screen.blit(size_label, (check_button_rect.x, size_section_y)) # Căn theo x của nút Check
    
    # Thông tin kích thước hiện tại "(Size: NxN)"
    size_info_label = font.render(f'( Size: {CELL_NUMBER - 2}x{CELL_NUMBER - 2} )', True, BLACK)
    screen.blit(size_info_label, (check_button_rect.x, size_section_y + 60)) # Cách y cơ sở 60px

# ---- IMAGE CACHE (load once, reuse every frame) ----
_image_cache = {}

def load_image(path, size=None):
    """Load an image from disk once, cache it, and return a scaled copy if size is given."""
    cache_key = (path, size)
    if cache_key not in _image_cache:
        img = pygame.image.load(path)
        if size:
            img = pygame.transform.scale(img, size)
        _image_cache[cache_key] = img
    return _image_cache[cache_key]

# Draw Check button
def draw_check_button():
    img = load_image("images/check.png", (check_button_rect.width, check_button_rect.height))
    screen.blit(img, check_button_rect.topleft)

# Draw Refresh button
def draw_refresh_button():
    img = load_image("images/new_game.png", (refresh_button_rect.width, refresh_button_rect.height))
    screen.blit(img, refresh_button_rect.topleft)

# Draw Reset button
def draw_reset_button():
    img = load_image("images/reset.png", (reset_button_rect.width, reset_button_rect.height))
    screen.blit(img, reset_button_rect.topleft)

# Draw reveal button
def draw_reveal_button():
    on_img  = load_image("images/revealOn.png",  (reveal_button_rect.width, reveal_button_rect.height))
    off_img = load_image("images/revealOff.png", (reveal_button_rect.width, reveal_button_rect.height))
    screen.blit(on_img if REVEAL_ENABLED else off_img, reveal_button_rect.topleft)

# Draw AI button
def draw_ai_button():
    on_img  = load_image("images/aiBotOn.png",  (AI_button_rect.width, AI_button_rect.height))
    off_img = load_image("images/aiBotOff.png", (AI_button_rect.width, AI_button_rect.height))
    screen.blit(on_img if AI_ENABLED else off_img, AI_button_rect.topleft)

# Draw algorithm button
def draw_algo_button():
    pygame.draw.rect(screen, GRAY, algo_button_rect)
    pygame.draw.rect(screen, BLACK, algo_button_rect, 2)
    font = pygame.font.Font(None, 24)
    text = font.render(f"Mode: {CURRENT_ALGO}", True, BLACK)
    text_rect = text.get_rect(center=algo_button_rect.center)
    screen.blit(text, text_rect)

def handle_click(state, pos):
    if not REVEAL_ENABLED:
        x, y = pos
        if x < state["cell_size"] or y < state["cell_size"] or x >= SCREEN_WIDTH_WITHOUT_SIDE_TAB - state["cell_size"] or y >= SCREEN_HEIGHT - state["cell_size"]:
            return
        i = x // state["cell_size"]
        j = y // state["cell_size"]
        if (i, j) in state["player_cells"]:
            toggle_cell_state(state, (i, j))

def handle_refresh_click():
    reset_game_state()

def handle_reset_click():
    global AI_ENABLED
    global REVEAL_ENABLED
    AI_ENABLED = False
    REVEAL_ENABLED = False
    print(game_state["player_cells"])
    for key in game_state["player_cells"]:
        game_state["player_cells"][key] = ''

_ai_thread = None

def handle_ai_button_click():
    global _ai_thread
    # Only start a new thread if one isn't already running
    if AI_ENABLED and (_ai_thread is None or not _ai_thread.is_alive()):
        target = solve_dfs if CURRENT_ALGO == "DFS" else solve_astar
        _ai_thread = threading.Thread(target=target, daemon=True)
        _ai_thread.start()

def handle_reveal_button_click():
    global TEMP
    if REVEAL_ENABLED:
        TEMP = game_state["player_cells"].copy()  # Save a real copy, not a reference
        game_state["player_cells"] = game_state["problem_cells"].copy()
    else:
        game_state["player_cells"] = TEMP.copy() if TEMP else {k: '' for k in game_state["problem_cells"]}

def check_solution():
    global AI_ENABLED  
    for cell, value in game_state["problem_cells"].items():
        if value == 'B' and game_state["player_cells"].get(cell) != 'B':
            return False
        if value != 'B' and game_state["player_cells"].get(cell) == 'B':
            return False
    AI_ENABLED = False
    return True

def show_popup_display(message):
    global show_popup
    global run
    color = None
    if show_popup:
        # Background
        background_rect = pygame.Rect(0, 0, 400, 200)
        background_image = load_image('images/popupBG.png', (400, 200))
        background_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        screen.blit(background_image, background_rect.topleft)

        # Text display
        popup_text1_image = load_image('images/popup_text1.png', (background_rect.width, background_rect.height))
        popup_text2_image = load_image('images/popup_text2.png', (background_rect.width, background_rect.height))
        popup_text3_image = load_image('images/popup_text3.png', (background_rect.width, background_rect.height))

        if message == 'text1':
            screen.blit(popup_text1_image, background_rect.topleft)
        elif message == 'text2':
            screen.blit(popup_text2_image, background_rect.topleft)
        elif message == 'text3':
            screen.blit(popup_text3_image, background_rect.topleft)

        # Button
        popup_button_width = 160
        popup_button_height = 50
        popup_button_x = (SCREEN_WIDTH - popup_button_width) // 2
        popup_button_y = ((SCREEN_HEIGHT - popup_button_height) // 2) + 60
        popup_button_rect = pygame.Rect(popup_button_x, popup_button_y, popup_button_width, popup_button_height)

        popup_button1_image = load_image('images/popup_button1.png', (popup_button_rect.width, popup_button_rect.height))
        popup_button2_image = load_image('images/popup_button2.png', (popup_button_rect.width, popup_button_rect.height))

        if is_win:
            screen.blit(popup_button1_image, popup_button_rect.topleft)
        else:
            screen.blit(popup_button2_image, popup_button_rect.topleft)

        # pygame.display.update()

        # Handle click event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if popup_button_rect.collidepoint(event.pos):
                        if is_win:
                            reset_game_state()
                            show_popup = False
                        else:
                            show_popup = False

def threaded_handle_refresh_click():
    # Must run on main thread — pygame.display.set_mode() cannot be called from a background thread
    handle_refresh_click()

# Initialize the check button before the event loop
draw_screen(game_state)
pygame.display.update()

clock = pygame.time.Clock()

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if check_button_rect and check_button_rect.collidepoint(event.pos):
                # print('Problem State: ', game_state["problem_cells"])
                # print('Player State: ', game_state["player_cells"])
                if REVEAL_ENABLED:
                    show_popup = True
                    popup_text = "text3"
                elif check_solution():
                    print("You Win!")
                    show_popup = True
                    is_win = True
                    popup_text = "text1"
                else:
                    show_popup = True
                    print("Incorrect, keep trying!")
                    popup_text = "text2"
            else:
                handle_click(game_state, event.pos)
                
            # Handle click on the refresh button
            if refresh_button_rect.collidepoint(event.pos):
                if REVEAL_ENABLED:
                    show_popup = True
                    popup_text = "text3"
                else:
                    threaded_handle_refresh_click()
            
            # Handle click on the reset button
            if reset_button_rect.collidepoint(event.pos):
                if REVEAL_ENABLED:
                    show_popup = True
                    popup_text = "text3"
                else:
                    handle_reset_click()

            # Handle click on the Algo toggle button
            if algo_button_rect.collidepoint(event.pos):
                if CURRENT_ALGO == "DFS":
                    CURRENT_ALGO = "A*"
                else:
                    CURRENT_ALGO = "DFS"
                draw_screen(game_state)
                pygame.display.update()

            # Handle click on the AI button
            if AI_button_rect.collidepoint(event.pos):
                if REVEAL_ENABLED:
                    show_popup = True
                    popup_text = "text3"
                else:
                    AI_ENABLED = not AI_ENABLED
                    game_state["player_cells"] = {(i, j): '' for i in range(1, game_state["cell_number"] - 1) for j in range(1, game_state["cell_number"] - 1)}
            
            # Handle click on the Reveal button
            if reveal_button_rect.collidepoint(event.pos):
                REVEAL_ENABLED = not REVEAL_ENABLED
                handle_reveal_button_click()

        elif event.type == pygame.KEYDOWN:
            # Handle keyboard events for text input
            text_input.handle_event(event)

    # Draw the screen only once per iteration
    draw_screen(game_state)

    if AI_ENABLED:
        handle_ai_button_click()

    if show_popup:
        show_popup_display(popup_text)
    pygame.display.update()
    clock.tick(60)  # Cap at 60 FPS — keeps main thread responsive while AI runs in background

pygame.quit()