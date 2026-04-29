# Example file showing a basic pygame "game loop"
import pygame
from pathlib import Path

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

background_location = Path(__file__).resolve().parent / "azimuthal-15-165.png"
background = pygame.image.load(background_location).convert_alpha()
background_rect = background.get_rect()

# Camera state
cam_pos = pygame.Vector2(0, 0)  # Top-left of the camera view in world space
zoom_level = 1.0
move_speed = 10

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
            zoom_level += event.y * 0.1
            zoom_level = max(0.1, min(zoom_level, 5.0))
            
            # Calculate new camera position to keep mouse over the same world spot
            # New Cam Pos = (World Mouse * new_zoom) - Mouse Screen Pos
            cam_pos = (world_mouse_before * zoom_level) - mouse_pos

    # 2. PANNING (Arrow keys)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  cam_pos.x -= move_speed
    if keys[pygame.K_RIGHT]: cam_pos.x += move_speed
    if keys[pygame.K_UP]:    cam_pos.y -= move_speed
    if keys[pygame.K_DOWN]:  cam_pos.y += move_speed

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    # RENDER YOUR GAME HERE
    # Scale the image based on zoom level
    new_size = (int(background_rect.width * zoom_level), int(background_rect.height * zoom_level))
    # use scale() for speed, smoothscale() for quality
    scaled_surf = pygame.transform.scale(background, new_size)

    # Blit the scaled image at the negative camera offset
    screen.blit(scaled_surf, -cam_pos)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()