from map import boards
import pygame
import math
import time
import copy
import psycopg2
import os
pygame.init()
pygame.display.set_caption("PACKEDMAN")

WIDTH = 900
HEIGHT = 950
PI= math.pi
screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.RESIZABLE)
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
level = copy.deepcopy(boards)
color = "blue" #change color variable to change the color of the level lines in future levels
run = True
player_sprites = []
conn = psycopg2.connect(host = "localhost", dbname  = "pacgame_db", user="postgres", password = "Aliame123", port= 5432)
cur = conn.cursor()
for i in range(1,5):
    #pacman player entity sprites => 1 through 4 eating sequence.
    player_sprites.append(pygame.transform.scale(pygame.image.load(f'C:/Users/User/Desktop/projects/pacman/assets/pacman_sprites/{i}.png'), (45, 45))) #load the sprites and scale down to 45x45 pixels.
blinky_img = pygame.transform.scale(pygame.image.load(f'C:/Users/User/Desktop/projects/pacman/assets/ghost_sprites/red.png'), (45, 45))
pinky_img = pygame.transform.scale(pygame.image.load(f'C:/Users/User/Desktop/projects/pacman/assets/ghost_sprites/pink.png'), (45, 45))
inky_img = pygame.transform.scale(pygame.image.load(f'C:/Users/User/Desktop/projects/pacman/assets/ghost_sprites/blue.png'), (45, 45))
clyde_img = pygame.transform.scale(pygame.image.load(f'C:/Users/User/Desktop/projects/pacman/assets/ghost_sprites/orange.png'), (45, 45))
scared_img = pygame.transform.scale(pygame.image.load(f'C:/Users/User/Desktop/projects/pacman/assets/ghost_sprites/powerup.png'), (45, 45))
packed_img = pygame.transform.scale(pygame.image.load(f'C:/Users/User/Desktop/projects/pacman/assets/ghost_sprites/dead.png'), (45, 45))
cherry_img = pygame.transform.scale(pygame.image.load(f'C:/Users/User/Desktop/projects/pacman/assets/power_ups/cherry.png'), (60, 60))
powerup_img = pygame.transform.scale(pygame.image.load(f'C:/Users/User/Desktop/projects/pacman/assets/power_ups/powerup1.png'), (45, 45))
watermelon_img = pygame.transform.scale(pygame.image.load(f'C:/Users/User/Desktop/projects/pacman/assets/power_ups/watrermelon.png'), (55, 55))
#GHOST STARTING POSITIONS + direction:
blinky_x, blinky_y, blinky_direction = 56, 58, 0
inky_x, inky_y, inky_direction = 440, 388, 2
pinky_x, pinky_y, pinky_direction = 370, 438, 2
clyde_x, clyde_y, clyde_direction = 440, 438, 2
blinky_dead, blinky_box = False, False
inky_dead, inky_box = False, False
pinky_dead, pinky_box= False, False
clyde_dead, clyde_box= False, False
#chosing the ghost speeds :
ghost_speeds = [2, 2, 2, 2]
pygame.display.set_caption("PACKEDMAN")
pygame.display.set_icon(player_sprites[0])
#starting position:
player_x = 425
player_y = 663
direction = 0
counter = 0
flicker = False
turns_allowed = [False, False, False, False] #RLUD
direction_command = 0
player_speed = 2
score = 0
power_up = False
power_counter = 0
eaten_ghosts = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)] #TARGETS OF GHOSTS WILL BE BY DEFAULT THE PLAYERS.
moving = False
start_up_counter =0
lives = 3
game_over = False
game_won = False
needLogin = True
game_paused = False
class Ghost: #THE GHOST CLASS
    def __init__(self, x, y, target, speed, img, direction, dead, box, id):
        self.target = target
        self.x, self.y = x, y
        self.speed = speed
        self.center_x = self.x + 22
        self.center_y = self.y + 22
        self.img = img
        self.target = target
        self.direction = direction
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()
    def get_target(self):
        return self.target
    def get_curx(self):
        return self.x
    def get_cury(self):
        return self.y
    def get_speed(self):
        return self.speed
    def get_img(self):
        return self.img
    def get_dead(self):
        return self.dead
    def get_box(self):
        return self.box
    def get_id(self):
        return self.id
    def set_speed(self, new_speed):
        self.speed = new_speed
    def check_collisions(self):
        # R, L, U, D
        num1 = ((HEIGHT - 50) // 32)
        num2 = (WIDTH // 30)
        num3 = 15
        self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns[2] = True
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[1] = True
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[0] = True
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True

        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.x < 550 and 370 < self.y < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    def move_clyde(self): #Clyde movie algo
        # r, l, u, d
        # clyde is going to turn whenever advantageous for pursuit
        if self.direction == 0:
            if self.target[0] > self.x and self.turns[0]:
                self.x += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                if self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                else:
                    self.x += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x and self.turns[1]:
                self.x -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                if self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                else:
                    self.x -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x and self.turns[1]:
                self.direction = 1
                self.x -= self.speed
            elif self.target[1] < self.y and self.turns[2]:
                self.direction = 2
                self.y -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                else:
                    self.y -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y and self.turns[3]:
                self.y += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                else:
                    self.y += self.speed
        if self.x < -30:
            self.x = 900
        elif self.x > 900:
            self.x = 30
        return self.x, self.y, self.direction

    def move_blinky(self):
        # r, l, u, d
        # blinky is going to turn whenever colliding with walls, otherwise continue straight
        if self.direction == 0:
            if self.target[0] > self.x and self.turns[0]:
                self.x += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
            elif self.turns[0]:
                self.x += self.speed
        elif self.direction == 1:
            if self.target[0] < self.x and self.turns[1]:
                self.x -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
            elif self.turns[1]:
                self.x -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y and self.turns[2]:
                self.direction = 2
                self.y -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
            elif self.turns[2]:
                self.y -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y and self.turns[3]:
                self.y += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
            elif self.turns[3]:
                self.y += self.speed
        if self.x < -30:
            self.x = 900
        elif self.x > 900:
            self.x = 30
        return self.x, self.y, self.direction

    def move_inky(self):
        # r, l, u, d
        # inky turns up or down at any point to pursue, but left and right only on collision
        if self.direction == 0:
            if self.target[0] > self.x and self.turns[0]:
                self.x += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                if self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                else:
                    self.x += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x and self.turns[1]:
                self.x -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                if self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                else:
                    self.x -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y and self.turns[2]:
                self.direction = 2
                self.y -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
            elif self.turns[2]:
                self.y -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y and self.turns[3]:
                self.y += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
            elif self.turns[3]:
                self.y += self.speed
        if self.x < -30:
            self.x = 900
        elif self.x > 900:
            self.x - 30
        return self.x, self.y, self.direction

    def move_pinky(self):
        if self.direction == 0:
            if self.target[0] > self.x and self.turns[0]:
                self.x += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
            elif self.turns[0]:
                self.x += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x and self.turns[1]:
                self.x -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
            elif self.turns[1]:
                self.x -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x and self.turns[1]:
                self.direction = 1
                self.x -= self.speed
            elif self.target[1] < self.y and self.turns[2]:
                self.direction = 2
                self.y -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.target[1] > self.y and self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                else:
                    self.y -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y and self.turns[3]:
                self.y += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x and self.turns[0]:
                    self.direction = 0
                    self.x += self.speed
                elif self.target[0] < self.x and self.turns[1]:
                    self.direction = 1
                    self.x -= self.speed
                else:
                    self.y += self.speed
        if self.x < -30:
            self.x = 900
        elif self.x > 900:
            self.x = 30
        return self.x, self.y, self.direction

    def draw(self):
        if(not power_up and not self.dead) or (eaten_ghosts[self.id] and power_up and not self.dead):
            screen.blit(self.img, (self.x, self.y))
        elif power_up and not self.dead and not eaten_ghosts[self.id]:
            screen.blit(scared_img, (self.x, self.y)) #if the ghost is spooked when power up is active for player
        else:
            screen.blit(packed_img, (self.x, self.y)) #if ghost is dead : change image to the dead.png
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y -18), (36, 36)) #define the hitbox rectangle around the ghosts.
        return ghost_rect



