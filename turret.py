# turret.py
import pygame as pg
import math
import constants as c
from turret_data import TURRET_DATA
from enemy_data import ENEMY_DATA # Keep this import for range calculation, but enemy applies damage

class Turret(pg.sprite.Sprite):
    def __init__(self, sprite_sheets, tile_x, tile_y, shot_fx):
        pg.sprite.Sprite.__init__(self)
        self.upgrade_level = 1
        self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
        self.damage = TURRET_DATA[self.upgrade_level - 1].get("damage")
        self.last_shot = pg.time.get_ticks()
        self.selected = False
        self.target = None
        self.health = 100
        self.max_health = 100

        # Waktu terakhir turret terkena damage, untuk cooldown damage dari enemy
        # Ini akan dihapus karena damage akan dikelola oleh Enemy
        # self.last_damaged = pg.time.get_ticks()
        # self.damage_cooldown = 500 # Turret bisa terkena damage setiap 0.5 detik

        #position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        #calculate center coordinates
        self.x = (self.tile_x + 0.5) * c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE
        #shot sound effect
        self.shot_fx = shot_fx

        #animation variables
        self.sprite_sheets = sprite_sheets
        self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
        self.frame_index = 0
        self.update_time = pg.time.get_ticks()

        #update image
        self.angle = 90
        self.original_image = self.animation_list[self.frame_index]
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.rect.center = (self.x, self.y)

        #create transparent oval showing range
        self.ellipse_width_factor = 2.5
        self.ellipse_height_factor = 1.0 # Reverted to original factor for visual ellipse height
        self.y_offset_oval = 0

        self.ellipse_width = int(self.range * self.ellipse_width_factor)
        self.ellipse_height = int(self.range * self.ellipse_height_factor)

        surface_width = max(self.range * 2, self.ellipse_width + 20)
        surface_height = max(self.range * 2, self.ellipse_height + self.y_offset_oval + 20)

        self.range_image = pg.Surface((surface_width, surface_height))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))

        ellipse_x_center_on_surface = surface_width // 2
        ellipse_y_center_on_surface = surface_height // 2

        ellipse_rect = pg.Rect(ellipse_x_center_on_surface - self.ellipse_width // 2,
                               ellipse_y_center_on_surface - self.ellipse_height // 2,
                               self.ellipse_width, self.ellipse_height)
        pg.draw.ellipse(self.range_image, (255, 0, 0), ellipse_rect)

        self.range_image.set_alpha(20)
        self.range_rect = self.range_image.get_rect()
        # Position the range_rect relative to the turret's center, with an offset
        self.range_rect.center = (self.rect.centerx, self.rect.centery + self.ellipse_height // 3)

        # Define the actual center of the drawn ellipse for attack calculations
        # This aligns the calculation origin with the visual representation, with a downward offset for "feet"
        self.attack_origin_x = self.range_rect.centerx
        self.attack_origin_y = self.range_rect.centery + (self.ellipse_height * 0.2) # Added downward offset


    def load_images(self, sprite_sheet):
        #extract images from spritesheet
        size = sprite_sheet.get_height()
        animation_list = []
        for x in range(c.ANIMATION_STEPS):
            temp_img = sprite_sheet.subsurface(x * size, 0, size, size)
            animation_list.append(temp_img)
        return animation_list

    def update(self, enemy_group, world):
        # Cek HP turret
        if self.health <= 0:
            self.kill() # Hapus turret jika HP <= 0

        #if target picked, play firing animation
        if self.target:
            self.play_animation()
        else:
            #search for new target once turret has cooled down
            if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
                self.pick_target(enemy_group)

        # THE SECTION BELOW IS REMOVED AS ENEMY WILL HANDLE DAMAGE TO TURRET
        # # Periksa musuh yang berada dalam range dan serang turret
        # for enemy in enemy_group:
        #     if enemy.health > 0:
        #         # Calculate relative position of enemy to the *ellipse's center*, using enemy's feet
        #         rel_x = enemy.pos[0] - self.attack_origin_x
        #         rel_y = enemy.rect.bottom - self.attack_origin_y

        #         half_width = self.ellipse_width / 2
        #         half_height = self.ellipse_height / 2

        #         if half_width > 0 and half_height > 0:
        #             # Check if enemy is within the ellipse
        #             if (rel_x / half_width)**2 + (rel_y / half_height)**2 <= 1:
        #                 if pg.time.get_ticks() - self.last_damaged > self.damage_cooldown:
        #                     self.health -= ENEMY_DATA[enemy.enemy_type]["damage"] # Turret menerima damage
        #                     self.last_damaged = pg.time.get_ticks()

    def pick_target(self, enemy_group):
        #find an enemy to target
        #check distance to each enemy to see if it is in range
        for enemy in enemy_group:
            if enemy.health > 0:
                # Calculate relative position of enemy to the *ellipse's center*, using enemy's feet
                rel_x = enemy.pos[0] - self.attack_origin_x
                rel_y = enemy.rect.bottom - self.attack_origin_y

                half_width = self.ellipse_width / 2
                half_height = self.ellipse_height / 2

                if half_width > 0 and half_height > 0:
                    # Check if enemy is within the ellipse
                    if (rel_x / half_width)**2 + (rel_y / half_height)**2 <= 1:
                        self.target = enemy
                        self.angle = math.degrees(math.atan2(-rel_y, rel_x))
                        self.target.health -= self.damage
                        self.shot_fx.play()
                        break

    def play_animation(self):
        #update image
        self.original_image = self.animation_list[self.frame_index]
        #check if enough time has passed since the last update
        if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1
            #check if the animation has finished and reset to idle
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0
                #record completed time and clear target so cooldown can begin
                self.last_shot = pg.time.get_ticks()
                self.target = None

    def upgrade(self):
        self.upgrade_level += 1
        self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
        self.damage = TURRET_DATA[self.upgrade_level - 1].get("damage")
        self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
        self.original_image = self.animation_list[self.frame_index]

        #upgrade range oval
        self.ellipse_width = int(self.range * self.ellipse_width_factor)
        self.ellipse_height = int(self.range * self.ellipse_height_factor)
        self.y_offset_oval = 0

        surface_width = max(self.range * 2, self.ellipse_width + 20)
        surface_height = max(self.range * 2, self.ellipse_height + self.y_offset_oval + 20)

        self.range_image = pg.Surface((surface_width, surface_height))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))

        ellipse_x_center_on_surface = surface_width // 2
        ellipse_y_center_on_surface = surface_height // 2

        ellipse_rect = pg.Rect(ellipse_x_center_on_surface - self.ellipse_width // 2,
                               ellipse_y_center_on_surface - self.ellipse_height // 2,
                               self.ellipse_width, self.ellipse_height)
        pg.draw.ellipse(self.range_image, (255, 0, 0), ellipse_rect)

        self.range_image.set_alpha(20)
        self.range_rect = self.range_image.get_rect()
        # Position the range_rect relative to the turret's center, with an offset
        self.range_rect.center = (self.rect.centerx, self.rect.centery + self.ellipse_height // 3) # Consistent offset

        # Define the actual center of the drawn ellipse for attack calculations
        # This aligns the calculation origin with the visual representation, with a downward offset for "feet"
        self.attack_origin_x = self.range_rect.centerx
        self.attack_origin_y = self.range_rect.centery + (self.ellipse_height * 0.2) # Added downward offset

    def draw(self, surface):
        surface.blit(self.range_image, self.range_rect)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        self.draw_health_bar(surface)

    def draw_range(self, surface):
        if self.selected:
            surface.blit(self.range_image, self.range_rect)

    def draw_health_bar(self, surface):
        # Hitung rasio HP saat ini
        health_ratio = self.health / self.max_health
        # Tentukan dimensi bar HP
        bar_width = self.rect.width * 0.8
        bar_height = 5
        bar_x = self.rect.centerx - (bar_width / 2)
        bar_y = self.rect.top - bar_height - 5 # Posisikan di atas turret

        # Gambar background bar (abu-abu gelap)
        pg.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        # Gambar foreground bar (hijau)
        pg.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))