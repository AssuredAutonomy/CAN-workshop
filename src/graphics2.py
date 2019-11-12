import pygame
from pygame.locals import *

class Gui(object):
    def __init__(self):
        white = (255, 255, 255)
        pygame.init()
        self.size = self.weight, self.height = 1000, 600
        self._display_surf = pygame.display.set_mode(self.size)
        self._display_surf.fill(white)
        self._running = True

        self.og_ipc = pygame.image.load("img/IPC_2.png")
        self.og_tac_needle = pygame.image.load("img/Pointer.png")
        self.og_speed_needle = pygame.image.load("img/Pointer.png")
        self.og_turnSig_L = pygame.image.load("img/turnSig_L.png")
        self.og_turnSig_R = pygame.image.load("img/turnSig_R.png")
        self.og_steering_wheel = pygame.image.load("img/steering_wheel2.png")

        self.steering_wheel = self.og_steering_wheel
        self.steering_rect = self.steering_wheel.get_rect()
        self.steering_rect.center = (500,480)
        self.steering_angle = 90

        self.og_speed_needle = pygame.transform.scale(self.og_speed_needle,(300,300))
        self.speed_needle = self.og_speed_needle
        self.speed_rect = self.speed_needle.get_rect()
        self.speed_rect.center = (723,210)
        self.speed_angle = 0

        self.og_tac_needle = pygame.transform.scale(self.og_tac_needle,(300,300))
        self.tac_needle = self.og_tac_needle
        self.tac_rect = self.tac_needle.get_rect()
        self.tac_rect.center = (293,208)
        self.tac_angle = 180


        self._display_surf.blit(self.og_ipc,(0,-50))

    def rotate_tac_needle(self, angle):
        self.tac_angle = angle

    def rotate_speed_needle(self, angle):
        self.speed_angle = angle

    def rotate_steering_wheel(self, angle):
        self.steering_angle = angle

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.tac_needle = pygame.transform.rotate(self.og_tac_needle, self.tac_angle)
        x,y = self.tac_rect.center
        self.tac_rect = self.tac_needle.get_rect()
        self.tac_rect.center = (x,y)

        self.speed_needle = pygame.transform.rotate(self.og_speed_needle, self.speed_angle)
        x,y = self.speed_rect.center
        self.speed_rect = self.speed_needle.get_rect()
        self.speed_rect.center = (x,y)

        self.steering_wheel = pygame.transform.rotate(self.og_steering_wheel, self.steering_angle)
        x,y = self.steering_rect.center
        self.steering_rect = self.steering_wheel.get_rect()
        self.steering_rect.center = (x,y)

    def on_render(self):
        self._display_surf.blit(self.tac_needle,self.tac_rect)
        self._display_surf.blit(self.speed_needle,self.speed_rect)
        self._display_surf.blit(self.steering_wheel,self.steering_rect)
        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):

        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

if __name__ == "__main__" :
    theApp = Gui()
    theApp.on_execute()

