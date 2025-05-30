# bullet.py
import pygame as pg
from pygame.math import Vector2
import constants as c

class Bullet(pg.sprite.Sprite):
    def __init__(self, image_list, target_enemy, start_pos, damage): # Add damage as a parameter
        pg.sprite.Sprite.__init__(self)
        self.image_list = image_list
        self.target_enemy = target_enemy
        self.pos = Vector2(start_pos)
        self.damage = damage # Store damage
        self.frame_index = 0
        self.animation_timer = pg.time.get_ticks()
        self.animation_speed = 50 # Milliseconds per frame
        self.alive = True

        self.image = self.image_list[self.frame_index]
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        if self.alive:
            # Animate the bullet
            self.animate()

            # Move towards the enemy's head
            if self.target_enemy and self.target_enemy.alive:
                target_head_pos = Vector2(self.target_enemy.rect.centerx, self.target_enemy.rect.top + (self.target_enemy.rect.height * 0.2)) # Approximate head position
                
                # Simple linear movement towards the target
                direction = (target_head_pos - self.pos).normalize()
                self.pos += direction * 10 # Adjust bullet speed as needed
                self.rect.center = self.pos

                # Check if bullet has reached the target
                if (self.pos.distance_to(target_head_pos) < 20): # Closer proximity for impact
                    self.target_enemy.health -= self.damage # Apply damage to the enemy
                    if self.target_enemy.health <= 0: # Check if enemy died from this hit
                        self.target_enemy.alive = False # Set enemy as not alive to trigger dying animation
                        self.target_enemy.dying_animation_start_time = pg.time.get_ticks() # Start dying animation timer
                        self.target_enemy.slashing_turret = None # Stop slashing if dying
                        self.target_enemy.speed = 0 # Stop movement when dying
                    self.alive = False
                    self.kill()
            else:
                self.alive = False # If target is dead or invalid, bullet disappears
                self.kill()

    def animate(self):
        current_time = pg.time.get_ticks()
        if current_time - self.animation_timer > self.animation_speed:
            self.frame_index += 1
            if self.frame_index >= len(self.image_list):
                self.frame_index = 0  # Loop animation
            self.image = self.image_list[self.frame_index]
            self.animation_timer = current_time

    def draw(self, surface):
        if self.alive:
            surface.blit(self.image, self.rect)