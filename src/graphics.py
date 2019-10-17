import sdl2
import sdl2.ext

class Gui():
    def __init__(self):
        sdl2.ext.init()
        self.window = sdl2.ext.Window("IPC", size=(1000, 500))
        self.window.show()
        self.renderer =  sdl2.ext.Renderer(window)
        self.factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
        self.ipc = factory.from_image("img/IPC.png")
        self.needle_1 = factory.from_image("img/Pointer.png")
        self.needle_2 = factory.from_image("img/Pointer.png")
        set_gui()
        display_gui()


        def set_gui():
            self.needle_1.x += 115
            self.needle_1.y += 78
            self.needle_2 = factory.from_image("IPC/Pointer.png")
            self.needle_2.x += 545
            self.needle_2.y += 78
            self.needle_1.angle = 160
            self.needle_2.angle = 160

        def display_gui():
            spriterenderer = factory.create_sprite_render_system(window)
            spriterenderer.render(ipc)
            spriterenderer.render(needle_1)
            spriterenderer.render(needle_2)
            processor = sdl2.ext.TestEventProcessor()
            processor.run(window)
            sdl2.ext.quit()


    
