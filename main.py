# Example file showing a basic pygame "game loop"
import pygame
import json
import math
from pathlib import Path

# 1. LOAD OPTIONS FROM JSON
# Define the path to your settings file
settings_path = Path(__file__).resolve().parent / "options.json"

with open(settings_path, "r") as f:
    settings = json.load(f)

METERS_PER_NM = 1852
HEX_NM = 20
hex_size_meters = HEX_NM * METERS_PER_NM

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720), flags=pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

background_location = Path(__file__).resolve().parent / settings["backgroundImagePath"]
background = pygame.image.load(background_location).convert_alpha()
background_rect = background.get_rect()

MAP_WIDTH = settings["mapWidth"]
px_per_meter = background_rect.width / MAP_WIDTH
hex_radius = hex_size_meters * px_per_meter

grid_surf = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)

def get_hex_points(center_x, center_y, radius):
    points = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.pi / 180 * angle_deg
        px = center_x + radius * math.cos(angle_rad)
        py = center_y + radius * math.sin(angle_rad)
        points.append((px, py))
    return points

# Grid math for flat-topped hexes
width_spacing = hex_radius * 1.5
height_spacing = hex_radius * math.sqrt(3)

cols = int(background_rect.width / width_spacing) + 1
rows = int(background_rect.height / height_spacing) + 1


for r in range(rows):
    for c in range(cols):
        x = c * width_spacing
        # Offset every other column
        y = r * height_spacing + (c % 2) * (height_spacing / 2)
        
        # Only draw if the center is roughly within the image bounds
        if x < background_rect.width + hex_radius and y < background_rect.height + hex_radius:
            pygame.draw.polygon(grid_surf, (0, 0, 0), get_hex_points(x, y, hex_radius), 1)


# Combine Background and Grid for easier handling
final_base_surf = background.copy()
final_base_surf.blit(grid_surf, (0, 0))

# Camera state
cam_pos = pygame.Vector2(0,0)  # Upper left of background image
zoom_level = 1.0
move_speed = 10
zoom_dirty = False
scaled_surf = final_base_surf

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            
            # Calculate world position of mouse before zoom
            # (Mouse screen pos + Camera pos) / old_zoom
            old_zoom = zoom_level
            world_mouse_before = (mouse_pos + cam_pos) / old_zoom
            
            # Update zoom level
            # (how far out to zoom, how far zoomed in)
            zoom_level += event.y * 0.1
            zoom_level = max(0.5, min(zoom_level, 2.5))
            
            # Calculate new camera position to keep mouse over the same world spot
            # New Cam Pos = (World Mouse * new_zoom) - Mouse Screen Pos
            cam_pos = (world_mouse_before * zoom_level) - mouse_pos

            zoom_dirty = True
            

    # 2. PANNING (Arrow keys)
    keys = pygame.key.get_pressed()
    move_speed = 15 / zoom_level
    if keys[pygame.K_LEFT]:  cam_pos.x -= move_speed
    if keys[pygame.K_RIGHT]: cam_pos.x += move_speed
    if keys[pygame.K_UP]:    cam_pos.y -= move_speed
    if keys[pygame.K_DOWN]:  cam_pos.y += move_speed

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    # RENDER YOUR GAME HERE
    # Scale the image based on zoom level
    if zoom_dirty:
        # use scale() for speed, smoothscale() for quality
        new_size = (int(background_rect.width * zoom_level), int(background_rect.height * zoom_level))
        scaled_surf = pygame.transform.scale(final_base_surf, new_size)
        zoom_dirty = False
    
    # Blit the scaled image at the negative camera offset
    screen.blit(scaled_surf, -cam_pos)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()