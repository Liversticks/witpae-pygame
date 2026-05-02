from .grid import HexGrid
from .view import HexView

class StrategicMap:
    def __init__(self, background_file_path: str, background_width: int, hex_radius_nm: int):
        # Initialize the two components
        self.view = HexView(background_file_path, background_width, hex_radius_nm)
        self.grid = HexGrid(self.view.cols, self.view.rows)

    def get_background(self):
        return self.view.background

    def get_rect(self):
        return self.view.rect
    
    def get_rows(self) -> int:
        return self.grid.rows
    
    def get_cols(self) -> int:
        return self.grid.cols
    
    def get_px_per_m(self) -> int:
        return self.view.px_per_meter
    
    def get_hex_radius_m(self) -> int:
        return self.view.hex_size_meters
    
    def get_hex_radius_px(self) -> int:
        return self.view.hex_radius_px
    
    def get_width_spacing(self) -> float:
        return self.view.width_spacing
    
    def get_height_spacing(self) -> float:
        return self.view.height_spacing
    
    def on_click_hex(self, coordinates: tuple[int, int]):
        # Delegate coordinate conversion to view, data lookup to grid
        clicked_hex = self.view.layout.pixel2hex(coordinates)
        
        print(f"Hex Coordinate: q={clicked_hex.q}, r={clicked_hex.r}")
        print(self.grid.hex_map.get(clicked_hex))
    
    def debug_print_map_initalization(self):
        print(self.grid.hex_map.center())
        print(self.grid.hex_map.corners())
        print(f"Cols: {self.grid.cols}, Rows: {self.grid.rows}")