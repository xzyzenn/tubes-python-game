import pygame as pg
from pygame.math import Vector2
import math

class Enemy(pg.sprite.Sprite):
  def __init__(self, waypoints, image):
    pg.sprite.Sprite.__init__(self)
    self.waypoints = waypoints
    self.pos = Vector2(self.waypoints[0])
    self.target_waypoints = 1
    self.speed = 2
    self.angle = 0
    self.original_image = image
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos

  def update(self):
    self.move()
    self.rotate()

  def move(self):
    #mendefenisikan target waypoint
    if self.target_waypoints < len(self.waypoints):
      self.target = Vector2(self.waypoints[self.target_waypoints])
      self.movement = self.target - self.pos
    else:
      #musuh telah mencapai akhir waypoint
      self.kill()

    #kalkulasi jarak ke target
    dist = self.movement.length()
    #cek kalau jarak sisa lebih besar daripada kecepatan musuh
    if dist >= self.speed:
      self.pos += self.movement.normalize() * self.speed
    else:
      if dist != 0:
        self.pos += self.movement.normalize() * dist
      self.target_waypoints += 1

  def rotate(self):
    #kalkulasi jarak ke next waypoints
    dist = self.target - self.pos
    #kalkulasi sudut menggunakan jarak
    self.angle = math.atan2(-dist[1], dist[0])
    #rotate image dan update persegi
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos