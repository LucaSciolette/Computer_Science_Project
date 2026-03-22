import pygame as pg

from GameClass import Game

'''In this file I Instantiate the game
object, initialise pygame joystick , 
create the screen and execute the game
loop'''

pg.init()
pg.joystick.init()

pg.mixer.music.load('../sound/game_sound.mp3')
pg.mixer.music.set_volume(0.01)

w = 1920
h = 980

screen = pg.display.set_mode((w,h))

game = Game(screen)

game.create_game()

game.game_loop()