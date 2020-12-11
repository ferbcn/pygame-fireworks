import pygame, sys, time
from pygame.locals import *
import random

colorPals = {"yellows": [(225,220,13), (240,235,0), (255,249,0), (242,238,85), (249,246,92)],
             "greens": [(8,108,2), (71,106,55), (23,179,38), (68,132,90), (16,168,46)],
             "reds": [(255,133,133), (255,71,71), (255,0,0), (227,0,0), (186,0,0)],
             "blues":[(1,31,75), (3,57,108), (0,91,150), (100,151,177), (179,205,224)],
             "white": [(0, 0, 0)]}

WINDOWWIDTH = 800
WINDOWHEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255,255,255)
RED = (255,0,0)



class Fireworks():

    def __init__ (self, window_title="Fireworks", base_count=3, rocket_count=10, explo_count=10, cycle_time=5, auto_explo=True):
        #super ().__init__ ()

        # lists holding objects that will be drawn to screen
        self.rockets = []
        self.explosions = []

        self.start_time = time.time ()
        self.cycle_done = False
        self.all_done = False

        self.anim_run = True

        self.explo_count = explo_count
        self.auto_explode = auto_explo
        self.cycle_time = cycle_time

        self.fps = 20 # default animation speed

        self.next_base_color = "" # buffer that holds a manually selected color
        self.auto_color = True

        self.lowFPS = False

        # Set up pygame.
        pygame.init ()

        # Set up the window.
        self.ws = pygame.display.set_mode ((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
        pygame.display.set_caption (window_title)

        self.clock = pygame.time.Clock ()

        # change mouse pointer
        pygame.mouse.set_cursor (*pygame.cursors.diamond)
        #pygame.mouse.set_visible(False)
        #self.pointerImg = pygame.image.load ('data/aim.png').convert ()
        #self.pointerImg_rect = self.pointerImg.get_rect () #rect for drawing custom mouse pointer

        # run animation
        self.runLoop(base_count, rocket_count)


    def runLoop(self, base_count, rocket_count):

       while not self.all_done:

            #reset the loop flag
            self.cycle_done = False
            self.start_time = time.time ()

            # rockets are initiated in cycles
            # random bases are created in each cycle
            # each base launches rockets with a random palett of colors
            # all rockets from the same base share initial x coordinates, initial delay and base color
            for i in range (base_count):
                init_x_pos = random.randint (50, WINDOWWIDTH - 50)
                delay_ms = random.randint (0, self.cycle_time)
                self.initRockets (init_x_pos, rocket_count, delay_ms)

            self.auto_color = True

            # Run the game/animation loop.
            while not self.cycle_done:

                # check if all rockets have been removed (end of cycle)
                if len (self.rockets) < 1:
                    self.cycle_done = True
                # print(self.rockets)

                # HANDLE EVENTS
                for event in pygame.event.get ():
                    #print(event)
                    if event.type == QUIT:
                        pygame.quit ()
                        sys.exit ()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit ()
                            sys.exit ()

                        if event.key == pygame.K_SPACE: # pause animation
                            if self.anim_run == False:
                                self.anim_run = True
                            else:
                                self.anim_run = False
                        if event.key == pygame.K_KP_PLUS: # increase anim speed
                            if self.fps < 60:
                                self.fps += 1
                        if event.key == pygame.K_KP_MINUS: # decrease anim speed
                            self.fps -= 1
                        # override randomization of rockets colors and set manually
                        if event.key == pygame.K_r: #set base color to red
                            self.next_base_color = "reds"
                            self.auto_color = False
                        if event.key == pygame.K_g:
                            self.next_base_color = "greens"
                            self.auto_color = False
                        if event.key == pygame.K_b:
                            self.next_base_color = "blues"
                            self.auto_color = False
                        if event.key == pygame.K_y:
                            self.next_base_color = "yellows"
                            self.auto_color = False

                        if event.key == pygame.K_a: # toggle fireworks auto explode
                            if self.auto_explode == False:
                                self.auto_explode = True
                            else:
                                self.auto_explode = False
                        if event.key == pygame.K_RETURN: # let all rockets explode
                            for rocket in self.rockets:
                                if rocket.flying:
                                    rocket.life = 0
                                    self.initExplosion (rocket.x_pos, rocket.y_pos, 1, rocket.color,
                                                       self.explo_count * rocket.size)
                                else:
                                    self.rockets.remove (rocket)

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        for rocket in self.rockets:
                            if abs(rocket.x_pos - x) < 10 and abs(rocket.y_pos - y) < 10:
                                self.rockets.remove (rocket)
                                self.initExplosion (rocket.x_pos, rocket.y_pos, 1, rocket.color, self.explo_count*rocket.size)

                # run / pause animation
                if self.anim_run:
                    # Draw background
                    self.ws.fill (BLACK)

                    # Draw objects
                    self.drawRockets ()
                    self.drawExplosions()

                    # Draw the window onto the screen.
                    pygame.display.update ()

                    # move objects
                    self.updateRockets ()
                    self.updateExplosions()

                    # if fps are to low crop more tail elements
                    if self.fps - self.clock.get_fps () > 2:
                        self.lowFPS = True
                    else:
                        self.lowFPS = False

                self.clock.tick (self.fps)


    def initRockets(self, init_x_pos, count, delay_ms): # we initiate all rockets from one base with a random base color
        if self.auto_color:
            base_color = random.choice (list (colorPals.keys ()))
        else:
            base_color = self.next_base_color
        for i in range(count):
            newRocket = Rocket(init_x_pos, delay_ms, base_color)
            self.rockets.append(newRocket)

    def drawRockets(self):
        for rocket in self.rockets:
            # activate rocket when delay is over
            if time.time() > self.start_time + rocket.init_delay:
                rocket.flying = True

            # check if rockets have been activated
            if rocket.flying:
                # Draw objects onto the surface.
                pygame.draw.rect (self.ws, rocket.color,
                                  pygame.Rect (rocket.x_pos, rocket.y_pos, rocket.size, rocket.size))
                rocket.tail_elems.append((rocket.x_pos, rocket.y_pos)) # keep track of path

                # draw the rockets tail
                for element in rocket.tail_elems:
                    pygame.draw.rect (self.ws, rocket.color,
                                      pygame.Rect (element[0], element[1], rocket.size, rocket.size))

    def updateRockets(self):
        for rocket in self.rockets:
            if rocket.flying:
                # check for life and explode if over
                if rocket.life < 1:
                    self.rockets.remove (rocket)
                    if self.auto_explode:
                        self.initExplosion (rocket.x_pos, rocket.y_pos, 1, rocket.color, self.explo_count*rocket.size)
                else:
                    rocket.update_rocket ()


    def initExplosion(self, x, y, s, color, count):
        for i in range(count):
            explosion = Explosion(self, x, y, s, color)
            self.explosions.append(explosion)


    def drawExplosions(self):
        for explosion in self.explosions:
            pygame.draw.rect (self.ws, explosion.color,
                              pygame.Rect (explosion.x_pos, explosion.y_pos, explosion.size, explosion.size))
            explosion.tail_elems.append ((explosion.x_pos, explosion.y_pos))  # keep track of path
            # draw tail
            for element in explosion.tail_elems:
                pygame.draw.rect (self.ws, explosion.color,
                                  pygame.Rect (element[0], element[1], explosion.size, explosion.size))

    def updateExplosions(self):
        for explosion in self.explosions:
            if explosion.life < 1:
                self.explosions.remove (explosion)
            else:
                explosion.update_explosion()


class Explosion():
    def __init__ (self, parent, init_x_pos, init_y_pos, size, color):
        self.parent = parent
        self.color = color
        self.size = size
        self.y_speed = random.randint(-30,20)
        self.x_speed = random.randint(-30,30)
        self.x_pos = init_x_pos
        self.y_pos = init_y_pos
        self.tail_length = 5
        self.life = random.randint(10,20) #determines when a explosion is gonna fade out
        self.tail_elems = []
        self.flying = True

        self.max_tail_elems = 10

    def update_explosion(self):
        self.y_pos += self.y_speed
        self.x_pos += self.x_speed
        self.life -= 1

        # decelerate speeds
        self.x_speed *= 0.9
        if self.y_speed > 0:
            self.y_speed *= 1
        else:
            self.y_speed *= 0.8

        """
        # crop tail elements
        if len(self.tail_elems) > self.tail_length:
            self.tail_elems=self.tail_elems[1:self.max_tail_elems]

        # if fps are to low crop more tail elements
        print(str(int (self.parent.clock.get_fps ())))
        if self.parent.fps - self.parent.clock.get_fps () > 2:
            print("LOW")
        """

class Rocket():
    def __init__ (self, init_x_pos, init_delay, base_color):
        self.color = random.choice (colorPals[base_color])
        self.size = random.randint(1,3)
        self.y_speed = random.randint(30,50)
        self.x_speed = random.randint(-10,10)
        self.x_pos = init_x_pos
        self.y_pos = WINDOWHEIGHT
        self.tail_length = 10
        self.life = random.randint(30, 100) #determines when a rocket is gonna explode
        self.tail_elems = []
        self.flying = False
        self.init_delay = init_delay

    def update_rocket(self):
        self.y_pos -= self.y_speed
        self.x_pos += self.x_speed
        self.life -= 1

        # decelerate speeds
        self.x_speed *= 0.95
        self.y_speed *= 0.9

        # crop tail elements
        if len(self.tail_elems) > self.tail_length:
            self.tail_elems=self.tail_elems[1:10]


if __name__ == "__main__":
    # init fireworks class
    myfire = Fireworks(base_count=5, rocket_count=10, explo_count=20, cycle_time=1, auto_explo=True)
