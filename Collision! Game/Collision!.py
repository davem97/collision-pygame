#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Use up/down/left/right keys to move
# Avoid the circle enemy objects or you lose the game if collided with
# Score goes up by 1 every 5 seconds and is doubled every 30 seconds
# Every 10 seconds the player size is increased
# Every 15 seconds a powerup spawns which reduces player size when collided with
# Every 30 seconds, gain a charge of "brace" to destroy an enemy when colliding with them
# Press and hold the "c" key to activate the brace mechanic, player will temporarily turn blue when it's active
# While in an active game, press and hold the "b" key to view current score, time elapsed, and current brace charges

import pygame
import random
import math
import sys

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Collision!')
enemy_sprite = pygame.image.load('Images/enemy.png').convert()
enemy_sprite.set_colorkey((255, 255, 255))  # Set white to transparent

powerup_sprite = pygame.image.load('Images/powerup.png').convert()
powerup_sprite.set_colorkey((255, 255, 255))

brace_image = pygame.image.load('Images/brace.png').convert()
brace_image.set_colorkey((255, 255, 255))

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (204, 102, 0) 
GREY = (211, 211, 211)
font = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 2
        self.width = 30
        self.height = 30
        self.velocity = [0, 0]  # x, y velocity
        self.jump_strength = -15  # Negative for upward motion
        self.gravity = 0.8
        self.max_fall_speed = 20
        self.is_jumping = False
        self.can_jump = True
        self.jump_start_y = None
        self.update_rect()
        
    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        # Keep player within screen bounds
        self.x = max(0, min(self.x, WIDTH - self.width))
        self.y = max(0, min(self.y, HEIGHT - self.height))
        self.update_rect()

    def jump(self):
        if not self.is_jumping:
            self.velocity[1] = self.jump_strength
            self.jump_start_y = self.y  # Save the starting y position
            self.is_jumping = True

    def update(self):
        if self.is_jumping:
            # Apply gravity
            if self.velocity[1] < self.max_fall_speed:
                self.velocity[1] += self.gravity

            # Update position
            self.y += self.velocity[1]

            # Check if the jump arc has completed
            if self.velocity[1] > 0 and self.y >= self.jump_start_y:  # Player is moving down and has reached or passed start position
                self.y = self.jump_start_y  # Land back at start position
                self.velocity[1] = 0
                self.is_jumping = False
                self.jump_start_y = None
        else:
            # If not jumping, apply normal movement restrictions
            self.y = max(0, min(self.y, HEIGHT - self.height))

        self.update_rect()

    def grow(self):
        # Calculate new dimensions
        new_width = self.width * 1.08
        new_height = self.height * 1.08

        # Ensure the player doesn't grow larger than the screen
        new_width = min(new_width, WIDTH)
        new_height = min(new_height, HEIGHT)

        # Calculate offset to center the growth
        width_increase = new_width - self.width
        height_increase = new_height - self.height

        # Adjust position if player is at the edge
        if self.x + new_width > WIDTH:
            self.x = WIDTH - new_width
        if self.y + new_height > HEIGHT:
            self.y = HEIGHT - new_height
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0

    # Update width, height, and position
        self.width = new_width
        self.height = new_height
        self.update_rect()


    def reduce(self):
        self.width -= self.width * 0.15
        self.height -= self.height * 0.15
        self.update_rect()

    def draw(self):
        # Determine colour based on key press and charges
        keyp = pygame.key.get_pressed()
        if keyp[pygame.K_c] and brace_charges > 0:
            screen.blit(brace_image, self.rect)
        else:
            pygame.draw.rect(screen, RED, self.rect)
        