def draw_stats():
    score_text = font.render(f'Score: {score}', True, 'white')
    info_txt = font.render("Press P to pause", True, 'White')
    screen.blit(info_txt, (300, 920))
    screen.blit(score_text, (10, 920))
    if power_up:
        screen.blit(powerup_img,(600,910))
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_sprites[0], (25,25)), (650  + i * 40, 915))
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render("Game Over! Press Space to restart!", True, 'red')
        screen.blit(gameover_text, (100, 300))
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render("You win! Press Space to restart!", True, 'green')
        screen.blit(gameover_text, (100, 300))

def check_collisions(player_score, player_power_up, power_count, eaten_ghosts): #CHECK IF WE EATING SOMETHING -> EITHER point or power up!!!!
    num1 = (HEIGHT - 50) //32
    num2 = WIDTH//30
    if 0 < player_x < 870:
        if level[center_Y//num1][center_X//num2]== -2:
            level[center_Y//num1][center_X//num2] =0
            player_score += 1250
        if level[center_Y//num1][center_X//num2]== -1:
            level[center_Y//num1][center_X//num2] =0
            player_score += 1000
        if level[center_Y//num1][center_X//num2]==1:
            level[center_Y//num1][center_X//num2] =0
            player_score += 10
        if level[center_Y//num1][center_X//num2]==2:
            level[center_Y//num1][center_X//num2] =0
            player_score += 100
            player_power_up = True
            power_count = 0
            #power_up = False
            eaten_ghosts = [False, False, False, False]

    return player_score, player_power_up, power_count, eaten_ghosts

font2 = pygame.font.SysFont("arialblack", 40)
TEXT_COLUMN = (255,255,255)
def draw_text(text, font, text_col, x, y):

    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

def draw_board(lvl):
    num1 = ((HEIGHT -50) // 32)
    num2 = ((WIDTH //30)) #floor division for the width and height.
    for i in range(len(lvl)): #loop through all rows
        for j in range(len(lvl[i])): #loop through all elements of rows
            if lvl[i][j] == -2: #water melon!
                screen.blit(watermelon_img,(j*num2 -10 , i*num1-20))
            if lvl[i][j] == -1: #Cherry!
                screen.blit(cherry_img,(j*num2 -15 , i*num1-8))
            if lvl[i][j] == 1: #small dot draw mehtod
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5*num2), i*num1 + (0.5 * num1)), 4)
            if lvl[i][j] == 2 and not flicker: #BIG dot draw mehtod
                screen.blit(powerup_img, (j * num2 - 10, i * num1 - 8))
                #pygame.draw.circle(screen, 'white', (j * num2 + (0.5*num2), i*num1 + (0.5 * num1)), 10)
            if lvl[i][j] == 3: #line1  draw mehtod
                pygame.draw.line(screen, color, (j*num2+(0.5*num2), i*num1), (j*num2+(0.5*num2), i*num1 + num1),3 )
            if lvl[i][j] == 4: #line2  draw mehtod
                pygame.draw.line(screen, color, (j*num2, i*num1+(0.5*num1)), (j*num2+num2, i*num1 + (0.5*num1)),3 )
            if lvl[i][j] == 9:  # GHOST DOOR  draw mehtod
                pygame.draw.line(screen, 'gray', (j * num2, i * num1 + (0.5 * num1)),
                               (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if lvl[i][j] == 5:  # arc1  draw mehtod
                pygame.draw.arc(screen, color,[(j*num2 - (num2*0.4))-2, (i * num1 + (0.5*num1)), num2, num1], 0,PI/2, 3)
            if lvl[i][j] == 6:  # arc2  draw mehtod
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], PI/2, PI, 3)
            if lvl[i][j] == 7:  # arc3  draw mehtod
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)) , (i * num1 - (0.4 * num1)), num2, num1], PI, 1.5*PI, 3)
            if lvl[i][j] == 8:  # arc4  draw mehtod
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) -2, (i * num1 - (0.4 * num1)), num2, num1], 1.5*PI, 2*PI , 3)

def move_player(playerx, playery): #R L U D
    if direction ==0 and turns_allowed[0]:
        playerx += player_speed
    if direction ==1 and turns_allowed[1]:
        playerx -= player_speed
    if direction ==2 and turns_allowed[2]:
        playery -= player_speed
    if direction ==3 and turns_allowed[3]:
        playery += player_speed
    return playerx, playery

def draw_player():
    if direction == 0:#right
        screen.blit(player_sprites[counter // 5], (player_x, player_y))
    elif direction == 1:#left
        screen.blit(pygame.transform.flip(player_sprites[counter // 5], True, False) , (player_x, player_y))
    elif direction == 2:#up
        screen.blit(pygame.transform.rotate(player_sprites[counter // 5], 90), (player_x, player_y))
    elif direction == 3:#down
        screen.blit(pygame.transform.rotate(player_sprites[counter // 5],270),  (player_x, player_y))

def get_targets(blinkyx, blinkyy, pinkyx, pinkyy, inkyx, inkyy, clydex, clydey):
    if player_x < 450:
        runaway_x = 900 #target location to get away from player during powerup
    else:
        runaway_x = 0 #go to the opposite!
    if player_y < 450:
        runaway_y = 900
    else:
        runaway_y = 0
    return_target = (380, 400)
    if power_up:
        if not blinky.dead and not eaten_ghosts[0]:
            blinky_target = (runaway_x, runaway_y)
        elif not blinky.dead and not eaten_ghosts[0]:
            if 340 < blinkyx < 560 and 340 < blinkyy < 500:
                blinky_target = (400, 100)
            else:
                blinky_target = (player_x, player_y)
        else:
            blinky_target = return_target
        if not inky.dead and not eaten_ghosts[1]:
            inky_target = (runaway_x, player_y)
        elif not inky.dead and eaten_ghosts[1]:
            if 340 < inkyx < 560 and 340 < inkyy < 500:
                inky_target = (400, 100)
            else:
                inky_target = (player_x, player_y)
        else:
            inky_target = return_target
        if not pinky_dead and not eaten_ghosts[2]:
            pinky_target = (player_x, runaway_y)
        elif not pinky.dead and eaten_ghosts[2]:
            if 340 < pinkyx < 560 and 340 < pinkyy < 500:
                pinky_target = (400,100)
            else:
                pinky_target = (player_x, player_y)
        else:
            pinky_target = return_target
        if not clyde_dead and not eaten_ghosts[3]:
            clyde_target = (450, 450)
        elif not clyde.dead and eaten_ghosts[3]:
            if 340 < pinkyx < 560 and 340 < pinkyy < 500:
                clyde_target = (400, 100)
            else:
                clyde_target = (player_x, player_y)
        else:
            clyde_target = return_target
    else:
        if not blinky.dead:
            if 340 < blinkyx < 560 and 340 < blinkyy < 500 :
                blinky_target = (400, 100)
            else:
                blinky_target = (player_x, player_y)
        else:
            blinky_target = return_target

        if not inky.dead:
            if 340 < inkyx < 560 and 340 < inkyy < 500 :
                inky_target = (400, 100)
            else:
                inky_target = (player_x, player_y)
        else:
            inky_target = return_target

        if not pinky.dead:
            if 340 < pinkyx < 560 and 340 < pinkyy < 500 :
                pinky_target = (400, 100)
            else:
                pinky_target = (player_x, player_y)
        else:
            pinky_target = return_target

        if not clyde.dead   :
            if 340 < clydex < 560 and 340 < clydey < 500 :
                clyde_target = (400, 100)
            else:
                clyde_target = (player_x, player_y)
        else:
            clyde_target = return_target
    return [blinky_target, inky_target, pinky_target, clyde_target]

def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT -50)//32
    num2 = (WIDTH//30)
    num3 = 15 #leeway
    if centerx //30 < 29:
        if direction == 0:
            if level[centery//num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
        if direction == 1:
            if level[centery//num1][(centerx + num3) // num2] < 3: #can pass through nums less than 3. the dots!
                    turns[0] = True
        if direction == 2:
            if level[(centery+num3)//num1][centerx // num2] < 3:
                    turns[3] = True
        if direction == 3:
            if level[(centery-num3)//num1][centerx // num2] < 3:
                    turns[2] = True
        if direction == 2 or direction == 3:
            if 12 <= centerx % num2 <=18:
                if level[(centery + num3) // num1][centerx // num2] <3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] <3:
                    turns[2] = True
            if 12 <= centery % num1 <=18:
                if level[centery// num1][(centerx - num2) // num2] <3:
                    turns[1] = True
                if level[centery// num1][(centerx + num2)// num2] <3:
                    turns[0] = True

        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <=18:
                if level[(centery + num1) // num1][centerx // num2] <3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] <3:
                    turns[2] = True
            if 12 <= centery % num1 <=18:
                if level[centery// num1][(centerx - num3) // num2] <3:
                    turns[1] = True
                if level[centery// num1][(centerx + num3)// num2] <3:
                    turns[0] = True


    else:
        turns[0] = True
        turns[1] = True
    return turns

while run:
    timer.tick(fps)
    if counter < 19:
        counter += 1
        if(counter > 3):
            flicker = False
    else:
        counter = 0
        flicker = True
    if(power_up and power_counter < 600):
        power_counter +=1
    elif (power_up and power_counter >= 600):
        power_counter = 0
        power_up = False
        eaten_ghosts = [False, False, False, False]

    if start_up_counter < 180 and not game_over and not game_won:
        moving = False
        start_up_counter +=1
    else:
        moving = True
    if game_paused == True:
        moving = False
    else:
        moving  = True
    screen.fill('black')
    center_X = player_x + 23
    center_Y = player_y + 24
    if power_up:
        ghost_speeds =  [1,1,1,1]
    else:
        ghost_speeds =  [2,2,2,2]
    if eaten_ghosts[0]:
        ghost_speeds[0] = 2
    if eaten_ghosts[1]:
        ghost_speeds[1] = 2
    if eaten_ghosts[2]:
        ghost_speeds[2] = 2
    if eaten_ghosts[3]:
        ghost_speeds[3] = 2
    if blinky_dead:
        ghost_speeds[0] = 4
    if inky_dead:
        ghost_speeds[1] = 4
    if pinky_dead:
        ghost_speeds[2] = 4
    if clyde_dead:
        ghost_speeds[3] = 4
    draw_board(level)
    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i] or -1 in level[i] or -2 in level[i]:
            game_won = False
    player_circle = pygame.draw.circle(screen, 'black', (center_X, center_Y), 20, 2)
    draw_player()

    #instance of all the ghosts:
    #def __int__(self, x, y, target, speed, img, direct, dead, box, id):
    blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speeds[0], blinky_img, blinky_direction, blinky_dead, blinky_box, 0)
    inky = Ghost(inky_x, inky_y, targets[1], ghost_speeds[1], inky_img, inky_direction, inky_dead, inky_box, 1)
    pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speeds[2], pinky_img, pinky_direction, pinky_dead, pinky_box, 2)
    clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speeds[3], clyde_img, clyde_direction, clyde_dead, clyde_box, 3)
    draw_stats()
    targets = get_targets(blinky_x, blinky_y, pinky_x, pinky_y, inky_x, inky_y, clyde_x, clyde_y)
    turns_allowed = check_position(center_X, center_Y)

    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if not blinky_dead and not blinky.in_box:
            blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
        else:
            blinky_x, blinky_y, blinky_direction = blinky.move_clyde()
        if not inky_dead and not inky.in_box:
            inky_x, inky_y, inky_direction = inky.move_inky()
        else:
            inky_x, inky_y, inky_direction = inky.move_clyde()
        if not pinky_dead and not pinky.in_box:
            pinky_x, pinky_y, pinky_direction = pinky.move_inky()
        else:
            pinky_x, pinky_y, pinky_direction = pinky.move_clyde()
        clyde_x, clyde_y, clyde_direction = clyde.move_clyde()

    score, power_up, power_counter, eaten_ghosts = check_collisions(score, power_up, power_counter, eaten_ghosts)
    #COLLISIONS WITH GHOSTS:
    if not power_up:
        if(player_circle.colliderect(blinky.rect) and not blinky.dead) or \
            (player_circle.colliderect(inky.rect)and not inky.dead) or \
            (player_circle.colliderect(pinky.rect) and not pinky.dead) or \
            (player_circle.colliderect(clyde.rect) and not clyde.dead):
            if lives > 0 :
                lives -=1
                start_up_counter = 0
                power_up = False
                player_x, player_y, direction, direction_command = 450, 663, 0, 0
                blinky_x, blinky_y, blinky_direction = 56, 58, 0
                inky_x, inky_y, inky_direction = 440, 388, 2
                pinky_x, pinky_y, pinky_direction = 370, 438, 2
                clyde_x, clyde_y, clyde_direction = 440, 438, 2
                eaten_ghosts = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                pinky_dead = False
                clyde_dead = False
            else:
                #game over tasks:
                game_over =True
                moving = False
                start_up_counter = 0
    if power_up and player_circle.colliderect(blinky.rect) and eaten_ghosts[0] and not blinky.dead:
        if lives > 0:
            lives -= 1
            start_up_counter = 0
            power_up = False
            player_x, player_y, direction, direction_command = 450, 663, 0, 0
            blinky_x, blinky_y, blinky_direction = 56, 58, 0
            inky_x, inky_y, inky_direction = 440, 388, 2
            pinky_x, pinky_y, pinky_direction = 370, 438, 2
            clyde_x, clyde_y, clyde_direction = 440, 438, 2
            eaten_ghosts = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            pinky_dead = False
            clyde_dead = False
        else:
            # game over tasks:
            game_over = True
            moving = False
            start_up_counter = 0
    if power_up and player_circle.colliderect(inky.rect) and eaten_ghosts[1] and not inky.dead:
        if lives > 0:
            lives -= 1
            start_up_counter = 0
            power_up = False
            player_x, player_y, direction, direction_command = 450, 663, 0, 0
            blinky_x, blinky_y, blinky_direction = 56, 58, 0
            inky_x, inky_y, inky_direction = 440, 388, 2
            pinky_x, pinky_y, pinky_direction = 370, 438, 2
            clyde_x, clyde_y, clyde_direction = 440, 438, 2
            eaten_ghosts = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            pinky_dead = False
            clyde_dead = False
        else:
            # game over tasks:
            game_over = True
            moving = False
            start_up_counter = 0
    if power_up and player_circle.colliderect(pinky.rect) and eaten_ghosts[2] and not pinky.dead:
        if lives > 0:
            lives -= 1
            start_up_counter = 0
            power_up = False
            player_x, player_y, direction, direction_command = 450, 663, 0, 0
            blinky_x, blinky_y, blinky_direction = 56, 58, 0
            inky_x, inky_y, inky_direction = 440, 388, 2
            pinky_x, pinky_y, pinky_direction = 370, 438, 2
            clyde_x, clyde_y, clyde_direction = 440, 438, 2
            eaten_ghosts = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            pinky_dead = False
            clyde_dead = False
        else:
            # game over tasks:
            game_over = True
            moving = False
            start_up_counter = 0
    if power_up and player_circle.colliderect(clyde.rect) and eaten_ghosts[3] and not clyde.dead:
        if lives > 0:
            lives -= 1
            start_up_counter = 0
            power_up = False
            player_x, player_y, direction, direction_command = 450, 663, 0, 0
            blinky_x, blinky_y, blinky_direction = 56, 58, 0
            inky_x, inky_y, inky_direction = 440, 388, 2
            pinky_x, pinky_y, pinky_direction = 370, 438, 2
            clyde_x, clyde_y, clyde_direction = 440, 438, 2
            eaten_ghosts = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            pinky_dead = False
            clyde_dead = False
        else:
            # game over tasks:
            game_over = True
            moving = False
            start_up_counter = 0
    if power_up :
        if (player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghosts[0]):
            blinky_dead = True
            eaten_ghosts[0] = True
            score += (2 * eaten_ghosts.count(True)) * 100
        if (player_circle.colliderect(inky.rect) and not inky.dead and not eaten_ghosts[1]):
            inky_dead = True
            eaten_ghosts[1] = True
            score += (2 * eaten_ghosts.count(True)) * 100
        if (player_circle.colliderect(pinky.rect) and not pinky.dead and not eaten_ghosts[2]):
            pinky_dead = True
            eaten_ghosts[2] = True
            score += (2 * eaten_ghosts.count(True)) * 100
        if (player_circle.colliderect(clyde.rect) and not clyde.dead and not eaten_ghosts[3]):
            clyde_dead = True
            eaten_ghosts[3] = True
            score += (2 * eaten_ghosts.count(True)) * 100

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: #Pausing game
                if (game_paused == True): #UNPAUSE
                    game_paused = False
                    #draw_pause_menu
                else: #PAUSE
                    game_paused = True

            if event.key == pygame.K_d or event.key == pygame.K_RIGHT: #handle movement to the right, with 'd' or rigth arrow
                direction_command = 0
            if event.key == pygame.K_a or event.key == pygame.K_LEFT: #handle movement to the left, with 'a' or left arrow
                direction_command = 1
            if event.key == pygame.K_w or event.key == pygame.K_UP: #handle movement upwards, with 'w' or up arrow
                direction_command = 2
            if event.key == pygame.K_s or event.key == pygame.K_DOWN: #handle movement down, with 's' or up down arrow
                direction_command = 3
            if event.key == pygame.K_SPACE and (game_over or game_won):
                start_up_counter = 0
                power_up = False
                player_x, player_y, direction, direction_command = 450, 663, 0, 0
                blinky_x, blinky_y, blinky_direction = 56, 58, 0
                inky_x, inky_y, inky_direction = 440, 388, 2
                pinky_x, pinky_y, pinky_direction = 370, 438, 2
                clyde_x, clyde_y, clyde_direction = 440, 438, 2
                eaten_ghosts = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                pinky_dead = False
                clyde_dead = False
                score = 0
                lives = 3
                level = boards
                game_over, game_won = False, False
        if event.type == pygame.KEYUP:
            if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and direction_command == 0: #handle movement to the right, with 'd' or rigth arrow
                direction_command = direction
            if (event.key == pygame.K_a or event.key == pygame.K_LEFT) and direction_command == 1: #handle movement to the left, with 'a' or left arrow
                direction_command = direction
            if (event.key == pygame.K_w or event.key == pygame.K_UP) and direction_command == 2: #handle movement upwards, with 'w' or up arrow
                direction_command = direction
            if (event.key == pygame.K_s or event.key == pygame.K_DOWN) and direction_command == 3: #handle movement down, with 's' or up down arrow
                direction_command = direction
    for i in range(4):
        if(direction_command == i and turns_allowed[i]):
            direction = i
    if player_x > 900: #tp accross the map in case player gets to edge:
        player_x = -47
    elif player_x < -50:
        player_x = 897

    if blinky.in_box and blinky_dead:
        blinky_dead = False
    if inky.in_box and inky_dead:
        inky_dead = False
    if pinky.in_box and pinky_dead:
        pinky_dead = False
    if clyde.in_box and clyde_dead:
        clyde_dead = False


    pygame.display.flip()
pygame.quit()