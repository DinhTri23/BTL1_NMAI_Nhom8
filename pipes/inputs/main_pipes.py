import pygame, sys, time
# Import các module ta vừa viết
from state import PipeState
from algorithms import solve_dfs, solve_astar

def load_level(filepath):
    """Đọc file txt và khởi tạo grid ban đầu với góc xoay ngẫu nhiên hoặc 0"""
    # ... logic đọc file text ở trên ...
    pass

def draw_pipe(screen, cell_rect, pipe_type, rotation):
    """Hàm vẽ từng loại ống dựa trên thông số"""
    # TODO: Dùng pygame.draw.line hoặc load ảnh PNG ống nước rồi xoay (pygame.transform.rotate)
    pass

def draw_board(screen, board, cell_size, offset_x, offset_y):
    """Vẽ toàn bộ bàn cờ"""
    size = len(board)
    for i in range(size):
        for j in range(size):
            rect = pygame.Rect(offset_x + j * cell_size, offset_y + i * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=4)
            pygame.draw.rect(screen, (120, 120, 120), rect, 1, border_radius=4)
            
            pipe_type, rotation = board[i][j]
            if pipe_type > 0:
                draw_pipe(screen, rect, pipe_type, rotation)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pipes AI Solver")
    clock = pygame.time.Clock()
    
    state = "menu_algo" # Bỏ qua menu chọn size, đi thẳng vào chọn thuật toán
    solver_steps = []
    current_step = 0
    last_step_time = time.time()
    
    # Init initial grid từ file
    initial_grid = load_level("inputs/level1.txt")
    initial_pipe_state = PipeState(initial_grid)
    
    # Nút bấm menu
    algo_buttons = [
        ("DFS Search", pygame.Rect(250, 200, 300, 70)),
        ("A* Search", pygame.Rect(250, 300, 300, 70))
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
            if state == "menu_algo" and event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for text, rect in algo_buttons:
                    if rect.collidepoint(pos):
                        # Bắt đầu giải
                        if "DFS" in text:
                            _, solver_steps = solve_dfs(initial_pipe_state)
                        else:
                            _, solver_steps = solve_astar(initial_pipe_state)
                            
                        state = "solving"
                        current_step = 0
                        last_step_time = time.time()

        screen.fill((40, 40, 40))
        
        if state == "menu_algo":
            # TODO: Vẽ các nút menu giống hệt code Nonogram
            pass
            
        elif state == "solving":
            # Hiệu ứng step-by-step
            if current_step < len(solver_steps):
                current_board = solver_steps[current_step]
                draw_board(screen, current_board, 80, 100, 100) # (cell_size, offset_x, offset_y)
                
            if time.time() - last_step_time >= 0.2: # Tốc độ animation (0.2s/bước)
                if current_step < len(solver_steps) - 1:
                    current_step += 1
                    last_step_time = time.time()
                else:
                    state = "result"
                    
        elif state == "result":
            # Bàn cờ kết quả cuối cùng
            draw_board(screen, solver_steps[-1], 80, 100, 100)
            
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()