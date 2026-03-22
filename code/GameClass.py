import math
from sys import exit

import numpy as np
import pygame
import pygame as pg

from ButtonClass import Button
from PlayerClass import ControllerPlayer, KeyboardPlayer
from bezgenerator import generate_bez
from ScoreManager import ScoreManager

clock = pg.time.Clock()

class Game():

    def __init__(self,window):

        '''This is the constructor for the Game class.
        Here I initialize all the private variables that I use within the game class.
        I instantiate all the 'buttons' such as menu_screen, that will later be
        drawn in their respective game state
        '''

        self.window = window
        self.bg_y = 0
        self.background = pg.transform.scale(pg.image.load('../images/background.png').convert_alpha(), (self.window.get_width(), self.window.get_height()))
        self.start_line = pg.transform.scale(pg.image.load('../images/start_line.png').convert_alpha(), (500, 320))

        # these are the fonts that i will be using in my game,
        # while they are the same font to keep consistency,
        # they have a different size
        self.score_font = pg.font.SysFont("Pixelify Sans", 50)
        self.game_over_font = pg.font.SysFont("Pixelify Sans", 100)

        # I am using a pygame clock so that the game fps stays the same
        # for all computers being used that are powerful enough
        self.clock = pg.time.Clock()

        self.shift_increment = 0.005
        self.start_shift = 3
        self.camera_shift = self.start_shift
        self.score = 0

        self.players = []

        self.winner = ''

        self.difficulty = 100

        self.state = 'MENU'

        self.menu_screen  = Button(0, 0, pg.transform.scale(pg.image.load('../images/menu.png').convert_alpha(), (self.window.get_width(), self.window.get_height())), self.window)
        self.htp_screen = Button(0, 0, pg.transform.scale(pg.image.load('../images/htp.png').convert_alpha(), (self.window.get_width(), self.window.get_height())), self.window)
        self.game_over_screen = Button(0, 0, pg.transform.scale(pg.image.load(
            '../images/game_over.png').convert_alpha(), (self.window.get_width(), self.window.get_height())), self.window)
        self.difficulty_select_screen = Button(0, 0, pg.transform.scale(pg.image.load(
            '../images/difficulty_screen.png').convert_alpha(), (self.window.get_width(), self.window.get_height())), self.window)

        # creates the database manager
        # this means the table is made if it doesn't already exist
        self.db = ScoreManager('game.db')

        self.player_name = ''
        self.finished_user_input = False

        # using a dictionary to easily convert between the
        # difficulty name and the number of total control points i am using
        self.difficulty_converter = {50: 'EASY', 150: 'MEDIUM',  200:'HARD' , 250:'IMPOSSIBLE'}

    def create_game(self):
        '''The create_game method is where the track points
        are generated, the players are instantiated depending
        on what inputs are present'''

        self.all = generate_bez(self.window.get_width(),self.difficulty)

        self.allpoints = self.all[0]
        self.main_points = self.all[2]
        self.controls = self.all[1]

        self.camera_shift = self.start_shift
        self.score = 0

        self.finished_user_input = False

        if pg.joystick.get_count() == 0:
            player_1 = pg.sprite.GroupSingle()
            player_1.add(KeyboardPlayer(self.main_points[0][0], self.main_points[0][1], 1, self.window, self.camera_shift))
            player_2 = pg.sprite.GroupSingle()
            player_2.add(KeyboardPlayer(self.main_points[0][0] - 20, self.main_points[0][1], 2, self.window, self.camera_shift))
        elif pg.joystick.get_count() == 1:
            player_1 = pg.sprite.GroupSingle()
            player_1.add(ControllerPlayer(self.main_points[0][0], self.main_points[0][1], 1, self.window,self.camera_shift))
            player_2 = pg.sprite.GroupSingle()
            player_2.add(KeyboardPlayer(self.main_points[0][0] - 20, self.main_points[0][1], 2, self.window, self.camera_shift))
        else:
            player_2 = pg.sprite.GroupSingle()
            player_2.add(ControllerPlayer(self.main_points[0][0] - 20, self.main_points[0][1], 2 ,self.window,self.camera_shift))

        # I am storing the player objects in a list so that they are
        # grouped together.
        self.players = [player_1, player_2]

    def draw_track(self):

        '''In the draw_track method i use all the
        points generated that lie on the track from the previous
        create_game to then draw the track
        I do this by drawing a 2 circles on each of the points:
        One larger red/white circle and one grey circle above it
        Also I draw the start line if it in the screen view'''


        for i in range(self.difficulty-1):
            for m in range(len(self.allpoints[0])):

                # every 5 points the circle colour changes
                # from red to white
                if m % 10 < 5:
                    pg.draw.circle(self.window, 'red', self.allpoints[i][m], 160)
                else:
                    pg.draw.circle(self.window, 'white', self.allpoints[i][m], 160)

        for i in range(self.difficulty-1):
            for m in range(len(self.allpoints[0])):
                pg.draw.circle(self.window, (30, 30, 30), self.allpoints[i][m], 140)
                self.allpoints[i][m][1] += self.camera_shift  # makes the 'camera' move up

        if (self.allpoints[0][0][1]-300)<self.window.get_height():
            # I am offsetting the coordinates because it is based off the top left of the image no the middle
            self.window.blit(self.start_line, (self.allpoints[0][0][0]-250, self.allpoints[0][0][1]-300))

    def check_if_closed(self):
        # this method checks if the player decided to quit
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                pg.joystick.quit()
                exit()

    def update_all_players(self):

        '''Players movement is updated first (this includes their speed),
          the collision check is done after and then the players are drawn.
          I do 2 separate loops so that the updates for both players are done together
          '''

        for player in self.players:
            player.sprite.update_movement()

        self.collide_players()

        for player in self.players:
            player.sprite.update_shift(self.shift_increment)
            player.sprite.update_draw()
            player.draw(self.window)

    def check_if_game_over(self):
        '''Here I  check if the top of both the cars are below the screen,
        In this case the game is over. If the game is over, it checks which player
        won.'''

        # adding 50 to account for car length
        if self.players[0].sprite.y_float > (self.window.get_height()+50) and self.players[1].sprite.y_float > (self.window.get_height()+50):
            if self.players[0].sprite.y_float>self.players[1].sprite.y_float:
                self.winner = 'PLAYER 2'
            else:
                self.winner = 'PLAYER 1'
            self.player_name = ''
            self.state = 'GAME OVER'

    def collide_players(self):
        '''This method detects whether there is
        a collision between the players.'''

        min_overlap = 121301230123 # large number
        smallest_axis = None
        x1,y1 = self.players[0].sprite.get_centre()
        x2,y2 = self.players[1].sprite.get_centre()


        p1_corners_x,p1_corners_y = self.players[0].sprite.get_corners()
        p2_corners_x, p2_corners_y = self.players[1].sprite.get_corners()

        axis = []

        # This for loop finds both the axis that are parallel to the sides
        # of each car
        for coordinate in range(0,2):
            line1 = [p1_corners_x[coordinate+1]-p1_corners_x[coordinate],p1_corners_y[coordinate+1]-p1_corners_y[coordinate]]
            line2 = [p2_corners_x[coordinate+1] - p2_corners_x[coordinate], p2_corners_y[coordinate+1] - p2_corners_y[coordinate]]

            # I divide each line by its magnitude to give the unit
            # vector for each axis

            l1 = math.sqrt(line1[1]**2+line1[0]**2)
            l2 = math.sqrt(line2[1] ** 2 + line2[0] ** 2)

            axis.append([-line1[1]/l1,line1[0]/l1])
            axis.append([-line2[1]/l2,line2[0]/l2])

        collision = True

        # In this for loop I am finding the projection of
        # the corners of the players car in each axis previously found,
        # Then applying the Separate Axis Theorem
        # to decide whether there isn't a collision

        for projection in axis:
            if collision:
                p1_projection = []
                p2_projection = []
                for i in range(4):
                    p1_projection.append(np.vdot(projection,(p1_corners_x[i],p1_corners_y[i])))
                    p2_projection.append(np.vdot(projection, (p2_corners_x[i], p2_corners_y[i])))

                p1_max = max(p1_projection)
                p1_min = min(p1_projection)
                p2_max = max(p2_projection)
                p2_min = min(p2_projection)

                overlap = min(p1_max,p2_max)-max(p1_min,p2_min)
                if overlap < min_overlap:
                    min_overlap = overlap
                    smallest_axis = projection

                if p1_max<p2_min or p2_max<p1_min:
                    collision = False

        cars_diff = [x2-x1,y2-y1]
        if np.vdot(cars_diff,smallest_axis)<0:
            smallest_axis = [-smallest_axis[0],-smallest_axis[1]]

        # If there is a collision, it calls
        # the collide function for one of the players
        # and passes the output to the other player
        if  collision:
            a,b,c,d = self.players[0].sprite.collide(self.players[1].sprite,smallest_axis,min_overlap)
            self.players[1].sprite.update_velocity(a,b,c,d)

    def play_Loop(self):
        """ In the play loop, I draw the track,
        background and players, I also shift everything
        down because of the camera moving, I also update and
        display the score."""

        self.score += 1

        # The camera shift starts slow and keeps increasing
        # until it is greater than 10
        if self.camera_shift > 10:
            self.shift_increment =  0
        else:
            self.shift_increment = 0.005

        self.camera_shift += self.shift_increment

        self.bg_y += self.camera_shift

        # loops background
        if self.bg_y > self.window.get_height():
            self.bg_y = 0

        self.window.blit(self.background, (0, self.bg_y))
        self.window.blit(self.background, (0, self.bg_y - self.window.get_height()))

        self.score_display = self.score_font.render(f"score: {self.score}", True, (255, 255, 255))


        self.draw_track()
        self.window.blit(self.score_display, (0, 0))
        self.update_all_players()
        pg.display.update()
        self.check_if_game_over()
        self.check_if_closed()

    def game_over(self,keys_pressed):
        """Once both players are eliminated they
        are sent to the game over screen. If the winning
        player beat the high score for that difficulty
        then they are prompted to input their name, and are
        added to the high score database, otherwise the current
        high score holder is displayed. The player can also return
        to the menu from here."""

        self.game_over_screen.draw(self.window)


        game_over_text = self.game_over_font.render(f'{self.score} {self.winner} is the winner!', True, (255, 255, 255))
        high_score = self.db.get_high_score(self.difficulty)

        if (self.score > high_score) and self.finished_user_input == False:
            self.get_user_name()
            input_high_score_text = self.game_over_font.render(f'input your name here : {self.player_name}', True,(255, 255, 255))
            self.window.blit(input_high_score_text,(self.window.get_width() / 2 - 500, self.window.get_height() / 2 + 250))

        else:
            # if they finished inputting their name they are
            # added to the database

            if self.score > high_score:
                high_score = self.score
                self.db.add_new_highscore(self.player_name,self.difficulty,high_score )
            self.player_name = self.db.get_player_name(self.difficulty)
            high_score_text = self.game_over_font.render(f'{self.player_name} holds the high score of {high_score} at difficulty {self.difficulty_converter[self.difficulty]}', True,(255, 255, 255))
            self.window.blit(high_score_text,(0, self.window.get_height() / 2 + 250))


        self.window.blit(game_over_text, (self.window.get_width() / 2 - 500, self.window.get_height() / 2 + 150)) #centering the score text

        self.check_if_closed()
        pg.display.update()


        # if the player presses 'space' or triangle then
        # they return to the menu
        if pg.joystick.get_count() > 0:
            if keys_pressed[pg.K_SPACE] or pg.joystick.Joystick(0).get_button(3):
                self.state = 'MENU'
        elif keys_pressed[pg.K_SPACE]:
            self.state = 'MENU'


    def get_user_name(self):
        """
        This is where the player's name is
        updated in the game over screen.
        """

        self.finished_user_input = False

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:

                # if they click backspace then it deletes
                # last character of name
                if event.key == pg.K_BACKSPACE:
                    self.player_name = self.player_name[0:len(self.player_name)-1]
                # if they press return then it signals
                # that they finished typing
                elif event.key == pg.K_RETURN:
                    self.finished_user_input = True
                # player name has a max of 5 characters
                elif len(self.player_name) < 5:
                    self.player_name += event.unicode


    def menu(self,keys_pressed,prev_keys_pressed):
        '''In the menu, the game decides what state to
        go into next based off of the user input'''

        self.menu_screen.draw(self.window)

        self.check_if_closed()
        pg.display.update()

        if pg.joystick.get_count() > 0:
            if (keys_pressed[pg.K_SPACE] and not prev_keys_pressed[pg.K_SPACE]) or pg.joystick.Joystick(0).get_button(0):
                self.state = 'SELECT'
            elif keys_pressed[pg.K_h] and not prev_keys_pressed[pg.K_h] or pg.joystick.Joystick(0).get_button(1):
                self.state = 'HTP'
        else:
            if (keys_pressed[pg.K_SPACE] and not prev_keys_pressed[pg.K_SPACE]):
                self.state = 'SELECT'
            elif keys_pressed[pg.K_h] and not prev_keys_pressed[pg.K_h]:
                self.state = 'HTP'

    def select_difficulty(self,keys):

        self.check_if_closed()
        pg.display.update()
        self.difficulty_select_screen.draw(self.window)
        if keys[pg.K_1]:
            self.difficulty = 50
            self.create_game()
            self.state = 'PLAY'
        elif keys[pg.K_2]:
            self.difficulty = 150
            self.create_game()
            self.state = 'PLAY'
        elif keys[pg.K_3]:
            self.difficulty = 200
            self.create_game()
            self.state = 'PLAY'
        elif keys[pg.K_4]:
            self.difficulty = 250
            self.create_game()
            self.state = 'PLAY'

    def htp(self,keys_pressed,prev_keys_pressed):
        self.window.fill((0, 0, 0))
        self.htp_screen.draw(self.window)
        self.check_if_closed()
        pg.display.update()
        if pg.joystick.get_count() > 0:
            if (keys_pressed[pg.K_SPACE] and not prev_keys_pressed[pg.K_SPACE]) or pg.joystick.Joystick(0).get_button(3):
                self.state = 'MENU'
        else:
            if (keys_pressed[pg.K_SPACE] and not prev_keys_pressed[pg.K_SPACE]):
                self.state = 'MENU'

    def game_loop(self):
        '''This is the game loop where everything is
        executed depending on the game state'''

        pg.mixer.music.play(-1)

        prev_keys = pg.key.get_pressed()
        while True:
            clock.tick(50)
            keys = pg.key.get_pressed()

            if self.state == 'MENU':
                self.menu(keys,prev_keys)
                # using previous keys as well because when you click space
                # once it counts it multiple frames in a row
                # so prev keys checks if it was false the frame before

            elif self.state == 'PLAY':
                self.play_Loop()

            elif self.state == 'GAME OVER':
                self.game_over(keys)

            elif self.state == 'HTP':
                self.htp(keys,prev_keys)

            elif self.state == 'SELECT':
                self.select_difficulty(keys)


            prev_keys = keys

