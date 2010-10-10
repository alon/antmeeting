"""
central place to load any data, does some caching
"""

import os
from math import pi

import pygame

sprites = {}
def get_sprite(filename):
    # all of the sprites are prebuilt for a certain size, we need to change then to the required size
    # proportionally.

    global sprites
    path = filename
    if filename not in sprites:
        if not os.path.exists(path):
            path = os.path.join('images', filename)
        sprites[filename] = pygame.image.load(path) # .convert() - supposed to bring better performance - but makes alpha disappear..
        print "loaded %s from %s" % (sprites[filename], path)
    return sprites[filename]

class Sprite(object):

    def __init__(self, filename, target_width, rotation):
        """ rotation in radians
        target_width in pixels
        """
        self._orig_sprite = self._sprite = get_sprite(filename)
        self._orig_rect = self._rect = self._sprite.get_rect()
        self.set_width(target_width)
        self.rotate(rotation)

    def clone(self, x, y):
        s = Sprite(self.filename, self._rect[0], 0)
        s.set_pos(x, y)
        return s

    def set_pos(self, x, y):
        self._rect.center = x, y

    def set_width(self, target_width):
        center = self._rect.center
        cur_width, cur_height = self._rect.width, self._rect.height
        #if cur_width == target_width:
        #    return
        target_height = cur_height * target_width / cur_width
        target_size = (int(target_width), int(target_height))
        self._sprite = pygame.transform.scale(self._orig_sprite, target_size)
        self._rect = self._sprite.get_rect()
        self._rect.center = center

    def rotate(self, angle):
        #if angle == 0:
        #    return
        angle = angle * 180 / pi
        center = self._rect.center
        self._sprite = pygame.transform.rotate(self._orig_sprite, angle)
        self._rect = self._sprite.get_rect()
        self._rect.center = center


