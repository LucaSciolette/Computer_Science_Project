import math
import numpy as np
import pygame as pg


class Player(pg.sprite.Sprite):
    def __init__(self,start_x,start_y,player_num,screen,shift):
        '''This is the constructor for the Player class
        Here I initialize all the movement variables including
        speed and angular velocity'''

        # Player inherits from the pygame sprite class
        # because it essentially provides me a template to build on
        # Doesn't really serve much of a purpose
        # but was helpful in the beginning of the process
        super().__init__()
        self.angle = 0.0
        self.friction_forward = 0.92
        self.friction_side = 0.8
        self.speed = [0.0,0.0]
        self.accn = 0.7
        self.steer_speed = 0.25

        self.player_num = player_num
        self.shift = shift
        self.angular_velocity = 0
        self.screen = screen

        if player_num == 1:
            self.o_image = pg.transform.scale(pg.image.load('../images/player1.png').convert_alpha(), (56, 94))
        else:
            self.o_image = pg.transform.scale(pg.image.load('../images/player2.png').convert_alpha(), (56, 94))

        self.image = self.o_image
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.o_rect_w = self.rect.width/2.0
        self.o_rect_h = self.rect.height/2.0

        self.x_float = self.rect.centerx
        self.y_float = self.rect.centery

    def drift(self):
        self.friction_side = 0.95

    def update_velocity(self,new_v,x_increment,y_increment,new_angular_v):
        ''' this method is called to the player
        that didn't have the 'collide' method called so that
        they can also have their coordinates and speeds updated
        after a collision'''
        self.speed = new_v
        self.x_float += x_increment
        self.y_float += y_increment
        self.angular_velocity = new_angular_v

    def collide(self,collider,normal,depth):
        '''This method is called to one player during a collision
        It is where calculations are done to find the new speeds, direction
        angular velocity, position of the cars after the collision.'''

        displacement_factor = 1
        padding = 0.01

        # increment is a vector that describes how much both cars
        # need to be displaced so that they no longer overlap
        # increment is parallel to the line of centres between the 2 cars
        increment = [normal[0]*max(depth-padding,0)*displacement_factor/2.0,normal[1]*max(depth-padding,0)*displacement_factor/2.0]
        self.x_float -= increment[0]
        self.y_float -= increment[1]
        collider_x_increment = increment[0]
        collider_y_increment = increment[1]
        collider_speed = collider.get_speed()
        collider_angular_velocity = collider.get_angular_velocity()

        best_dot = float('-inf')

        contact_point = [0,0]

        # This is used to find the contact point,
        # which is the corner of a car that hit the other.
        for p in range(len(collider.get_corners()[0])):
            x = collider.get_corners()[0][p]
            y = collider.get_corners()[1][p]
            dot = np.vdot([-normal[0],-normal[1]],[x,y])
            if dot > best_dot:
                best_dot = dot
                contact_point = [x,y]

        r1 = [contact_point[0]-self.x_float,contact_point[1]-self.y_float]
        r2 = [contact_point[0]-collider.x_float,contact_point[1]-collider.y_float]

        r1_perp = [-r1[1], r1[0]]  # perpendicular to r1
        r2_perp = [-r2[1], r2[0]]  # perpendicular to r2

        w1 = math.radians(self.angular_velocity)  # angular velocity of car1 in radians
        w2 = math.radians(collider.get_angular_velocity())  # angular velocity of car2 in radians

        v1_point = [self.speed[0]+r1_perp[0]*w1,self.speed[1]+r1_perp[1]*w1]
        v2_point = [collider_speed[0]+r2_perp[0]*w2,collider_speed[1]+r2_perp[1]*w2]

        rel_vel = [v2_point[0]-v1_point[0],v2_point[1]-v1_point[1]]

        vel_along_normal = np.dot(normal,rel_vel)

        # this checks if the cars are already moving apart
        # if they are then another 'bounce' doesn't happen
        if vel_along_normal < -0.01:
            return collider_speed,collider_x_increment,collider_y_increment,collider_angular_velocity

        restitution = 2

        r1_cross_n = r1[0] * normal[1] - r1[1] * normal[0]
        r2_cross_n = r2[0] * normal[1] - r2[1] * normal[0]

        inv_mass_sum = 2
        inertia = (64 ** 2 + 32 ** 2) / 36 * 5 # car width and height is 64 and 32
        ang_denom = (r1_cross_n ** 2) / inertia + (r2_cross_n ** 2) / inertia

        j = -(1 + restitution) * vel_along_normal
        j /= (inv_mass_sum + ang_denom)

        impulse = [normal[0] * j, normal[1] * j]

        self.speed = [self.speed[0]-impulse[0],self.speed[1]-impulse[1]]
        collider_speed = [collider_speed[0]+impulse[0],collider_speed[1]+impulse[1]]

        torque1 = r1[0] * impulse[1] - r1[1] * impulse[0]
        torque2 = r2[0] * impulse[1] - r2[1] * impulse[0]

        # when the cars collide they spin like in real life
        self.angular_velocity -= math.degrees(torque1 / inertia)
        collider_angular_velocity += math.degrees(torque2 / inertia)

        return collider_speed,collider_x_increment,collider_y_increment,collider_angular_velocity

    def rotate(self):
        '''This method is used to rotate the car
        when an image is rotated in pygame its dimensions change, so
        the rectangle is re-centered'''
        o_x = self.rect.x
        o_y = self.rect.y
        self.image = pg.transform.rotate(self.o_image, self.angle)
        self.rect.x = o_x- self.image.get_width()//2
        self.rect.y = o_y- self.image.get_height()//2

    def check_surface(self):
        '''Here I check if the player is off the track
        by seeing what the colour of the pixel below the center
        of the car is before drawing it. If the color isn't one of
        the colors I used to make the track, then the car is
        off-road and will slow down
        '''
        if  self.screen.get_width() > self.rect.centerx > 0 and self.screen.get_height() > self.rect.centery > 0 :
            if self.screen.get_at(self.rect.center) not in [(30,30,30),'red','white ']:
                self.friction_forward = 0.88
            else:
                self.friction_forward = 0.96

    def update_coords(self):
        global shift
        self.y_float -= self.speed[0] - self.shift
        self.x_float -= self.speed[1]
        self.rect.y = round(self.y_float,2)
        self.rect.x = round(self.x_float,2)

    def get_corners(self):
        '''This method is used to get the corners of the car
        by using trigonometry since I know the dimensions of the car
        and its angle.'''

        # take into account the padding in the car image,
        # when using width and height
        w = 64
        h = 32
        x,y = self.get_centre()
        theta = self.get_angle()
        corners_x = [x + (w / 2) * math.cos(theta) - (h / 2) * math.sin(theta),
                        x + (w / 2) * math.cos(theta) + (h / 2) * math.sin(theta),
                        x - (w / 2) * math.cos(theta) - (h / 2) * math.sin(theta),
                        x - (w / 2) * math.cos(theta) + (h / 2) * math.sin(theta)]
        corners_y = [y + (w / 2) * math.sin(theta) + (h / 2) * math.cos(theta),
                        y + (w / 2) * math.sin(theta) - (h / 2) * math.cos(theta),
                        y - (w / 2) * math.sin(theta) + (h / 2) * math.cos(theta),
                        y - (w / 2) * math.sin(theta) - (h / 2) * math.cos(theta)]

        return corners_x,corners_y



    def move(self):
        # This is a virtual method that will
        # be overwritten in subclasses
        pass

    '''From now on there are only getter and setters'''

    def get_rect(self):
        return self.rect

    def get_angle(self):
        return (math.radians(-self.angle) + math.pi / 2)  # self.angle isnt actually the angle to the vertical

    def get_speed(self):
        return self.speed

    def get_centre(self):
        return self.x_float, self.y_float

    def update_shift(self, increment):
        self.shift += increment

    def reset_shift(self, num):
        self.shift = num

    def get_angular_velocity(self):
        return self.angular_velocity

    def update_movement(self):
        self.update_coords()
        self.rotate()

    def update_draw(self):
        self.move()
        self.check_surface()


class ControllerPlayer(Player):
    def __init__(self,start_x,start_y,player_num,screen,shift):
        super().__init__(start_x,start_y,player_num,screen,shift)
        self.joystick = pg.joystick.Joystick(self.player_num - 1)

    def move(self):
        '''This is where the player's velocity and
        angular velocity change
        based off of joystick inputs
        '''
        prev_angle = self.angle

        self.speed_m = math.hypot(self.speed[0], self.speed[1])

        self.speed_vect = pg.math.Vector2(self.speed)

        # ff is forward unit vector and fs is side
        # forward being the direction the car is facing
        ff = pg.math.Vector2(1.0,0.0).rotate(self.angle)
        fs = ff.rotate(-90.0)

        # sf and ss are components of velocity in
        # forward and side direction respectively
        sf = ff.dot(self.speed_vect) * self.friction_forward
        ss = fs.dot(self.speed_vect) * self.friction_side

        # turn with joystick but by a smaller amount
        # if the car is moving slow because that is
        # how it works in real life
        if self.speed_m > 1:
            self.angle -= self.joystick.get_axis(0) * 3.5
        else:
            self.angle -= self.joystick.get_axis(0) * self.speed_m

        # accelerates or decelerates the car in
        # forward direction depending on whether
        # left or right trigger is pressed
        if (self.joystick.get_axis(4)>0):
            sf -= self.accn*self.joystick.get_axis(4)/2
        elif (self.joystick.get_axis(5)>0):
            sf += self.accn*self.joystick.get_axis(5)

        # checks is square is pressed so player drifts
        if self.joystick.get_button(2):
            self.drift()
        else:
            self.friction_side = 0.8

        speed_vect = ff*sf+fs*ss

        # sets a limit for max angular velocity so car doesn't spin too much
        self.angular_velocity = min(abs(0.8*self.angular_velocity),3)*np.sign(self.angular_velocity)
        self.angle += self.angular_velocity
        self.angular_velocity = self.angle - prev_angle

        self.speed = [speed_vect.x,speed_vect.y]


