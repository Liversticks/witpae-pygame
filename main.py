# Example file showing a basic pygame "game loop"
import pygame
import json
import math
from pathlib import Path
from geks import RectHexmap, Layout

# 1. LOAD OPTIONS FROM JSON
def load_settings():
    settings_path = Path(__file__).resolve().parent / "options.json"

    with open(settings_path, "r") as f:
        return json.load(f)

settings = load_settings()

GRID_VISIBILITY_THRESHOLD = 0.4

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

def get_hex_points(center_x, center_y, radius):
    points = []
    for i in range(6):
        angle_deg = 60 * i - 30
        angle_rad = math.pi / 180 * angle_deg
        px = center_x + radius * math.cos(angle_rad)
        py = center_y + radius * math.sin(angle_rad)
        points.append((px, py))
    return points

# Grid math for pointy-topped hexes
width_spacing = hex_radius * math.sqrt(3)
height_spacing = hex_radius * 1.5

cols = int(background_rect.width / width_spacing) + 1
rows = int(background_rect.height / height_spacing) + 1

hex_map = RectHexmap(None, (cols, rows), flat=False)
layout = Layout(size=(hex_radius, hex_radius), flat=False)

print(f"Cols: {cols}, Rows: {rows}")

# Camera state
cam_pos = pygame.Vector2(0,0)  # Upper left of background image
zoom_level = 1.0
move_speed = 10
zoom_dirty = False
scaled_surf = background

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
            zoom_level = max(0.1, min(zoom_level, 2.5))
            
            # Calculate new camera position to keep mouse over the same world spot
            # New Cam Pos = (World Mouse * new_zoom) - Mouse Screen Pos
            cam_pos = (world_mouse_before * zoom_level) - mouse_pos

            zoom_dirty = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 1. Get the screen position of the click
            mouse_x, mouse_y = event.pos
            
            # 2. Convert Screen Coordinates to World Coordinates (Zoom level 1.0)
            # Formula: (Screen Pos + Camera Offset) / Zoom
            world_x = (mouse_x + cam_pos.x) / zoom_level
            world_y = (mouse_y + cam_pos.y) / zoom_level
            
            # 3. Use geks to convert the fractional world point to a hex coordinate
            # The 'layout' object contains the base math for your pointy-top grid
            clicked_hex = layout.pixel2hex((world_x, world_y))
            
            print(f"Clicked Screen: ({mouse_x}, {mouse_y})")
            print(f"World Coordinate: ({world_x:.2f}, {world_y:.2f})")
            print(f"Hex Coordinate: q={clicked_hex.q}, r={clicked_hex.r}")

            # if (clicked_hex.q)
            

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
        scaled_surf = pygame.transform.scale(background, new_size)
        zoom_dirty = False
    
    # Blit the scaled image at the negative camera offset
    screen.blit(scaled_surf, -cam_pos)
    
    # 2. Draw the grid dynamically
    # We apply the zoom to the radius and spacing
    if zoom_level > GRID_VISIBILITY_THRESHOLD:
        current_hex_radius = hex_radius * zoom_level
        current_w_spacing = width_spacing * zoom_level
        current_h_spacing = height_spacing * zoom_level
        
        for r in range(rows):
            for c in range(cols):
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

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()