class AIObject:
    def __init__(self, settings=None):
        if settings is None:
            settings = {}  # Default to an empty dictionary if no settings are passed

        self.settings = settings  # Store settings for later use if needed
        self.x, self.y = random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)
        self.target_x, self.target_y = self.x, self.y
        self.speed = settings['ai_speed']
        self.movement_phase = 0
        self.timer = 0
        self.image = enemy_sprite
        self.angle = 0  # Rotation angle in degrees
        self.orig_image = self.image  # Keep original image for rotation
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.rotation_speed = 5  # Degrees per frame, adjust as needed

    def set_new_target(self):
        self.target_x = random.randint(50, WIDTH-50)
        self.target_y = random.randint(50, HEIGHT-50)

    def move(self, settings=None):
        if settings is None:
            settings = self.settings  # Fallback to instance's settings if not provided
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        # Frames calculation for 2-6 seconds at 50 FPS
        # 2 seconds * 50 FPS = 100 frames
        # 6 seconds * 50 FPS = 300 frames
        if distance > self.speed:
            self.x += (dx / distance) * settings['ai_speed']
            self.y += (dy / distance) * settings['ai_speed']

            # Continuous rotation
            self.angle = (self.angle + self.rotation_speed) % 360  # Keep angle between 0 and 360
        else:
            self.x, self.y = self.target_x, self.target_y
            self.timer += 1
            if self.timer >= random.randint(*settings['begin_move_interval']):
                if self.movement_phase == 0:
                    self.set_new_target()
                    self.movement_phase = 1
                elif self.movement_phase == 1:
                    self.set_new_target()
                    self.movement_phase = 2
                elif self.movement_phase == 2:
                    # Check if we're in hard mode before applying the delay
                    if settings.get('current_difficulty', 'easy') == 'hard':
                        self.movement_phase = 3  # New phase for delay before deletion
                        self.timer = 0  # Reset timer for delay phase
                    else:
                        self.movement_phase = 0
                        self.timer = 0
                        return "delete"
                elif self.movement_phase == 3:  # Delay phase
                    if self.timer >= 50:  # 1 second at 50 FPS
                        self.movement_phase = 0
                        self.timer = 0
                        return "delete"
                self.timer = 0
        self.rect.center = (self.x, self.y)
        return None  # Return None if not to be deleted

    def check_overlap_with_player(self, player):
        # Create a rect for the potential spawn position
        potential_rect = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        return player.rect.colliderect(potential_rect)
    
    @staticmethod
    def spawn_multiple(settings):
        global spawned_at_least_5
        if len(ai_objects) >= 5 and not spawned_at_least_5:
            for _ in range(3):
                ai_objects.append(AIObject(settings))
            spawned_at_least_5 = True
        global spawned_at_least_10
        if len(ai_objects) >= 10 and not spawned_at_least_10:
            for _ in range(3):
                ai_objects.append(AIObject(settings))
                spawned_at_least_10 = True
            
    def draw(self):
        # Rotate the image
        rotated_image = pygame.transform.rotate(self.orig_image, self.angle)
        # Get a new rect with the center of the original rect
        new_rect = rotated_image.get_rect(center=self.rect.center)
        # Draw the rotated image
        screen.blit(rotated_image, new_rect)

class Powerup:
    def __init__(self):
        self.x, self.y = random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)
        self.image = powerup_sprite  
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update_rect(self):
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def load_image_with_transparency(path, colorkey=(255, 255, 255)):
    image = pygame.image.load(path).convert()
    image.set_colorkey(colorkey)
    return image

import pygame
import random

class MovingObject:
    def __init__(self, image_path):
        self.image = load_image_with_transparency(image_path)
        self.rect = self.image.get_rect()
        self.angle = 0
        self.is_active = False  # New flag to track if the object is currently in view or moving
        self.original_image = self.image.copy()
        self.speed = 3  # Fixed speed
        self.rotation_speed = 4  # Fixed rotation speed

    def reset_position(self):
        if random.choice([True, False]):  # Spawn at bottom
            self.rect.midbottom = (random.randint(0, WIDTH), HEIGHT + 20)
            self.speed = -4.5  # Negative speed for moving up
        else:  # Spawn at top
            self.rect.midtop = (random.randint(0, WIDTH), -20)
            self.speed = 4.5   # Positive speed for moving down
        self.is_active = True

    def move(self):
        if self.is_active:
            self.rect.move_ip(0, self.speed)
            if self.rect.top > HEIGHT or self.rect.bottom < 0:
                self.is_active = False

    def rotate(self):
        if self.is_active:
            # Fixed rotation speed
            self.angle = (self.angle + self.rotation_speed) % 360
            self.image = pygame.transform.rotate(self.original_image, self.angle).convert_alpha()
            self.rect = self.image.get_rect(center=self.rect.center)

