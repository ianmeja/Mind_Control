import pygame
import sys
import random
import argparse
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels
from brainflow.data_filter import DataFilter, AggOperations
import time
import numpy as np
import pyautogui

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
pygame.display.set_caption("Dino Game")

game_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 24)


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
        super().__init__()
        self.running_sprites = []
        self.ducking_sprites = []

        self.running_sprites.append(pygame.transform.scale(
            pygame.image.load("assets/Dino1.png"), (80, 100)))
        self.running_sprites.append(pygame.transform.scale(
            pygame.image.load("assets/Dino2.png"), (80, 100)))

        self.ducking_sprites.append(pygame.transform.scale(
            pygame.image.load(f"assets/DinoDucking1.png"), (110, 60)))
        self.ducking_sprites.append(pygame.transform.scale(
            pygame.image.load(f"assets/DinoDucking2.png"), (110, 60)))

        self.x_pos = x_pos
        self.y_pos = y_pos
        self.current_image = 0
        self.image = self.running_sprites[self.current_image]
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.velocity = 20
        self.gravity = 3.9
        self.ducking = False

    def jump(self):
        jump_sfx.play()
        if self.rect.centery >= 360:
            while self.rect.centery - self.velocity > 40:
                self.rect.centery -= 1

    def duck(self):
        self.ducking = True

    def unduck(self):
        self.ducking = False

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

        if self.ducking:
            self.image = self.ducking_sprites[int(self.current_image)]
        else:
            self.image = self.running_sprites[int(self.current_image)]


class Cactus(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.sprites = []
        for i in range(1, 7):
            current_sprite = pygame.transform.scale(
                pygame.image.load(f"assets/cacti/cactus{i}.png"), (100, 100))
            self.sprites.append(current_sprite)
        self.image = random.choice(self.sprites)
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def update(self):
        self.x_pos -= game_speed
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))


game_speed = 5
player_score = 0
game_over = False
obstacle_timer = 0
obstacle_spawn = False
obstacle_cooldown = 1000

ground = pygame.image.load("assets/ground.png")
ground = pygame.transform.scale(ground, (1280, 20))
ground_x = 0
cloud = pygame.image.load("assets/cloud.png")
cloud = pygame.transform.scale(cloud, (200, 80))

cloud_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
dino_group = pygame.sprite.GroupSingle()

death_sfx = pygame.mixer.Sound("assets/sfx/lose.mp3")
points_sfx = pygame.mixer.Sound("assets/sfx/100points.mp3")
jump_sfx = pygame.mixer.Sound("assets/sfx/jump.mp3")

CLOUD_EVENT = pygame.USEREVENT
pygame.time.set_timer(CLOUD_EVENT, 3000)


def end_game():
    global player_score, game_speed
    game_over_text = game_font.render("Game Over!", True, "black")
    game_over_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 30))
    score_text = game_font.render(f"Score: {int(player_score)}", True, "black")
    score_rect = score_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 10))
    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    game_speed = 5
    cloud_group.empty()
    obstacle_group.empty()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False, default=0)
    parser.add_argument('--serial-port', type=str, help='serial port', required=True)
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    parser.add_argument('--log', action='store_true')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards', required=True)
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.timeout = args.timeout

    if args.log:
        BoardShim.enable_dev_board_logger()
    else:
        BoardShim.disable_board_logger()

    board = BoardShim(args.board_id, params)
    board.prepare_session()

    board.start_stream(45000, args.streamer_params)

    # initialize calibration and time variables
    time_thres = 100
    max_val = -100000000000
    vals_mean = 0
    num_samples = 2000
    samples = 0

    print("Starting calibration")
    time.sleep(5)  # wait for data to stabilize
    data = board.get_board_data()  # clear buffer

    print("Relax and flex your arm a few times")

    while samples < num_samples:

        data = board.get_board_data()  # get data
        if len(data[1]) > 0:
            DataFilter.perform_rolling_filter(data[1], 2, AggOperations.MEAN.value)  # denoise data
            vals_mean += sum([data[1, i] / num_samples for i in range(len(data[1]))])  # update mean
            samples += len(data[1])
            if np.amax(data[1]) > max_val:
                max_val = np.amax(data[1])  # update max

    flex_thres = 0.4 * ((max_val - vals_mean) ** 2)  # calculate flex threshold - percentage needs to be set per person

    print("Mean Value")
    print(vals_mean)
    print("Max Value")
    print(max_val)
    print("Threshold")
    print(flex_thres)

    print("Calibration complete. Start!")
    prev_time = int(round(time.time() * 1000))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        data = board.get_board_data()  # get data
        if len(data[1]) > 0:
            DataFilter.perform_rolling_filter(data[1], 2, AggOperations.MEAN.value)  # denoise data
            if (int(round(time.time() * 1000)) - time_thres) > prev_time:  # if enough time has gone by since the last flex
                prev_time = int(round(time.time() * 1000))  # update time
                for element in data[1]:
                    if ((element - vals_mean) ** 2) >= flex_thres:  # if above threshold
                        pyautogui.press('space')  # jump
                        break

    board.stop_stream()
    board.release_session()

    DataFilter.write_file(data[1], 'chrome.csv', 'w')

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