class KeyboardPlayer(Player):
    def __init__(self,start_x,start_y,player_num,screen,shift):
        super().__init__(start_x, start_y, player_num, screen, shift)

    def move(self):
        '''same as controller player movement
        but with different inputs'''

        keys = pg.key.get_pressed()
        prev_angle = self.angle

        self.speed_m = math.hypot(self.speed[0], self.speed[1])

        self.speed_vect = pg.math.Vector2(self.speed)
        ff = pg.math.Vector2(1.0,0.0).rotate(self.angle)
        fs = ff.rotate(-90.0)

        sf = ff.dot(self.speed_vect) * self.friction_forward
        ss = fs.dot(self.speed_vect) * self.friction_side

        # player 1 and 2 have different inputs
        # player 1 uses wasd and 2 uses arrow keys
        if self.player_num == 1:
            if self.speed_m > 1:
                if keys[pg.K_a]:
                    self.angle += self.steer_speed * self.speed_m
                elif keys[pg.K_d]:
                    self.angle -= self.steer_speed * self.speed_m
            else:
                if keys[pg.K_a]:
                    self.angle += self.steer_speed
                elif keys[pg.K_d]:
                    self.angle -= self.steer_speed

            if keys[pg.K_w]:
                sf += self.accn
            elif keys[pg.K_s]:
                sf -= self.accn / 2

        elif self.player_num == 2:
            if self.speed_m > 1:
                if keys[pg.K_LEFT]:
                    self.angle += self.steer_speed * self.speed_m
                elif keys[pg.K_RIGHT]:
                    self.angle -= self.steer_speed * self.speed_m
            else:
                if keys[pg.K_LEFT]:
                    self.angle += self.steer_speed
                elif keys[pg.K_RIGHT]:
                    self.angle -= self.steer_speed

            if keys[pg.K_UP]:
                sf += self.accn
            elif keys[pg.K_DOWN]:
                sf -= self.accn / 2
        else:
            self.friction_side = 0.8
        if keys[pg.K_SPACE]:
            self.drift()
        else:
            self.friction_side = 0.8

        speed_vect = ff*sf+fs*ss

        self.angular_velocity = min(abs(0.8*self.angular_velocity),3)*np.sign(self.angular_velocity)
        self.angle += self.angular_velocity
        self.angular_velocity = self.angle - prev_angle

        self.speed = [speed_vect.x,speed_vect.y]

