from geks import RectHexmap

class HexGrid:
    """Handles the logical data structure of the hex grid."""
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        # flat=False indicates a pointy-topped hex grid
        self.hex_map = RectHexmap(1, (self.cols, self.rows), flat=False)