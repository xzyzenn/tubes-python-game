import pygame as pg
from enemy import Enemy
import constants as c

#insialisasi pygame
pg.init()

#buat waktu
clock = pg.time.Clock()

#buat game window
screen = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
pg.display.set_caption ("Tower Defense")

#menyimpan gambar
enemy_image = pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha()

#buat grup
enemy_group = pg.sprite.Group()

waypoints = [
  (100, 100),
  (400, 200),
  (400, 100),
  (200, 300),
]

enemy = Enemy(waypoints, enemy_image)
enemy_group.add(enemy)

#game loop
run = True
while run:
  
  clock.tick(c.FPS)

  screen.fill("grey100")

  #gambar jalur enemy
  pg.draw.lines(screen, "grey0", False, waypoints)

  #update grup
  enemy_group.update()

  #gambar grup
  enemy_group.draw(screen)

  #event handler
  for event in pg.event.get():
    #keluar program
    if event.type == pg.QUIT:
      run = False

  #update display
  pg.display.flip()

pg.quit()