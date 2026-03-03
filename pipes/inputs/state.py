import copy

class PipeState:
    def __init__(self, grid):
        # grid là mảng 2D chứa tuple (loại_ống, góc_xoay)
        # Ví dụ: (2, 0) là ống Góc L xoay 0 độ
        self.grid = grid
        self.size = len(grid)

    def get_successors(self):
        """
        Sinh các trạng thái kế tiếp (Successor Function).
        Mỗi bước đi, ta thử xoay 1 ống 90 độ.
        """
        successors = []
        # TODO: Bạn sẽ cần tìm ô cần xoay tiếp theo (ví dụ duyệt từ trên xuống dưới, trái qua phải)
        # Giả sử tìm được ô (i, j) có loại ống > 0.
        # Ta tạo ra các trạng thái mới bằng cách tăng góc xoay: (rotation + 1) % 4
        
        # Ví dụ cấu trúc sinh trạng thái:
        # new_grid = copy.deepcopy(self.grid)
        # new_grid[i][j] = (loại_ống, (góc_xoay + 1) % 4)
        # successors.append(PipeState(new_grid))
        
        return successors

    def is_goal(self):
        """
        Điều kiện kết thúc (Goal Test).
        """
        # TODO: Duyệt toàn bộ lưới, kiểm tra xem tất cả các đầu nối của các ống có khớp nhau không.
        # Không có đầu ống nào chĩa ra ngoài viền hoặc chĩa vào ô trống.
        return False