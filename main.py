# Example file showing a basic pygame "game loop"
import json
import math
from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel

from strategic_map import StrategicMap

# 1. LOAD OPTIONS FROM JSON
def load_settings():
    settings_path = Path(__file__).resolve().parent / "options.json"

    with open(settings_path, "r") as f:
        return json.load(f)

settings = load_settings()

GRID_VISIBILITY_THRESHOLD = 0.4

HEX_NM = 20

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720), flags=pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

manager = pygame_gui.UIManager((1280, 720))
# Create the menu bar
# We use anchors to ensure it stays pinned to the top and stretches to the full width
menu_bar = UIPanel(
    relative_rect=pygame.Rect(0, 0, screen.get_width(), 40),
    manager=manager,
    starting_height=1,  # Ensures it draws above other UI elements in the same layer
    anchors={
        'top': 'top',
        'bottom': 'top',
        'left': 'left',
        'right': 'right'
    }
)

TESTING_MAP_INDEX = 2

MAP_WIDTH = settings["maps"][TESTING_MAP_INDEX]["mapWidth"]
strat_map = StrategicMap(str(Path(__file__).resolve().parent / settings["maps"][TESTING_MAP_INDEX]["backgroundImagePath"]), MAP_WIDTH, HEX_NM)

def get_hex_points(center_x, center_y, radius):
    points = []
    for i in range(6):
        angle_deg = 60 * i - 30
        angle_rad = math.pi / 180 * angle_deg
        px = center_x + radius * math.cos(angle_rad)
        py = center_y + radius * math.sin(angle_rad)
        points.append((px, py))
    return points

# Camera state
cam_pos = pygame.Vector2(0,0)  # Upper left of background image
zoom_level = 1.0
move_speed = 10
zoom_dirty = False
scaled_surf = strat_map.get_background()

SHOW_GRID = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            manager.set_window_resolution(event.size)

        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            
            # Calculate world position of mouse before zoom
            # (Mouse screen pos + Camera pos) / old_zoom
            old_zoom = zoom_level
            world_mouse_before = (mouse_pos + cam_pos) / old_zoom
            
            # Update zoom level
            # (how far out to zoom, how far zoomed in)
            zoom_level += event.y * 0.1
            zoom_level = max(0.1, min(zoom_level, 2.5))
            
            # Calculate new camera position to keep mouse over the same world spot
            # New Cam Pos = (World Mouse * new_zoom) - Mouse Screen Pos
            cam_pos = (world_mouse_before * zoom_level) - mouse_pos

            zoom_dirty = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not manager.get_hovering_any_element():
                # 1. Get the screen position of the click
                mouse_x, mouse_y = event.pos
                
                # 2. Convert Screen Coordinates to World Coordinates (Zoom level 1.0)
                # Formula: (Screen Pos + Camera Offset) / Zoom
                world_x = (mouse_x + cam_pos.x) / zoom_level
                world_y = (mouse_y + cam_pos.y) / zoom_level
                print(f"Clicked Screen: ({mouse_x}, {mouse_y})")
                print(f"World Coordinate: ({world_x:.2f}, {world_y:.2f})")
                # 3. Convert "World Pixels" to Meters
                # px_per_meter is calculated in your main.py as: background_rect.width / MAP_WIDTH
                click_x_meters = world_x / strat_map.get_px_per_m()
                click_y_meters = world_y / strat_map.get_px_per_m()
                print(f"Clicked Location Offset (Meters): ({click_x_meters},{click_y_meters})")

                strat_map.on_click_hex((world_x, world_y))

        manager.process_events(event)

    manager.update(time_delta)

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
        new_size = (int(strat_map.get_rect().width * zoom_level), int(strat_map.get_rect().height * zoom_level))
        scaled_surf = pygame.transform.scale(strat_map.get_background(), new_size)
        zoom_dirty = False
    
    # Blit the scaled image at the negative camera offset
    screen.blit(scaled_surf, -cam_pos)
    
    # 2. Draw the grid dynamically
    # We apply the zoom to the radius and spacing
    if zoom_level > GRID_VISIBILITY_THRESHOLD and SHOW_GRID:
        current_hex_radius = strat_map.get_hex_radius_px() * zoom_level
        current_w_spacing = strat_map.get_width_spacing() * zoom_level
        current_h_spacing = strat_map.get_height_spacing() * zoom_level
        
        for r in range(strat_map.get_rows()):
            for c in range(strat_map.get_cols()):
                # Calculate screen position: (World Pos * Zoom) - Camera Offset
                # Since we already have the spacing constants, we just scale them
                # Pointy-top: offset every other row (r % 2) horizontally
                x = (c * current_w_spacing + (r % 2) * (current_w_spacing / 2)) - cam_pos.x
                y = (r * current_h_spacing) - cam_pos.y
            
                # Culling: Only draw if the hex is actually on the screen
                if -current_hex_radius < x < screen.get_width() + current_hex_radius and \
                -current_hex_radius < y < screen.get_height() + current_hex_radius:
                    # The '1' here ensures the border is ALWAYS 1 pixel thick
                    pygame.draw.polygon(screen, (0, 0, 0), get_hex_points(x, y, current_hex_radius), 1)

    manager.draw_ui(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

pygame.quit()