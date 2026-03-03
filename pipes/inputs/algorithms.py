import heapq

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.g = 0 # Chi phí đường đi
        self.h = 0 # Heuristic
        
    def f(self):
        return self.g + self.h

def solve_dfs(initial_state):
    """Giải thuật Blind Search (DFS)"""
    stack = [Node(initial_state)]
    visited = set()
    steps = [] # Lưu mảng grid ở mỗi bước để demo
    
    while stack:
        node = stack.pop()
        steps.append(node.state.grid)
        
        if node.state.is_goal():
            return node.state.grid, steps
            
        # TODO: Xử lý visited hash để không bị lặp trạng thái
        # TODO: Mở rộng các node con từ node.state.get_successors() và push vào stack
        
    return None, steps

def solve_astar(initial_state):
    """Giải thuật Heuristic (A*)"""
    # TODO: Khởi tạo priority queue (heapq) với giá trị f(n)
    # TODO: Implement tương tự code Nonogram, nhưng dùng f(n) = g(n) + heuristic của Pipe
    pass