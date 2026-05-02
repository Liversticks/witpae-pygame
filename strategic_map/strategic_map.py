import pygame
from math import sqrt
from geks import RectHexmap, Layout

METERS_PER_NM = 1852

class StrategicMap:
    def __init__(self, background_file_path: str, background_width: int, hex_radius_nm: int):
        self.background = pygame.image.load(background_file_path).convert_alpha()
        self.rect = self.background.get_rect()
        
        # Spatial math
        self.px_per_meter = self.rect.width / background_width
        self.hex_size_meters = hex_radius_nm * METERS_PER_NM
        self.hex_radius_px = self.hex_size_meters * self.px_per_meter
        
        # Spacing constants for pointy-topped hexes
        self.width_spacing = self.hex_radius_px * sqrt(3)
        self.height_spacing = self.hex_radius_px * 1.5
        
        # Grid dimensions derived from image size and hex spacing
        self.cols = int(self.rect.width / self.width_spacing) + 1
        self.rows = int(self.rect.height / self.height_spacing) + 1
        
        self.hex_map = RectHexmap(1, (self.cols, self.rows), flat=False)
        self.layout = Layout(size=(self.hex_radius_px, self.hex_radius_px), flat=False)

    def get_background(self):
        return self.background

    def get_rect(self):
        return self.rect
    
    def get_rows(self) -> int:
        return self.rows
    
    def get_cols(self) -> int:
        return self.cols
    
    def get_px_per_m(self) -> int:
        return self.px_per_meter
    
    def get_hex_radius_m(self) -> int:
        return self.hex_size_meters
    
    def get_hex_radius_px(self) -> int:
        return self.hex_radius_px
    
    def get_width_spacing(self) -> float:
        return self.width_spacing
    
    def get_height_spacing(self) -> float:
        return self.height_spacing
    
    def on_click_hex(self, coordinates: tuple[int, int]):
        clicked_hex = self.layout.pixel2hex(coordinates)
        print(f"Hex Coordinate: q={clicked_hex.q}, r={clicked_hex.r}")
        print(self.hex_map.get(clicked_hex))
    
    def debug_print_map_initalization(self):
        print(self.hex_map.center())
        print(self.hex_map.corners())
        print(f"Cols: {self.cols}, Rows: {self.rows}")