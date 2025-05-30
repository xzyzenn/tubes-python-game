# enemy.py

import pygame as pg
from pygame.math import Vector2
import constants as c
import random
from enemy_data import ENEMY_DATA

class Enemy(pg.sprite.Sprite):
    def __init__(self, enemy_type, images):
        pg.sprite.Sprite.__init__(self)
        self.enemy_type = enemy_type

        # Spawn posisi X di paling kanan layar, Y secara acak
        self.pos = Vector2(0 - c.TILE_SIZE, random.randint(0, c.SCREEN_HEIGHT - c.TILE_SIZE))
        self.speed = ENEMY_DATA.get(enemy_type)["speed"]
        self.health = ENEMY_DATA.get(enemy_type)["health"]
        self.max_health = ENEMY_DATA.get(enemy_type)["health"]

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

    def draw_health_bar(self, surface):
        # Hitung rasio HP saat ini
        health_ratio = self.health / self.max_health
        # Tentukan dimensi bar HP
        bar_width = self.rect.width * 0.8
        bar_height = 5
        bar_x = self.rect.centerx - (bar_width / 2)
        bar_y = self.rect.top - bar_height - 5 # Posisikan di atas musuh

        # Gambar background bar (abu-abu gelap)
        pg.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        # Gambar foreground bar (hijau)
        pg.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))