GAME_SETTINGS = {
    'easy': {
        'spawn_interval': (2500, 3500),  # milliseconds
        'begin_move_interval': (200, 300), # 2 seconds, 4 seconds
        'ai_speed': 2.5,  # Example setting
        'max_ai_objects': 20  # Maximum number of AI objects
    },
    'hard': {
        'spawn_interval': (1500, 3000),  # Faster spawn rate
        'begin_move_interval': (300, 650), # 3 seconds, 5 seconds
        'ai_speed': 2.8,  # Faster AI movement
        'max_ai_objects': 40  # More AI objects
    }
}

# Default difficulty
current_difficulty = 'easy'

def game_loop(difficulty='easy'):
    global spawned_at_least_5, spawned_at_least_10, powerup, powerup_spawned, game_over, running, ai_objects
    settings = GAME_SETTINGS[difficulty].copy()
    settings['current_difficulty'] = difficulty
    ai_objects = []
    player = Player()
    game_over = False  # Before the main loop, define game state
    running = True  # Main game loop

    last_spawn_time = pygame.time.get_ticks() - random.randint(*settings['spawn_interval'])
    
    def display_time(time_ms):
        """Return time in milliseconds as string mm:ss."""
        minutes, seconds = divmod(int(time_ms / 1000), 60)
        return f"{minutes: 2}:{seconds:02}"
    # Have either 5 or 10 total AI objects spawned into the game
    spawned_at_least_5 = False
    spawned_at_least_10 = False

    # Powerup variables - before the main game loop
    powerup = None
    powerup_spawned = False
    powerup_destroy_time = 0

    # Player brace mechanic
    global brace_charges, charge_timer, charge_interval, powerup_destroy_timer, last_score_increase, last_score_double, timer_event
    brace_charges = 0
    charge_timer = 0  # Timer to track elapsed time for adding charges
    charge_interval = 30  # Time in seconds to add a charge

    # Score related variables, set all to 0 prior to the game starting
    global score
    score = 0
    last_score_increase = 0
    last_score_double = 0
    
    # Timer variables
    timer_event = 10000  # This is 10 seconds in milliseconds
    last_spawn_time = pygame.time.get_ticks()  # Checks when the last enemy object was spawned into the game
    last_time = pygame.time.get_ticks()  # Handles the player growth timer
    start_timer = pygame.time.get_ticks()  # This is used for accumulating brace mechanic charges
    clock = pygame.time.Clock()  # Used for FPS
    elapsed_time = pygame.time.get_ticks()  # Used for scoring
    start_time = pygame.time.get_ticks()  # Used together with elapsed_time for scoring

    while running:
        current_time = pygame.time.get_ticks()
        # Update the timer
        charge_timer = pygame.time.get_ticks() - start_timer
        if not game_over:
            elapsed_time = pygame.time.get_ticks() - start_time
            if elapsed_time - last_score_increase >= 5000:
                score += 1
                last_score_increase += 5000

            if elapsed_time - last_score_double >= 30000:
                score *= 2
                last_score_double += 30000

            if charge_timer >= 30000:
                brace_charges += 1  # Add a brace charge
                start_timer = pygame.time.get_ticks()

        if game_over:
            screen.fill(BLACK)
            font = pygame.font.Font(None, 36)

            game_over_text = font.render("Game Over! Press SPACE to restart or ESC to quit.", True, WHITE)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

            time_text = font.render(f"Time: {display_time(elapsed_time)}", True, WHITE)
            screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 - time_text.get_height() // 2))

            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 - score_text.get_height() // 2 + 25))

            screen.blit(game_over_text, game_over_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    game_over = True
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Reset the game here
                    spawned_at_least_5 = False
                    spawned_at_least_10 = False
                    
                    ai_objects = []
                    player = Player()  # Assuming player's position and size are reset in its __init__
                    game_over = False
                    powerup = None
                    powerup_spawned = False
                    powerup_destroy_time = pygame.time.get_ticks()
                    last_time = pygame.time.get_ticks()  # Reset the last time for player growth
                    elapsed_time = pygame.time.get_ticks()
                    start_time = pygame.time.get_ticks()
                    current_time = pygame.time.get_ticks()
                    score = 0
                    last_score_increase = 0
                    last_score_double = 0
                    brace_charges = 0
                    start_timer = pygame.time.get_ticks()
                    last_spawn_time = current_time - random.randint(0, 1000) # Restart AI object spawn delay              
                    continue
            continue  # Skip the rest of the loop to avoid processing game logic

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                return

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.move(0, -1)
        if keys[pygame.K_DOWN]:
            player.move(0, 1)
        if keys[pygame.K_LEFT]:
            player.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            player.move(1, 0)
        if keys[pygame.K_x]:
            player.jump()
        if keys[pygame.K_BACKSPACE]:
            running = False

        player.update()

        if current_time - last_spawn_time > random.randint(*settings['spawn_interval']):
            if len(ai_objects) < settings['max_ai_objects']:
                spawn_count = 2 if settings['current_difficulty'] == 'hard' else 1
                for _ in range(spawn_count):
                    new_obj = AIObject(settings)
                    attempts = 0
                    max_attempts = 100
                    while new_obj.check_overlap_with_player(player) and attempts < max_attempts:
                        new_obj.x, new_obj.y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
                        attempts += 1
                    if attempts < max_attempts:
                        ai_objects.append(new_obj)
                last_spawn_time = current_time

        if current_time - last_time >= timer_event:
            # Update the player's size
            player.grow()  # This calls a method on the player instance
            last_time = current_time  # Reset the last time you grew the player

        AIObject.spawn_multiple(settings)

        if powerup is None and not powerup_spawned and current_time - powerup_destroy_time >= 15000:
            powerup = Powerup()
            powerup_spawned = True
            last_powerup_time = current_time  # Update this when a new powerup spawns

        if powerup:
            player.update_rect()  # Ensure the rect is up to date
            if player.rect.colliderect(powerup.rect):
                player.reduce()  # Reduce player size
                powerup = None
                powerup_spawned = False
                powerup_destroy_time = current_time  # Time when powerup was last destroyed

        to_remove = []  # Create a temporary list to track objects to remove

        # Before drawing anything, update all game objects and check for collisions:
        for obj in ai_objects[:]:  # Use a copy to safely modify the list during iteration
            action = obj.move(settings) # Pass settings here
            if action == "delete":
                ai_objects.remove(obj)

        # Collision could be checked here if you want to check immediately after each move for more precise collision detection
        brace_key = pygame.key.get_pressed()
        if brace_key[pygame.K_c] and brace_charges > 0:
            for obj in ai_objects[:]:  # Iterate again for checking collisions
                if player.rect.colliderect(pygame.Rect(obj.x - 15, obj.y - 15, 30, 30)):
                    to_remove.append(obj)  # Track for removal
                    brace_charges -= 1
                    score += 5
                    if brace_charges < 0:
                        brace_charges = 0  # Ensure it doesn't go below zero
        else:
            # Collision check after all movements:
            player.update_rect()
            for obj in ai_objects:  # No need for a copy here since we're not modifying the list
                if player.rect.colliderect(pygame.Rect(obj.x - 15, obj.y - 15, 30, 30)):
                    game_over = True
                    to_remove.append(obj)
                    break

        # Remove all objects that are to be deleted after all checks
        for obj in to_remove:
            if obj in ai_objects:
                ai_objects.remove(obj)

        # Check if game is over before drawing to avoid unnecessary operations
        if game_over:
            continue  # This skips the drawing and updating display part if game over

        screen.fill(BLACK)
        
        for obj in ai_objects[:]:
            action = obj.move(settings)
            if action == "delete":
                ai_objects.remove(obj)
            else:
                obj.draw()

        player.draw()

        if powerup:
            powerup.draw(screen)

        keyp = pygame.key.get_pressed()
        if keyp[pygame.K_b]:
            # Render score, current charges and time elapsed during an active game
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            time_text = font.render(f"Time elapsed: {display_time(elapsed_time)}", True, WHITE)
            screen.blit(time_text, (565, 10))
            brace_text = font.render(f"Charges: {brace_charges}", True, WHITE)
            screen.blit(brace_text, (10, 35))
        pygame.display.flip()
        clock.tick(50)  # 50 FPS for smooth movement

    pygame.quit()
    sys.exit()
def show_how_to_play():
    while True:
        screen.fill(GREY)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE):
                return  # Exit the function to go back to the main menu

        # Define the font and color
        title_font = pygame.font.Font(None, 45)  # Larger font for the title
        font = pygame.font.Font(None, 34)        # Regular font for the instructions
        title_color = (204, 102, 0)                # Red color for the title text
        text_color = BLACK                       # Black color for the other text

        # Render and display "Game Information" in red with the larger font
        title_text = title_font.render("Game Information", True, title_color)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        # Add a gap before displaying the other instructions
        instructions = [
            "Use arrow keys to move.",
            "Avoid the enemy objects.",
            "Press and hold 'c' to use a brace charge to destroy an enemy object.",
            "Press and hold 'b' to toggle the display of score, time and charges.",
            "Pick up power-ups to reduce player size.",
            "The longer you survive, the more points you get.",
            "Press Backspace to return to the main menu."
        ]
        
        y_offset = 150  # Start a bit lower to create a gap after the title
        for line in instructions:
            text = font.render(line, True, text_color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 35  # Move to the next line

        pygame.display.flip()

        
def show_menu():
    global current_difficulty
    current_selection = 0  # Start with the first option
    options = ["Easy Mode", "Hard Mode", "How to Play", "Quit"]
    # Load the logo image
    
    logo = pygame.image.load('Images/collision_logo.png')  # Replace with the actual path to your logo
    logo_rect = logo.get_rect(center=(WIDTH // 2, 150))  # Position the logo in the center top
    
    clock = pygame.time.Clock()
    
    # Initialize the moving object
    moving_object = MovingObject('Images/animation.png')
    first_spawn = True
    last_spawn_time = pygame.time.get_ticks()
    
    while True:
        screen.fill(GREY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_selection = (current_selection - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    current_selection = (current_selection + 1) % len(options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:  # Enter key selection
                    if options[current_selection] == "Easy Mode":
                        current_difficulty = 'easy'
                        game_loop(current_difficulty)
                    elif options[current_selection] == "Hard Mode":
                        current_difficulty = 'hard'
                        game_loop(current_difficulty)
                    elif options[current_selection] == "How to Play":
                        show_how_to_play()
                    elif options[current_selection] == "Quit":
                        pygame.quit()
                        sys.exit()

        # Draw the menu options
        for index, option in enumerate(options):
            if index == current_selection:
                color = ORANGE  # Highlight color
            else:
                color = BLACK  # Normal color

            text = font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 280 + 35 * index))

        screen.blit(logo, logo_rect)
        
        current_time = pygame.time.get_ticks()
        
        # Logic for spawning the object:
        if first_spawn:
            if current_time - last_spawn_time > random.randint(10000, 13000):
                first_spawn = False
                moving_object.reset_position()
                last_spawn_time = current_time
        else:
            if current_time - last_spawn_time > random.randint(10000, 13000):
                if not moving_object.is_active:  # Only reset if the current object is not active
                    moving_object.reset_position()
                    last_spawn_time = current_time

        moving_object.move()
        moving_object.rotate()
        if moving_object.is_active:
            screen.blit(moving_object.image, moving_object.rect)
        
        pygame.display.flip()
        clock.tick(50)
        
if __name__ == "__main__":
    show_menu()


# In[ ]:




