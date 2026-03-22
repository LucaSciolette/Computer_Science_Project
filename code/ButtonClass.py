import pygame as pg


class Button:
    ''' This class is used to abstract some of the
    pygame commands and make the code easier for me to
    change'''

    def __init__(self, x, y, image, surface):

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
