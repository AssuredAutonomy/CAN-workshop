import pygame
import random
from pygame.locals import *
WHITE = (255, 255, 255)

class _Steering_Wheel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.og_image = pygame.image.load("img/steering_wheel2.png")
        except pygame.error as message:
            print('Cannot load graphics')
            raise SystemExit(message)

        self.image = self.og_image
        self.rect = self.image.get_rect()
        self.rect.center = (500,480)
        self.angle = 0

    def update(self):
        self.image = pygame.transform.rotate(self.og_image, self.angle)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.

class _Turn_R_Needle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.og_image = pygame.image.load("img/turnSig_R.png")
        except pygame.error as message:
            print('Cannot load graphics')
            raise SystemExit(message)

        self.image = self.og_image
        self.rect = self.image.get_rect()
        self.rect.center = (567,115)
        self.state = 0

class _Turn_L_Needle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.og_image = pygame.image.load("img/turnSig_L.png")
        except pygame.error as message:
            print('Cannot load graphics')
            raise SystemExit(message)

        self.image = self.og_image
        self.rect = self.image.get_rect()
        self.rect.center = (450,115)
        self.state = 0

class _Speed_Needle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.og_image = pygame.image.load("img/Pointer.png")
            self.og_image = pygame.transform.scale(self.og_image,(300,300))
        except pygame.error as message:
            print('Cannot load graphics')
            raise SystemExit(message)

        self.image = self.og_image
        self.rect = self.image.get_rect()
        self.rect.center = (724,208)
        self.angle = 0

    def update(self):
        self.image = pygame.transform.rotate(self.og_image, self.angle)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.

class _Tac_Needle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.og_image = pygame.image.load("img/Pointer.png")
            self.og_image = pygame.transform.scale(self.og_image,(300,300))
        except pygame.error as message:
            print('Cannot load graphics')
            raise SystemExit(message)

        self.image = self.og_image
        self.rect = self.image.get_rect()
        self.rect.center = (295,208)
        self.angle = 0

    def update(self):
        self.image = pygame.transform.rotate(self.og_image, self.angle)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.

class _MIL(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.og_image = pygame.image.load("img/MIL.png")
        except pygame.error as message:
            print('Cannot load graphics')
            raise SystemExit(message)

        self.image = self.og_image
        self.rect = self.image.get_rect()
        self.rect.center = (510,200)
        self.state = 0


class Gui(object):
    def __init__(self):
        white = (255, 255, 255)
        pygame.init()
        self.size = self.weight, self.height = 1000, 600
        self._display_surf = pygame.display.set_mode(self.size)
        self._display_surf.fill(white)
        self._running = True

        try:
            self.steering_wheel=_Steering_Wheel()
            self.speed_needle = _Speed_Needle()
            self.tac_needle = _Tac_Needle()

            self.block_list = pygame.sprite.Group()
            self.block_list.add(self.steering_wheel)
            self.block_list.add(self.speed_needle)
            self.block_list.add(self.tac_needle)

            self.right_turn_signal = _Turn_R_Needle()
            self.left_turn_signal = _Turn_L_Needle()
            self.mil = _MIL()

            self.og_ipc = pygame.image.load("img/IPC_2.png")

        except pygame.error as message:
            print('Cannot load graphics')
            raise SystemExit(message)

    def turn_on_mil(self,state):
        self.mil.state = state

    def rotate_tac_needle(self, angle):
        self.tac_needle.angle = 200-angle

    def rotate_speed_needle(self, angle):
        self.speed_needle.angle = 200-angle

    def rotate_steering_wheel(self, angle):
        self.steering_wheel.angle = 360-angle

    def turnSig_state(self,state):
        if state == 0:
            self.left_turn_signal.state = 0
            self.right_turn_signal.state = 0
        elif state == 1:
            self.left_turn_signal.state = 1
            self.right_turn_signal.state = 0
        elif state == 2:
            self.left_turn_signal.state = 0
            self.right_turn_signal.state = 1

    def on_loop(self):

        self.block_list.update()

    def on_render(self):

        self._display_surf.fill(WHITE)
        self._display_surf.blit(self.og_ipc,(0,-50))

        if self.left_turn_signal.state == 1:
            self._display_surf.blit(self.left_turn_signal.image,self.left_turn_signal.rect)

        if self.right_turn_signal.state == 1:
            self._display_surf.blit(self.right_turn_signal.image,self.right_turn_signal.rect)

        if self.mil.state == 1:
            self._display_surf.blit(self.mil.image,self.mil.rect)

        self.block_list.draw(self._display_surf)
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):

        self.on_loop()
        self.on_render()
