import sdl2
import sdl2.ext

class Gui():
    def __init__(self):
        sdl2.ext.init()
        self.window = sdl2.ext.Window("IPC", size=(1000, 500))
        self.window.show()
        self.world = sdl2.ext.World()
        self.renderer =  sdl2.ext.Renderer(self.window)
        self.factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=self.renderer)
        self.ipc = self.factory.from_image("img/IPC.png")
        self.tac_needle = self.factory.from_image("img/Pointer.png")
        self.speed_needle = self.factory.from_image("img/Pointer.png")

        def set_gui():
            self.tac_needle.x = 115
            self.tac_needle.y = 78
            self.speed_needle.x = 545
            self.speed_needle.y = 78
            self.tac_needle.angle = 160
            self.speed_needle.angle = 160
            self.spriterenderer = self.factory.create_sprite_render_system(self.window)
            self.world.add_system(self.spriterenderer)
            self.tec_ent = needleEntity(self.world, self.tac_needle, self.tac_needle.angle)

        def display_gui():
            self.spriterenderer.render(self.ipc)
            self.spriterenderer.render(self.tac_needle)
            self.spriterenderer.render(self.speed_needle)
            #processor = sdl2.ext.TestEventProcessor()
            #processor.run(self.window)
            #sdl2.ext.quit()

        set_gui()
        display_gui()
        # To the image is rendered at 0 degrees/2pi wrt to speedometer/tachometer
        # the root angle is the 0 poisiton on the dials, to apply rotation
        # wrt to the dials, calculate the offset angle and add it to the root angle
        self.root_needle_angle = self.tac_needle.angle

    def refresh_gui(self):
        self.spriterenderer.process(self.world, [self.ipc, self.tac_needle, self.speed_needle])

    def rotate_tac_needle(self, angle):
        self.tac_needle.angle = self.root_needle_angle + angle
    
    def rotate_speed_needle(self, angle):
        self.speed_needle.angle = self.root_needle_angle + angle

class needleEntity(sdl2.ext.Entity):
    def __init__(self, world, sprite, angle):
        self.sprite = sprite
        self.angle = angle