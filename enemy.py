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
        self.attack_cooldown = ENEMY_DATA.get(enemy_type)["attack_cooldown"] # New: enemy's attack cooldown
        self.last_attack = pg.time.get_ticks() # New: last time enemy attacked

        self.images = images.get(enemy_type)
        self.animation_type = "walking" # New: current animation state
        self.frame_index = 0
        self.animation_counter = 0
        # Dynamically set the initial image based on the current animation_type
        self.original_image = self.images[self.animation_type][self.frame_index]
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.alive = True # New: flag to track if enemy is alive
        self.dying_animation_start_time = 0 # New: to track dying animation duration
        self.slashing_turret = None # New: stores the turret being slashed

    def update(self, world, turret_group):
        if self.alive:
            self.check_for_turret_collision(turret_group)
            if self.slashing_turret and self.slashing_turret.health > 0: # Only slash if turret is alive
                self.animation_type = "slashing"
                self.animate(0.15) # Slashing animation speed
                
                # Apply damage to turret only if attack cooldown is met
                if pg.time.get_ticks() - self.last_attack > self.attack_cooldown: # New condition
                    self.slashing_turret.health -= ENEMY_DATA[self.enemy_type]["damage"] # Turret menerima damage
                    self.last_attack = pg.time.get_ticks() # Reset cooldown
            else:
                self.animation_type = "walking"
                self.animate(0.15) # Walking animation speed
                self.move(world)
            self.check_alive(world)
        elif self.animation_type == "dying":
            self.animate(0.1) # Dying animation speed
            if pg.time.get_ticks() - self.dying_animation_start_time > 2000: # 2-second delay
                self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def animate(self, speed_factor):
        current_images = self.images[self.animation_type]
        self.animation_counter += speed_factor
        if self.animation_counter >= len(current_images):
            if self.animation_type == "dying":
                # Hold on the last frame of dying animation
                self.frame_index = len(current_images) - 1
            else:
                self.animation_counter = 0
                self.frame_index = 0 # Reset frame index for continuous animations
        else:
            self.frame_index = int(self.animation_counter)
        
        self.original_image = current_images[self.frame_index]
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
        if self.health <= 0 and self.alive: # Only transition to dying once
            self.alive = False
            self.animation_type = "dying"
            self.frame_index = 0
            self.animation_counter = 0
            self.dying_animation_start_time = pg.time.get_ticks()
            world.killed_enemies += 1
            world.money += c.KILL_REWARD
            self.speed = 0 # Stop movement when dying
            self.slashing_turret = None # Stop slashing if dying

    def check_for_turret_collision(self, turret_group):
        # Only check for collision if the enemy is walking and alive
        if self.alive and self.animation_type == "walking": 
            colliding_turret = None
            # Calculate the enemy's current tile coordinates
            enemy_tile_x = int(self.pos.x // c.TILE_SIZE)
            enemy_tile_y = int(self.pos.y // c.TILE_SIZE)

            for turret in turret_group:
                # Check if the enemy's current tile matches the turret's tile
                if enemy_tile_x == turret.tile_x and enemy_tile_y == turret.tile_y:
                    colliding_turret = turret
                    break # Found a colliding turret on the same tile

            if colliding_turret and colliding_turret.health > 0:
                self.slashing_turret = colliding_turret
                self.speed = 0 # Stop moving to slash
            else:
                self.slashing_turret = None
                self.speed = ENEMY_DATA.get(self.enemy_type)["speed"] # Resume normal speed

    def draw_health_bar(self, surface):
        if self.alive: # Only draw health bar if still alive
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