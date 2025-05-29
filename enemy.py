# enemy.py

import pygame as pg
from pygame.math import Vector2
import constants as c
import random
from enemy_data import ENEMY_DATA

class Enemy(pg.sprite.Sprite):
    def __init__(self, enemy_type, images):
        pg.sprite.Sprite.__init__(self)

        # Spawn posisi X di paling kanan layar, Y secara acak
        self.pos = Vector2(0 - c.TILE_SIZE, random.randint(0, c.SCREEN_HEIGHT - c.TILE_SIZE))
        self.speed = ENEMY_DATA.get(enemy_type)["speed"]
        self.health = ENEMY_DATA.get(enemy_type)["health"]

        self.images = images.get(enemy_type)
        self.frame_index = 0
        self.animation_counter = 0
        self.original_image = self.images[self.frame_index]
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def update(self, world):
        self.animate()
        self.move(world)
        self.check_alive(world)

    def animate(self):
        self.animation_counter += 0.15
        if self.animation_counter >= len(self.images):
            self.animation_counter = 0
        self.frame_index = int(self.animation_counter)
        self.original_image = self.images[self.frame_index]
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def move(self, world):
        self.pos.x += self.speed * world.game_speed
        self.rect.center = self.pos

        # Jika keluar dari layar sebelah kanan
        if self.pos.x - self.rect.width > c.SCREEN_WIDTH:
            self.kill()
            world.health -= 1
            world.missed_enemies += 1

    def check_alive(self, world):
        if self.health <= 0:
            world.killed_enemies += 1
            world.money += c.KILL_REWARD
            self.kill()
