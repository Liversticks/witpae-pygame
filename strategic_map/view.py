import pygame
from math import sqrt
from geks import Layout

METERS_PER_NM = 1852

class HexView:
    """Handles the visual representation and spatial layout of the map."""
    def __init__(self, background_file_path: str, background_width_m: int, hex_radius_nm: int):
        self.background = pygame.image.load(background_file_path).convert_alpha()
        self.rect = self.background.get_rect()
        
        # Spatial math
        self.px_per_meter = self.rect.width / background_width_m
        self.hex_size_meters = hex_radius_nm * METERS_PER_NM
        self.hex_radius_px = self.hex_size_meters * self.px_per_meter
        
        # Spacing constants for pointy-topped hexes
        self.width_spacing = self.hex_radius_px * sqrt(3)
        self.height_spacing = self.hex_radius_px * 1.5
        
        # Grid dimensions derived from image size and hex spacing
        self.cols = int(self.rect.width / self.width_spacing) + 1
        self.rows = int(self.rect.height / self.height_spacing) + 1
        
        # Geks Layout handles pixel <-> hex conversions
        self.layout = Layout(size=(self.hex_radius_px, self.hex_radius_px), flat=False)