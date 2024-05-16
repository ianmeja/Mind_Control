import pygame
import sys
import random

# In-game variables
game_speed = 6
game_duration = 10000  # in miliseconds
dino_gravity = 4.2
scale_size = 0.01
obstacle_spawn_time = 550 # in miliseconds
jump_height = 280

class Cloud(pygame.sprite.Sprite):
    def __init__(self, image, x_pos, y_pos):
        super().__init__()
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def update(self):
        self.rect.x -= 1


class Dino(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        # sourcery skip: merge-list-append, move-assign-in-block
        super().__init__()
        self.running_sprites = []

        self.running_sprites.append(pygame.transform.scale(
            pygame.image.load("assets/Dino1.png"), (80, 100)))
        self.running_sprites.append(pygame.transform.scale(
            pygame.image.load("assets/Dino2.png"), (80, 100)))

        self.x_pos = x_pos
        self.y_pos = y_pos
        self.current_image = 0
        self.image = self.running_sprites[self.current_image]
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.rect.width = self.rect.width * scale_size
        self.gravity = dino_gravity
        self.ducking = False

    def jump(self):
        jump_sfx.play()
        if self.rect.centery >= 300:
            while self.rect.centery > 360-jump_height:
                self.rect.centery -= 1

    def apply_gravity(self):
        if self.rect.centery <= 360:
            self.rect.centery += self.gravity

    def update(self):
        self.animate()
        self.apply_gravity()

    def animate(self):
        self.current_image += 0.05
        if self.current_image >= 2:
            self.current_image = 0
        self.image = self.running_sprites[int(self.current_image)]


class Cactus(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.sprites = []
        current_sprite = pygame.transform.scale(
            pygame.image.load("assets/cacti/cactus6.png"), (100, 100)
        )
        self.sprites.append(current_sprite)
        self.image = random.choice(self.sprites)
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.rect = self.rect.scale_by(scale_size)

    def update(self):
        self.x_pos -= game_speed
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        
def display_time_remaining():
    elapsed_seconds = timer // 1000
    timer_text = game_font.render(f"Time: {elapsed_seconds}s", True, (0, 0, 0))
    timer_rect = timer_text.get_rect(topright=(780, 10))
    screen.blit(timer_text, timer_rect)

def end_game():
    if times_up:
        game_over_text = game_font.render("Time is up!", True, "black")
    else:
        game_over_text = game_font.render("Game Over!", True, "black")
    game_over_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 30))  # Centro vertical, 30 píxeles arriba del centro horizontal
    screen.blit(game_over_text, game_over_rect)
    
    jump_text = game_font.render(f"Jumps: {int(jump_counter)}", True, "black")
    jump_rect = jump_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 10))
    jump_rect = jump_text.get_rect(center=(640, 340))
    screen.blit(jump_text, jump_rect)
    
    elapsed_seconds = final_time / 1000
    timer_text = game_font.render(f"Final Time: {elapsed_seconds}s", True, (0, 0, 0))
    timer_rect = timer_text.get_rect(topright=(780, 10))
    screen.blit(timer_text, timer_rect)
    
    cloud_group.empty()
    obstacle_group.empty()
    pygame.time.set_timer(OBSTACLE_EVENT, 0)
    
    
def init_screen():
    init_text = game_font.render("Press 'space' to start", True, "black")
    init_rect = init_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 30))  # Centro vertical, 30 píxeles arriba del centro horizontal
    screen.blit(init_text, init_rect)

################
###  PYGAME  ###
################

pygame.init()

# Display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Dino Game")
game_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 24)

# Surfaces
ground = pygame.image.load("assets/ground.png")
ground = pygame.transform.scale(ground, (1280, 20))
ground_x = 0
ground_rect = ground.get_rect(center=(640, 400))
cloud = pygame.image.load("assets/cloud.png")
cloud = pygame.transform.scale(cloud, (200, 80))

# Groups
cloud_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
dino_group = pygame.sprite.GroupSingle()

# Objects
dinosaur = Dino(50, 360)
dino_group.add(dinosaur)

# Sounds
death_sfx = pygame.mixer.Sound("assets/sfx/lose.mp3")
points_sfx = pygame.mixer.Sound("assets/sfx/100points.mp3")
jump_sfx = pygame.mixer.Sound("assets/sfx/jump.mp3")

# Timer & FPS
fps = 120
clock = pygame.time.Clock()

# Events
CLOUD_EVENT = pygame.USEREVENT
OBSTACLE_EVENT = pygame.USEREVENT
pygame.time.set_timer(OBSTACLE_EVENT, obstacle_spawn_time)
pygame.time.set_timer(CLOUD_EVENT, 3000)

# Variables
start_time = 0
timer = 0
jump_counter = 0
game_over = True
times_up = False
final_time = 0

# Game Loop
first_screen = True
running = True
while running:

    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == CLOUD_EVENT:
            current_cloud_y = random.randint(50, 300)
            current_cloud = Cloud(cloud, 1380, current_cloud_y)
            cloud_group.add(current_cloud)
        if event.type == OBSTACLE_EVENT:
            new_obstacle = Cactus(1280, 340)
            obstacle_group.add(new_obstacle)
            
        if event.type == pygame.KEYDOWN and event.key in [
            pygame.K_SPACE,
            pygame.K_UP,
        ]:
            dinosaur.jump()
            
            if game_over: # Game start / restart
                first_screen = False
                game_over = False
                times_up = False
                jump_counter = 0
                start_time = pygame.time.get_ticks()
                pygame.time.set_timer(OBSTACLE_EVENT, obstacle_spawn_time)
            else:
                jump_counter += 1

    screen.fill("white")
    

    # Update timer
    current_time = pygame.time.get_ticks()
    timer = current_time - start_time
    
    # Time over
    if timer >= game_duration and not game_over:
        final_time = timer
        game_over = True
        times_up = True

    # Collisions
    if pygame.sprite.spritecollide(dino_group.sprite, obstacle_group, False) and not game_over:
       final_time = timer
       game_over = True
       death_sfx.play()
        
    if first_screen:
        init_screen()
    elif game_over:
        end_game()

    if not game_over:
        display_time_remaining()
        
        cloud_group.update()
        cloud_group.draw(screen)

        dino_group.update()
        dino_group.draw(screen)

        obstacle_group.update()
        obstacle_group.draw(screen)

        ground_x -= game_speed

        screen.blit(ground, (ground_x, 360))
        screen.blit(ground, (ground_x + 1280, 360))

        if ground_x <= -1280:
            ground_x = 0

    clock.tick_busy_loop(fps)
    pygame.display.update()
    
# Quit Pygame
pygame.quit()
sys.exit()