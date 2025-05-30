# main.py
import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
from bullet import Bullet # Import the new Bullet class
from button import Button
import constants as c

#initialise pygame
pg.init()

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

#game variables
game_over = False
game_outcome = 0# -1 is loss & 1 is win
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None

#load images
#map
map_image = pg.image.load('levels/level.png').convert_alpha()
#turret spritesheets
turret_spritesheets = []
for level_num in range(1, c.TURRET_LEVELS + 1): # Loop untuk setiap level turret (1, 2, 3)
    level_frames = []
    for frame_num in range(1, c.TURRET_FRAMES + 1): # Loop untuk setiap frame (1 sampai 9)
        # Konstruksi jalur file yang benar: assets/images/turrets/turret_X/t_Y (Y).png
        img_path = f'assets/images/turrets/turret_{level_num}/t_1 ({frame_num}).png'
        try:
            img = pg.image.load(img_path).convert_alpha()
            level_frames.append(img)
        except pg.error as e:
            print(f"Error loading image {img_path}: {e}")
    if level_frames: # Hanya tambahkan jika frame berhasil dimuat
        turret_spritesheets.append(level_frames)
    else:
        print(f"Warning: No frames loaded for turret level {level_num}. Check image paths.")

#individual turret image for mouse cursor
# Ambil frame pertama dari turret level 1 sebagai gambar kursor
cursor_turret = None
if turret_spritesheets and turret_spritesheets[0]:
    cursor_turret = turret_spritesheets[0][0] # Ambil frame pertama dari turret level 1
else:
    # Fallback jika tidak ada gambar turret yang dimuat
    print("Warning: Could not load cursor_turret image. Check turret image paths.")
    cursor_turret = pg.Surface((c.TILE_SIZE, c.TILE_SIZE), pg.SRCALPHA) # Buat permukaan kosong
    pg.draw.rect(cursor_turret, (255, 255, 0), cursor_turret.get_rect(), 2) # Gambar persegi panjang kuning sebagai placeholder
#enemies
enemy_images = {
  "weak": { "walking": [], "dying": [], "slashing": [] },
  "medium": { "walking": [], "dying": [], "slashing": [] },
  "strong": { "walking": [], "dying": [], "slashing": [] }
}

# Define a helper function to load animations for each enemy type
def load_enemy_animations(enemy_type_key, folder_prefix, num_walking_frames, num_dying_frames, num_slashing_frames):
    # Determine the numerical prefix for the image files
    file_prefix_num = ""
    if enemy_type_key == "weak":
        file_prefix_num = "1"
    elif enemy_type_key == "medium":
        file_prefix_num = "2"
    elif enemy_type_key == "strong":
        file_prefix_num = "3"

    for i in range(num_walking_frames):
        img = pg.image.load(f'assets/images/enemies/{folder_prefix}/Walking/{file_prefix_num}_Zombie_Villager_Walking_{i}.png').convert_alpha()
        enemy_images[enemy_type_key]["walking"].append(img)
    for i in range(num_dying_frames):
        img = pg.image.load(f'assets/images/enemies/{folder_prefix}/Dying/{file_prefix_num}_Zombie_Villager_Dying_{i}.png').convert_alpha()
        enemy_images[enemy_type_key]["dying"].append(img)
    for i in range(num_slashing_frames):
        img = pg.image.load(f'assets/images/enemies/{folder_prefix}/Slashing/{file_prefix_num}_Zombie_Villager_Slashing_{i}.png').convert_alpha()
        enemy_images[enemy_type_key]["slashing"].append(img)

# Load animations for each enemy type with their specific frame counts
# YOU MUST CHANGE THESE TO YOUR ACTUAL FRAME COUNTS IF THEY ARE DIFFERENT
load_enemy_animations("weak", "enemy_1", 24, 10, 8)
load_enemy_animations("medium", "enemy_2", 24, 12, 10)
load_enemy_animations("strong", "enemy_3", 24, 15, 12)


#buttons
buy_turret_image = pg.image.load('assets/images/buttons/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
upgrade_turret_image = pg.image.load('assets/images/buttons/upgrade_turret.png').convert_alpha()
begin_image = pg.image.load('assets/images/buttons/begin.png').convert_alpha()
restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
fast_forward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
#gui
heart_image = pg.image.load("assets/images/gui/heart.png").convert_alpha()
coin_image = pg.image.load("assets/images/gui/coin.png").convert_alpha()
logo_image = pg.image.load("assets/images/gui/logo.png").convert_alpha()

#load sounds
shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(0.5)

#load json data for level
with open('levels/level.tmj') as file:
  world_data = json.load(file)

#load fonts for displaying text on the screen
text_font = pg.font.SysFont("Consolas", 24, bold = True)
large_font = pg.font.SysFont("Consolas", 36)

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def display_data():
  #draw panel
  pg.draw.rect(screen, "maroon", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
  pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
  screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
  #display data
  draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.SCREEN_WIDTH + 10, 10)
  screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
  draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH + 50, 40)
  screen.blit(coin_image, (c.SCREEN_WIDTH + 10, 65))
  draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH + 50, 70)
  

