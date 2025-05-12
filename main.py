import pygame as pg
import constants as c

#insialisasi pygame
pg.init()

#buat waktu
clock = pg.time.Clock()

#buat game window
screen = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
pg.display.set_caption ("Tower Defense")

#game loop
run = True
while run:
  
  clock.tick(c.FPS)

  #event handler
  for event in pg.event.get():
    #keluar program
    if event.type == pg.QUIT:
      run = False

pg.quit()