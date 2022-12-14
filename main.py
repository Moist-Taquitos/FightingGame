import time
import random
import pygame
from pygame import mixer
import turtle
import os
from colours import *
from tkinter import *
from tkinter import messagebox

# TODO: More Characters, Win Screen, Start Screen, Character select screen, Battle music!, ...actual sprites, UPLOAD ON STEAM, WOOOOOOORLD DOMINATION!!!!!

# ----- CONSTANTS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
SKY_BLUE = (95, 165, 228)
WIDTH = 1200
HEIGHT = 1000
TITLE = "Fighting Game"
# ----------- SCREEN STUFF
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption(TITLE)


# -------- TEXT
def write_text(text, x, y, font_size):
    font = pygame.font.Font(pygame.font.get_default_font(), font_size)
    text_surface = font.render(text, False, BLACK)
    screen.blit(text_surface, (x, y))


player_1_moves = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f,
                  pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_LSHIFT]

player_2_moves = [pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p, pygame.K_j, pygame.K_k, pygame.K_l,
                  pygame.K_SEMICOLON,
                  pygame.K_m, pygame.K_COMMA, pygame.K_PERIOD, pygame.K_SLASH]
player_list = []

# Sprite groups
all_sprites_group = pygame.sprite.Group()
mr_hitbox_punch_sprites_group = pygame.sprite.Group()
mr_hitbox_kick_sprites_group = pygame.sprite.Group()
player_1_hitbox_group = pygame.sprite.Group()
player_2_hitbox_group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, schmoves):
        super().__init__()
        self.schmoves = schmoves
        """
        0 -> light atk
        1 -> jump
        2 -> heavy atk
        3 -> fireball (special move)
        4 -> move left
        5 -> crouch
        6 -> move right
        7 -> (F key) Super?
        8 -> guard crush (blocked by sitting still)
        9 -> block (Cannot be hit)
        10 -> the c key (Whatever. Taunt?)
        11 -> Run


        """

        self.direction = 0
        self.crouch = False
        self.guarding = False
        self.facing_right = True
        self.attacking_state = False
        self.jump = 0
        self.id = 0
        self.time_since_last_jump = 0
        self.time_since_last_fireball = 0
        self.time_since_last_punch = 0
        self.time_since_last_kick = 0
        self.time_since_last_crouch_punch = 0
        self.time_since_last_crouch_kick = 0
        self.time_since_last_jump_kick = 0
        self.time_since_last_jump_punch = 0
        self.time_since_last_kick = 0
        self.time_since_last_guard_break = 0
        self.image = pygame.Surface([100, 150])
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.change_y = 0
        self.change_x = 0
        self.rect.x, self.rect.y = (WIDTH / 4, HEIGHT / 2)
        self.hp = 420
        self.combo = 0
        self.hitstun = 0
        self.blockstun = 0
        self.guard_broken = 0
        self.hitstunmod = 0

    def update(self):
        pressed = pygame.key.get_pressed()
        # Keeping player in the screen
        # Top and bottom
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        # Left and right
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.x < player_list[not self.id].rect.x:
            self.facing_right = True
        else:
            self.facing_right = False
        self.calc_grav()
        # print(self.change_x)
        if self.rect.y >= HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = HEIGHT - self.rect.height
            self.jump = 0
        if self.hitstun > 0:
            self.hitstun -= 1
            self.calc_hit_grav()
        if self.hitstun < 0:
            self.hitstun = 0
            self.change_x = 0
            self.combo = 0
        if self.blockstun > 0:
            self.blockstun -= 1
            self.calc_hit_grav()
        if self.blockstun < 0:
            self.blockstun = 0
            self.change_x = 0
        if self.guard_broken > 0:
            self.guard_broken -= 1
        if self.guard_broken < 0:
            self.guard_broken = 0
        if pressed[self.schmoves[1]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0:
            self.direction = 1
            if self.time_since_last_jump >= 0.5 * 60:
                if self.jump < 2:
                    self.change_y = -10
                    # self.rect.y -= self.change_y  # moves the self upward
                    self.jump += 1
                    self.time_since_last_jump = 0
        if pressed[self.schmoves[
            5]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.change_y = 5
            self.rect.y += self.change_y
            self.direction = 2
            self.crouch = True
        if not pressed[self.schmoves[
            5]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.crouch = False
        if pressed[self.schmoves[
            4]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.change_x = 5
            self.rect.x -= self.change_x
            self.direction = 3
        if pressed[self.schmoves[
            6]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.change_x = 5
            self.rect.x += self.change_x
            self.direction = 4
        if pressed[self.schmoves[11]] and pressed[self.schmoves[
            6]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.change_x = 10
            self.rect.x += self.change_x
        if pressed[self.schmoves[11]] and pressed[self.schmoves[
            4]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.change_x = 10
            self.rect.x -= self.change_x
        # Moves
        if not pressed[self.schmoves[9]]:
            self.guarding = False
        if pressed[self.schmoves[9]] and self.guard_broken <= 0 and self.hitstun <= 0 and not self.attacking_state:
            block = Block(self.id)
            all_sprites_group.add(block)
            self.guarding = True
        elif pressed[self.schmoves[
            0]] and not self.crouch and not self.jump >= 1 and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_punch >= 0.25 * 60:
                punch = Punch(self.id)
                # print("Punch")
                all_sprites_group.add(punch)
                player_1_hitbox_group.add(punch)
                self.time_since_last_punch = 0
        elif pressed[self.schmoves[
            2]] and not self.crouch and not self.jump >= 1 and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_kick >= 0.5 * 60:
                kick = Kick(self.id)
                all_sprites_group.add(kick)
                player_1_hitbox_group.add(kick)
                self.time_since_last_kick = 0
        elif self.crouch and not self.jump and pressed[
            self.schmoves[0]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_crouch_punch >= 0.2 * 60:
                crouch_punch = Crouch_Punch(self.id)
                all_sprites_group.add(crouch_punch)
                player_1_hitbox_group.add(crouch_punch)
                self.time_since_last_crouch_punch = 0
        elif self.crouch and not self.jump and pressed[
            self.schmoves[2]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_crouch_kick >= 0.5 * 60:
                crouch_kick = Crouch_Kick(self.id)
                all_sprites_group.add(crouch_kick)
                player_1_hitbox_group.add(crouch_kick)
                self.time_since_last_crouch_kick = 0
        elif pressed[self.schmoves[3]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_fireball >= 1.3 * 60:
                fireball = Fireball(self.id)
                all_sprites_group.add(fireball)
                player_1_hitbox_group.add(fireball)
                self.time_since_last_fireball = 0
        elif self.jump >= 1 and pressed[
            self.schmoves[0]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_jump_punch >= 0.2 * 60:
                jump_punch = Jump_Punch(self.id)
                all_sprites_group.add(jump_punch)
                player_1_hitbox_group.add(jump_punch)
                self.time_since_last_jump_punch = 0
        elif self.jump >= 1 and pressed[
            self.schmoves[2]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_jump_kick >= 0.5 * 60:
                jump_kick = Jump_Kick(self.id)
                all_sprites_group.add(jump_kick)
                player_1_hitbox_group.add(jump_kick)
                self.time_since_last_jump_kick = 0
        elif pressed[self.schmoves[8]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_guard_break >= .75 * 60:
                guard_break = Guard_Break(self.id)
                all_sprites_group.add(guard_break)
                player_1_hitbox_group.add(guard_break)
                self.time_since_last_guard_break = 0

        self.rect.y += self.change_y  # remember to actually use self.change_y instead of just setting it
        self.direction = 0
        self.time_since_last_jump += 1
        self.time_since_last_fireball += 1
        self.time_since_last_punch += 1
        self.time_since_last_kick += 1
        self.time_since_last_crouch_punch += 1
        self.time_since_last_crouch_kick += 1
        self.time_since_last_jump_kick += 1
        self.time_since_last_jump_punch += 1
        self.time_since_last_guard_break += 1
        # print(self.time_since_last_jump)

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 0.5
        else:
            self.change_y += 0.34

        # See if we are on the ground.
        if self.rect.y >= HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = HEIGHT - self.rect.height

    def calc_hit_grav(self):
        self.rect.x += self.change_x
        if self.change_x != 0:
            if self.change_x <= 0:
                self.change_x += 1
                if self.change_x >= 0:
                    self.change_x = 0
            else:
                self.change_x -= 1
                if self.change_x <= 0:
                    self.change_x = 0


player = Player(player_1_moves)


class Player_2(pygame.sprite.Sprite):
    def __init__(self, schmoves):
        super().__init__()
        self.schmoves = schmoves
        """
        0 -> light atk
        1 -> jump
        2 -> heavy atk
        3 -> fireball (special move)
        4 -> move left
        5 -> crouch
        6 -> move right
        7 -> (F key) Super?
        8 -> guard crush (blocked by sitting still)
        9 -> block (Cannot be hit)
        10 -> the c key (Whatever. Taunt?)
        11 -> Run
        """
        self.image = pygame.Surface([100, 150])
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.change_y = 0
        self.change_x = 0

        self.direction = 0
        self.crouch = False
        self.guarding = False
        self.facing_right = True
        self.attacking_state = False
        self.jump = 0
        self.id = 1
        self.time_since_last_jump = 0
        self.time_since_last_fireball = 0
        self.time_since_last_punch = 0
        self.time_since_last_kick = 0
        self.time_since_last_crouch_punch = 0
        self.time_since_last_crouch_kick = 0
        self.time_since_last_jump_kick = 0
        self.time_since_last_jump_punch = 0
        self.time_since_last_kick = 0
        self.time_since_last_guard_break = 0
        self.image = pygame.Surface([100, 150])
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.change_y = 0
        self.change_x = 0
        self.rect.x, self.rect.y = (2 * WIDTH / 3, HEIGHT / 2)
        self.hp = 420
        self.combo = 0
        self.hitstun = 0
        self.blockstun = 0
        self.guard_broken = 0
        self.hitstunmod = 0

    def update(self):
        pressed = pygame.key.get_pressed()
        # Keeping player in the screen
        # Top and bottom
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        # Left and right
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.x < player_list[not self.id].rect.x:
            self.facing_right = True
        else:
            self.facing_right = False
        self.calc_grav()
        if self.rect.y >= HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = HEIGHT - self.rect.height
            self.jump = 0
        if self.hitstun > 0:
            self.hitstun -= 1
            self.calc_hit_grav()
        if self.hitstun < 0:
            self.hitstun = 0
            self.change_x = 0
            self.combo = 0
        if self.blockstun > 0:
            self.blockstun -= 1
            self.calc_hit_grav()
        if self.blockstun < 0:
            self.blockstun = 0
            self.change_x = 0
        if self.guard_broken > 0:
            self.guard_broken -= 1
        if self.guard_broken < 0:
            self.guard_broken = 0
        if pressed[self.schmoves[1]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0:
            self.direction = 1
            if self.time_since_last_jump >= 0.5 * 60:
                if self.jump < 2:
                    self.change_y = -10
                    # self.rect.y -= self.change_y  # moves the self upward
                    self.jump += 1
                    self.time_since_last_jump = 0
        if pressed[self.schmoves[
            5]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.change_y = 5
            self.rect.y += self.change_y
            self.direction = 2
            self.crouch = True
        if not pressed[self.schmoves[
            5]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.crouch = False
        if pressed[self.schmoves[
            4]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.change_x = 5
            self.rect.x -= self.change_x
            self.direction = 3
            # print("left")
        if pressed[self.schmoves[
            6]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.change_x = 5
            self.rect.x += self.change_x
            self.direction = 4
        if pressed[self.schmoves[11]] and pressed[self.schmoves[
            4]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.change_x = 10
            self.rect.x -= self.change_x
        if pressed[self.schmoves[11]] and pressed[self.schmoves[
            6]] and not self.guarding and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            self.change_x = 10
            self.rect.x += self.change_x
        # Moves
        if not pressed[self.schmoves[9]]:
            self.guarding = False
        if pressed[self.schmoves[9]] and self.guard_broken <= 0 and self.hitstun <= 0 and not self.attacking_state:
            block = Block(self.id)
            all_sprites_group.add(block)
            self.guarding = True
        elif pressed[self.schmoves[
            0]] and not self.crouch and not self.jump >= 1 and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_punch >= 0.25 * 60:
                punch = Punch(self.id)
                # print("Punch")
                all_sprites_group.add(punch)
                player_2_hitbox_group.add(punch)
                self.time_since_last_punch = 0
        elif pressed[self.schmoves[
            2]] and not self.crouch and not self.jump >= 1 and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_kick >= 0.5 * 60:
                kick = Kick(self.id)
                all_sprites_group.add(kick)
                player_2_hitbox_group.add(kick)
                self.time_since_last_kick = 0
        elif self.crouch and not self.jump and pressed[
            self.schmoves[0]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_crouch_punch >= 0.2 * 60:
                crouch_punch = Crouch_Punch(self.id)
                all_sprites_group.add(crouch_punch)
                player_2_hitbox_group.add(crouch_punch)
                self.time_since_last_crouch_punch = 0
        elif self.crouch and not self.jump and pressed[
            self.schmoves[2]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_crouch_kick >= 0.5 * 60:
                crouch_kick = Crouch_Kick(self.id)
                all_sprites_group.add(crouch_kick)
                player_2_hitbox_group.add(crouch_kick)
                self.time_since_last_crouch_kick = 0
        elif pressed[self.schmoves[3]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_fireball >= 1.3 * 60:
                fireball = Fireball(self.id)
                all_sprites_group.add(fireball)
                player_2_hitbox_group.add(fireball)
                self.time_since_last_fireball = 0
        elif self.jump >= 1 and pressed[
            self.schmoves[0]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_jump_punch >= 0.2 * 60:
                jump_punch = Jump_Punch(self.id)
                all_sprites_group.add(jump_punch)
                player_2_hitbox_group.add(jump_punch)
                self.time_since_last_jump_punch = 0
        elif self.jump >= 1 and pressed[
            self.schmoves[2]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_jump_kick >= 0.5 * 60:
                jump_kick = Jump_Kick(self.id)
                all_sprites_group.add(jump_kick)
                player_2_hitbox_group.add(jump_kick)
                self.time_since_last_jump_kick = 0
        elif pressed[self.schmoves[8]] and self.hitstun <= 0 and self.blockstun <= 0 and not self.attacking_state:
            if self.time_since_last_guard_break >= .75 * 60:
                guard_break = Guard_Break(self.id)
                all_sprites_group.add(guard_break)
                player_2_hitbox_group.add(guard_break)
                self.time_since_last_guard_break = 0

        self.rect.y += self.change_y  # remember to actually use self.change_y instead of just setting it
        self.direction = 0
        self.time_since_last_jump += 1
        self.time_since_last_fireball += 1
        self.time_since_last_punch += 1
        self.time_since_last_kick += 1
        self.time_since_last_crouch_punch += 1
        self.time_since_last_crouch_kick += 1
        self.time_since_last_jump_kick += 1
        self.time_since_last_jump_punch += 1
        self.time_since_last_guard_break += 1

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 0.5
        else:
            self.change_y += 0.34
        # See if we are on the ground.
        if self.rect.y >= HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = HEIGHT - self.rect.height

    def calc_hit_grav(self):
        self.rect.x += self.change_x
        if self.change_x != 0:
            if self.change_x <= 0:
                self.change_x += 1
                if self.change_x >= 0:
                    self.change_x = 0
            else:
                self.change_x -= 1
                if self.change_x <= 0:
                    self.change_x = 0


player_2 = Player_2(player_2_moves)


class Punch(pygame.sprite.Sprite):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.tick = 0
        self.image = pygame.Surface([0, 0])
        self.image.fill(RED1)
        self.rect = self.image.get_rect()

    def update(self):
        self.tick += 1
        if self.tick == 1:
            player_list[self.id].attacking_state = True
        if self.tick == 3:
            self.image = pygame.Surface([50, 50])
            self.image.fill(RED1)
            self.rect = self.image.get_rect()
        if self.tick == 7:
            self.image = pygame.Surface([0, 0])
        if self.tick == 14:
            self.kill()
            player_list[self.id].attacking_state = False
            self.tick = 0

        # print(self.tick)
        if player_list[self.id].facing_right and self.tick <= 7:
            self.rect.x, self.rect.y = (player_list[self.id].rect.right, player.rect.y + 50)
        elif not player_list[self.id].facing_right and self.tick <= 7:
            self.rect.right, self.rect.y = (player_list[self.id].rect.left, player_list[self.id].rect.y + 50)
        else:
            self.rect.x = -500
            self.rect.y = 5000

        # if player.facing_right:
        #     self.rect.x, self.rect.y = (player.rect.right, player.rect.y + 50)
        # else:
        #     self.rect.right, self.rect.y = (player.rect.left, player.rect.y + 50)

    def knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 14 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 2
        player_list[not self.id].hp -= 9

    def knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 14 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 2
        player_list[not self.id].hp -= 9

    def block_knockback_right(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x += 5
        player_list[not self.id].blockstun += 13 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 3

    def block_knockback_left(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x -= 5
        player_list[not self.id].blockstun += 13 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 3

    def counter_knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 24 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 2
        player_list[not self.id].hp -= 10

    def counter_knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 24 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 2
        player_list[not self.id].hp -= 9


class Kick(pygame.sprite.Sprite):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.tick = 0
        self.image = pygame.Surface([0, 0])
        self.image.fill(RED1)
        self.rect = self.image.get_rect()

    def update(self):
        self.tick += 1
        if self.tick == 1:
            player_list[self.id].attacking_state = True
        if self.tick == 7:
            self.image = pygame.Surface([110, 50])
            self.image.fill(RED1)
            self.rect = self.image.get_rect()
        if self.tick == 13:
            self.image = pygame.Surface([0, 0])
        if self.tick == 21:
            self.kill()
            player_list[self.id].attacking_state = False
            self.tick = 0

        # self.rect.x, self.rect.y = (player.rect.x+125, player.rect.y+50)

        # print(self.tick)

        if player_list[self.id].facing_right and self.tick <= 13:
            self.rect.x, self.rect.y = (player_list[self.id].rect.right + 5, player_list[self.id].rect.y + 50)
        elif not player_list[self.id].facing_right and self.tick <= 13:
            self.rect.right, self.rect.y = (player_list[self.id].rect.left - 5, player_list[self.id].rect.y + 50)
        else:
            self.rect.x = -500
            self.rect.y = 5000

    def knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 21 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 5
        player_list[not self.id].change_y -= 4
        player_list[not self.id].hp -= 12

    def knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 21 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 5
        player_list[not self.id].change_y -= 4
        player_list[not self.id].hp -= 9

    def block_knockback_right(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x += 7
        player_list[not self.id].blockstun += 17 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 6

    def block_knockback_left(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x -= 7
        player_list[not self.id].blockstun += 17 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 6

    def counter_knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 30 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 3
        player_list[not self.id].change_y -= 6
        player_list[not self.id].hp -= 13

    def counter_knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 30 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 3
        player_list[not self.id].change_y -= 6
        player_list[not self.id].hp -= 13


class Crouch_Punch(pygame.sprite.Sprite):
    def __init__(self, id):
        super().__init__()
        self.tick = 0
        self.id = id
        self.image = pygame.Surface([0, 0])
        self.image.fill(RED1)
        self.rect = self.image.get_rect()

    def update(self):
        self.tick += 1
        if self.tick == 1:
            player_list[self.id].attacking_state = True
        if self.tick == 5:
            self.image = pygame.Surface([80, 25])
            self.image.fill(RED1)
            self.rect = self.image.get_rect()
        if self.tick == 9:
            self.image = pygame.Surface([0, 0])
        if self.tick == 14:
            self.kill()
            player_list[self.id].attacking_state = False
            self.tick = 0

        # self.rect.x, self.rect.y = (player.rect.x + 80, player.rect.y+100)

        if player_list[self.id].facing_right and self.tick <= 9:
            self.rect.x, self.rect.y = (player_list[self.id].rect.right, player_list[self.id].rect.y + 100)
        elif not player_list[self.id].facing_right and self.tick <= 9:
            self.rect.right, self.rect.y = (player_list[self.id].rect.left, player_list[self.id].rect.y + 100)
        else:
            self.rect.x = -500
            self.rect.y = 5000

    def knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 14 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 3
        player_list[not self.id].hp -= 10

    def knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 14 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 3
        player_list[not self.id].hp -= 10

    def block_knockback_right(self):
        player_list[self.id].change_x += player_list[self.id].change_x
        player_list[self.id].change_x += 5
        player_list[not self.id].blockstun += 12 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 4

    def block_knockback_left(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x -= 5
        player_list[not self.id].blockstun += 12 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 4

    def counter_knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 25 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 3
        player_list[not self.id].hp -= 10

    def counter_knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 25 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 3
        player_list[not self.id].hp -= 10


class Crouch_Kick(pygame.sprite.Sprite):
    def __init__(self, id):
        super().__init__()
        self.tick = 0
        self.id = id
        self.image = pygame.Surface([0, 0])
        self.rect = self.image.get_rect()

    def update(self):
        self.tick += 1
        if self.tick == 1:
            player_list[self.id].attacking_state = True
        if self.tick == 17:
            self.image = pygame.Surface([100, 100])
            self.image.fill(RED1)
            self.rect = self.image.get_rect()
        if self.tick == 25:
            self.image = pygame.Surface([0, 0])
            # self.rect.x = -500
            # self.rect.y = 5000
        if self.tick == 75:
            self.kill()
            player_list[self.id].attacking_state = False
            self.tick = 0

        # self.rect.x, self.rect.y = (player.rect.x + 80, player.rect.y - 75)

        if player_list[self.id].facing_right and self.tick <= 25:
            self.rect.x, self.rect.y = (player_list[self.id].rect.right - 10, player_list[self.id].rect.y - 65)
        elif not player_list[self.id].facing_right and self.tick <= 25:
            self.rect.right, self.rect.y = (player_list[self.id].rect.left + 10, player_list[self.id].rect.y - 65)
        else:
            self.rect.x = -500
            self.rect.y = 5000

    def knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 45 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 5
        player_list[not self.id].change_y -= 10
        player_list[not self.id].hp -= 28

    def knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 45 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 5
        player_list[not self.id].change_y -= 10
        player_list[not self.id].hp -= 28

    def block_knockback_right(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x += 20
        player_list[not self.id].blockstun += 40 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 6

    def block_knockback_left(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x -= 20
        player_list[not self.id].blockstun += 40 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 6

    def counter_knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 100 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 3
        player_list[not self.id].change_y -= 10
        player_list[not self.id].hp -= 30

    def counter_knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 100 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 3
        player_list[not self.id].change_y -= 10
        player_list[not self.id].hp -= 30


class Jump_Punch(pygame.sprite.Sprite):
    def __init__(self, id):
        super().__init__()
        self.tick = 0
        self.id = id
        self.image = pygame.Surface([0, 0])
        self.rect = self.image.get_rect()

    def update(self):
        self.tick += 1
        if self.tick == 1:
            player_list[self.id].attacking_state = True
        if self.tick == 6:
            self.image = pygame.Surface([80, 50])
            self.image.fill(RED1)
            self.rect = self.image.get_rect()
        if self.tick == 12:
            self.image = pygame.Surface([0, 0])
        if self.tick == 17:
            self.kill()
            player_list[self.id].attacking_state = False
            self.tick = 0
        # self.rect.x, self.rect.y = (player.rect.x + 100, player.rect.y + 60)

        if player_list[self.id].facing_right and self.tick <= 12:
            self.rect.x, self.rect.y = (player_list[self.id].rect.right, player_list[self.id].rect.y + 50)
        elif not player_list[self.id].facing_right and self.tick <= 12:
            self.rect.right, self.rect.y = (player_list[self.id].rect.left, player_list[self.id].rect.y + 50)
        else:
            self.rect.x = -500
            self.rect.y = 5000

    def knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 15 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 5
        player_list[not self.id].change_y -= 5
        player_list[not self.id].hp -= 11

    def knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 15 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 5
        player_list[not self.id].change_y -= 5
        player_list[not self.id].hp -= 11

    def block_knockback_right(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x += 5
        player_list[not self.id].blockstun += 15 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 6

    def block_knockback_left(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x -= 5
        player_list[not self.id].blockstun += 15 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 6

    def counter_knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 27 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 3
        player_list[not self.id].change_y -= 4
        player_list[not self.id].hp -= 12

    def counter_knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 27 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 3
        player_list[not self.id].change_y -= 4
        player_list[not self.id].hp -= 12


class Jump_Kick(pygame.sprite.Sprite):
    def __init__(self, id):
        super().__init__()
        self.tick = 0
        self.id = id
        self.image = pygame.Surface([0, 0])
        self.rect = self.image.get_rect()

    def update(self):
        self.tick += 1
        if self.tick == 1:
            player_list[self.id].attacking_state = True
        if self.tick == 13:
            self.image = pygame.Surface([100, 100])
            self.image.fill(RED1)
            self.rect = self.image.get_rect()
        if self.tick == 21:
            self.image = pygame.Surface([0, 0])
        if self.tick == 30:
            self.kill()
            player_list[self.id].attacking_state = False
            self.tick = 0
        # self.rect.x, self.rect.y = (player.rect.x + 25, player.rect.y + 83)

        if player_list[self.id].facing_right and self.tick <= 21:
            self.rect.x, self.rect.y = (player_list[self.id].rect.right - 25, player_list[self.id].rect.y + 83)
        elif not player_list[self.id].facing_right and self.tick <= 21:
            self.rect.right, self.rect.y = (player_list[self.id].rect.left + 25, player_list[self.id].rect.y + 83)
        else:
            self.rect.x = -500
            self.rect.y = 5000

    def knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 35 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 20
        player_list[not self.id].change_y += 30
        player_list[not self.id].hp -= 27

    def knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 35 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 20
        player_list[not self.id].change_y += 30
        player_list[not self.id].hp -= 27

    def block_knockback_right(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x += 20
        player_list[not self.id].blockstun += 21 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 15

    def block_knockback_left(self):
        player_list[self.id].rect.x += player_list[self.id].change_x
        player_list[self.id].change_x -= 20
        player_list[not self.id].blockstun += 21 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 15

    def counter_knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 80 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 15
        player_list[not self.id].change_y += 60
        player_list[not self.id].hp -= 30

    def counter_knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 80 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 15
        player_list[not self.id].change_y += 60
        player_list[not self.id].hp -= 30


class Fireball(pygame.sprite.Sprite):
    def __init__(self, id):
        super().__init__()
        self.tick = 0
        self.id = id
        self.change_x = 0
        self.image = pygame.Surface([50, 50])
        self.image.fill(RED1)
        self.rect = self.image.get_rect()
        # self.rect.x, self.rect.y = (player.rect.x + 50, player.rect.y + 20)

        if player_list[self.id].facing_right:
            self.rect.x, self.rect.y = (player_list[self.id].rect.right - 10, player_list[self.id].rect.y + 20)
        else:
            self.rect.right, self.rect.y = (player_list[self.id].rect.left + 10, player_list[self.id].rect.y + 20)

    def update(self):
        self.rect.x += self.change_x
        self.tick += 1
        if player_list[self.id].facing_right:
            self.change_x += 3
        else:
            self.change_x -= 3
        if self.tick == 50:
            self.kill()
            self.tick = 0
            self.change_x = 0

    def knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 10 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 5
        player_list[not self.id].change_y -= 10
        player_list[not self.id].hp -= 15

    def knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 10 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 5
        player_list[not self.id].change_y -= 10
        player_list[not self.id].hp -= 15

    def block_knockback_right(self):
        player_list[not self.id].blockstun += 3 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 2
        player_list[not self.id].hp -= 3

    def block_knockback_left(self):
        player_list[not self.id].blockstun += 3 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 2
        player_list[not self.id].hp -= 3

    def counter_knockback_left(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 25 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 3
        player_list[not self.id].change_y -= 10
        player_list[not self.id].hp -= 15

    def counter_knockback_right(self):
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 25 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 3
        player_list[not self.id].change_y -= 10
        player_list[not self.id].hp -= 15


class Guard_Break(pygame.sprite.Sprite):
    def __init__(self, id):
        super().__init__()
        self.tick = 0
        self.id = id
        self.image = pygame.Surface([0, 0])
        self.rect = self.image.get_rect()

    def update(self):
        self.tick += 1
        if self.tick == 1:
            player_list[self.id].attacking_state = True
        if self.tick == 10:
            self.image = pygame.Surface([75, 75])
            self.image.fill(CYAN)
            self.rect = self.image.get_rect()
        if self.tick == 12:
            self.image = pygame.Surface([0, 0])
        if self.tick == 30:
            self.kill()
            player_list[self.id].attacking_state = False
            self.tick = 0
        # self.rect.x, self.rect.y = (player_list[self.id].rect.x + 80, player_list[self.id].rect.y + 50)

        if player_list[self.id].facing_right and self.tick <= 12:
            self.rect.x, self.rect.y = (player_list[self.id].rect.right, player_list[self.id].rect.y + 50)
        elif not player_list[self.id].facing_right and self.tick <= 12:
            self.rect.right, self.rect.y = (player_list[self.id].rect.left, player_list[self.id].rect.y + 50)
        else:
            self.rect.x = -500
            self.rect.y = 5000

    def block_knockback_left(self):
        player_list[not self.id].guard_broken += 30
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 30 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 0
        player_list[not self.id].change_y -= 10
        player_list[not self.id].hp -= 20

    def block_knockback_right(self):
        player_list[not self.id].guard_broken += 30
        player_list[self.id].combo += 1
        player_list[not self.id].hitstun += 30 - player_list[self.id].hitstunmod
        player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 0
        player_list[not self.id].change_y -= 10
        player_list[not self.id].hp -= 20

    def knockback_right(self):
        player_list[not self.id].blockstun += 0 - player_list[self.id].hitstunmod
        # player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x -= 0

    def knockback_left(self):
        player_list[not self.id].blockstun += 0 - player_list[self.id].hitstunmod
        # player_list[not self.id].rect.x += player_list[not self.id].change_x
        player_list[not self.id].change_x += 0


class Block(pygame.sprite.Sprite):
    def __init__(self, id):
        super().__init__()
        self.tick = 0
        self.id = id
        self.image = pygame.Surface([0, 0])
        self.rect = self.image.get_rect()

    def update(self):
        self.tick += 1
        if self.tick == 1:
            self.image = pygame.Surface([100, 150])
            self.image.fill(CYAN)
            self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = (player_list[self.id].rect.x, player_list[self.id].rect.y)
        if self.tick == 2:
            self.kill()
            self.tick = 0


def draw_health_bar(id, x, y, ):
    health_bar_width = 50
    health_bar_length = 500
    health_bar_border = pygame.Rect(x, y, health_bar_length, health_bar_width)
    pygame.draw.rect(screen, BLACK, health_bar_border)
    health_bar_inside = pygame.Rect(x + 5, y + 5, health_bar_length - 10, health_bar_width - 10)
    pygame.draw.rect(screen, WHITE, health_bar_inside)
    proportion = player_list[id].hp / 420
    the_length_of_the_health_bar_coloured_in = (health_bar_length - 10) * proportion
    health_bar_the_actual_health_bar = pygame.Rect(x + 5, y + 5, the_length_of_the_health_bar_coloured_in,
                                                   health_bar_width - 10)
    pygame.draw.rect(screen, CYAN, health_bar_the_actual_health_bar)


def main():
    pygame.init()

    # ----- SCREEN PROPERTIES

    """
    0 -> light atk
    1 -> jump
    2 -> heavy atk
    3 -> move left
    4 -> crouch and/or fast fall
    5 -> move right
    6 -> super?
    7 -> guard crush (pseudo grab. I'm not programming a goddamn grab.)
    8 -> block (Cannot be hit unless guard crushed)
    9 -> the letter c, used for some miscellaneous purpose I am unsure of.
    10 -> the run button
    11 -> special move (fireball)


    """

    all_sprites_group.add(player)
    all_sprites_group.add(player_2)
    player_list.append(player)
    player_list.append(player_2)
    # all_sprites_group.add(punch)
    # all_sprites_group.add(kick)
    # all_sprites_group.add(crouch_punch)
    # all_sprites_group.add(crouch_kick)
    # all_sprites_group.add(fireball)
    # ----- LOCAL VARIABLES
    done = False

    clock = pygame.time.Clock()

    # ----- MAIN LOOP
    while not done:

        if len(player_1_hitbox_group) == 0:
            player.attacking_state = False
        else:
            player.attacking_state = True
        if len(player_2_hitbox_group) == 0:
            player_2.attacking_state = False
        else:
            player_2.attacking_state = True
        # print (player.attacking_state)
        # -- Event Handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        pressed = pygame.key.get_pressed()
        if player.hp <= 0:
            print("Player 2 wins!")
            quit()
        if player_2.hp <= 0:
            print("Player 1 wins!")
            quit()
        # ----- LOGIC

        things_that_hit_player_2 = pygame.sprite.spritecollide(player_2, player_1_hitbox_group, True)
        for hitbox in things_that_hit_player_2:
            if player_2.rect.x < player.rect.x:
                if player_2.guarding == True:
                    hitbox.block_knockback_right()
                else:
                    if player_2.attacking_state == True:
                        hitbox.counter_knockback_right()
                        print("COUNTER!")
                    else:
                        hitbox.knockback_right()
            else:
                if player_2.guarding == True:
                    hitbox.block_knockback_left()
                else:
                    if player_2.attacking_state == True:
                        hitbox.counter_knockback_left()
                        print("COUNTER!")
                    else:
                        hitbox.knockback_left()

        things_that_hit_player_1 = pygame.sprite.spritecollide(player, player_2_hitbox_group, True)
        for hitbox in things_that_hit_player_1:
            if player.rect.x < player_2.rect.x:
                if player.guarding == True:
                    hitbox.block_knockback_right()
                else:
                    if player.attacking_state == True:
                        hitbox.counter_knockback_right()
                        print("COUNTER!")
                    else:
                        hitbox.knockback_right()
            else:
                if player.guarding == True:
                    hitbox.block_knockback_left()
                else:
                    if player.attacking_state == True:
                        hitbox.counter_knockback_left()
                        print("COUNTER!")
                    else:
                        hitbox.knockback_left()

        # print(len(things_that_hit_player_2))

        all_sprites_group.update()
        # player.update(pressed)

        # ----- RENDER
        screen.fill(WHITE)
        all_sprites_group.draw(screen)
        draw_health_bar(0, 50, 25)
        draw_health_bar(1, 650, 25)

        # ----- UPDATE DISPLAY
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()