def create_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  # Periksa apakah posisi mouse berada dalam batas layar game area
  if mouse_tile_x < 0 or mouse_tile_x >= c.COLS or mouse_tile_y < 0 or mouse_tile_y >= c.ROWS:
    return False
  if True:
    #check that there isn't already a turret there
    space_is_free = True
    for turret in turret_group:
      if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
        space_is_free = False
        break
      if mouse_tile_y == turret.tile_y:
        if abs(mouse_tile_x - turret.tile_x) <= 1:
          space_is_free = False
          break

    if space_is_free == True:
      new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
      turret_group.add(new_turret)
      #deduct cost of turret
      world.money -= c.BUY_COST
      return True
  return False

def select_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  for turret in turret_group:
    if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
      return turret

def clear_selection():
  for turret in turret_group:
    turret.selected = False

#create world
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()
bullet_group = pg.sprite.Group() # New: Bullet group

# Add bullet_group to the world object for easier access
world.bullet_group = bullet_group

#create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 300, begin_image, True)
restart_button = Button(310, 300, restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH + 50, 300, fast_forward_image, False)

#game loop
run = True
while run:

  clock.tick(c.FPS)

  #########################
  # UPDATING SECTION
  #########################

  if game_over == False:
    #check if player has lost
    if world.health <= 0:
      game_over = True
      game_outcome = -1 #loss
    #check if player has won
    if world.level > c.TOTAL_LEVELS:
      game_over = True
      game_outcome = 1 #win

    #update groups
    enemy_group.update(world, turret_group)
    turret_group.update(enemy_group, world) # Pass world to turret update
    bullet_group.update() # Update bullets

    #highlight selected turret
    if selected_turret:
      selected_turret.selected = True

  #########################
  # DRAWING SECTION
  #########################

  #draw level
  world.draw(screen)

  # Create a combined list of sprites for drawing order
  # This ensures enemies are drawn over the map, turrets over enemies (if applicable), and bullets over everything
  all_sprites_for_drawing = sorted(list(enemy_group) + list(turret_group), key=lambda sprite: sprite.rect.bottom)

  for sprite in all_sprites_for_drawing:
      if isinstance(sprite, Turret):
          sprite.draw(screen)
      elif isinstance(sprite, Enemy):
          sprite.draw(screen)
          sprite.draw_health_bar(screen)
  
  # Draw bullets on top of other game elements
  bullet_group.draw(screen) # Draw bullets


  # Draw turret ranges (only if selected) - this should be on top of everything else except UI
  for turret in turret_group:
      turret.draw_range(screen)

  display_data()

  if game_over == False:
    #check if the level has been started or not
    if level_started == False:
      if begin_button.draw(screen):
        level_started = True
    else:
      #fast forward option
      world.game_speed = 1
      if fast_forward_button.draw(screen):
        world.game_speed = 2
      #spawn enemies
      if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
        if world.spawned_enemies < len(world.enemy_list):
          enemy_type = world.enemy_list[world.spawned_enemies]
          enemy = Enemy(enemy_type, enemy_images)
          enemy_group.add(enemy)
          world.spawned_enemies += 1
          last_enemy_spawn = pg.time.get_ticks()

    #check if the wave is finished
    if world.check_level_complete() == True:
      world.money += c.LEVEL_COMPLETE_REWARD
      world.level += 1
      level_started = False
      last_enemy_spawn = pg.time.get_ticks()
      world.reset_level()
      world.process_enemies()

    #draw buttons
    #button for placing turrets
    #for the "turret button" show cost of turret and draw the button
    draw_text(str(c.BUY_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 135)
    screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
    if turret_button.draw(screen):
      placing_turrets = True
    #if placing turrets then show the cancel button as well
    if placing_turrets == True:
      #show cursor turret
      cursor_rect = cursor_turret.get_rect()
      cursor_pos = pg.mouse.get_pos()
      cursor_rect.center = cursor_pos
      if cursor_pos[0] <= c.SCREEN_WIDTH:
        screen.blit(cursor_turret, cursor_rect)
      if cancel_button.draw(screen):
        placing_turrets = False
    #if a turret is selected then show the upgrade button
    if selected_turret:
      #if a turret can be upgraded then show the upgrade button
      if selected_turret.upgrade_level < c.TURRET_LEVELS:
        #show cost of upgrade and draw the button
        draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
        if upgrade_button.draw(screen):
          if world.money >= c.UPGRADE_COST:
            selected_turret.upgrade()
            world.money -= c.UPGRADE_COST
  else:
    pg.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius = 30)
    if game_outcome == -1:
      draw_text("GAME OVER", large_font, "grey0", 310, 230)
    elif game_outcome == 1:
      draw_text("YOU WIN!", large_font, "grey0", 315, 230)
    #restart level
    if restart_button.draw(screen):
      game_over = False
      level_started = False
      placing_turrets = False
      selected_turret = None
      last_enemy_spawn = pg.time.get_ticks()
      world = World(world_data, map_image)
      world.process_data()
      world.process_enemies()
      #empty groups
      enemy_group.empty()
      turret_group.empty()
      bullet_group.empty() # Clear bullets on restart

  #event handler
  for event in pg.event.get():
    #quit program
    if event.type == pg.QUIT:
      run = False
    #mouse click
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
      mouse_pos = pg.mouse.get_pos()
      #check if mouse is on the game area
      if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
        #clear selected turrets
        selected_turret = None
        clear_selection()
        if placing_turrets == True:
          #check if there is enough money for a turret
          if world.money >= c.BUY_COST:
            create_turret(mouse_pos)
        else:
          selected_turret = select_turret(mouse_pos)

  #update display
  pg.display.flip()

pg.quit()