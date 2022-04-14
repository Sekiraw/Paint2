import cv2
import numpy as np
import os
import pygame
import sys

# main state-ből indulunk ahonnan választhatunk, hogy betöltött képpel indulunk, vagy egy üres sheet-el
# nyilak és space segítségével navigálhatunk itt

# A menü navigációk kb ugyan úgy vannak mint a feladat kiírásban
# 1-2 új billentyűkombó kivételével

# a fancység kedvéért pygame-el csináltam egy menüt neki amit a nyilak segítségével
# lehet navigálni és a space-el
# valószínűleg importálni kell a pygame-et

# a kommentjeimet angolul írom, mert ezt szoktam meg és nagyon zavar,
# hogy minden magyar szót aláhúz

###########################################################

# controls
# line 310 def input_loop
# új kontrollok

# ',' vagy '?' gomb, plusz jelre állítja a rajz-toolt

# nyilak, csak a pygame windowra kattintva működik, a menü navigálásához kell
# space, a menüben a választott helyen végrehajtja az ottani akcióját, pl színnél, lép egy színt

# j gomb, kikapcsolja a crosshairt

# p gomb, megnyit egy ablakot ahova a borderes képet rajzolja majd elmenti, ezután ajánlott újraindítani a programot
# a border színe és mérete a rajztool színe és mérete szerint van meghatározva

# kilépésnél csinál egy utolsó mentést, mert miért ne

class Beadando:
    def __init__(self):
        # pygame
        pygame.init()
        self.screen = pygame.display.set_mode((350, 300))
        self.UI_FONT = 'font/joystix.ttf'
        self.UI_FONT_SIZE = 18
        self.TEXT_COLOR = '#FFFFFF'
        self.font = pygame.font.Font(self.UI_FONT, self.UI_FONT_SIZE)
        self.background_image = pygame.image.load('paint/bg.jpg')
        self.screen.blit(self.background_image, (0, 0))
        pygame.display.set_caption('Tool window')

        # cv2
        self.image = np.zeros((480, 640, 3), np.uint8)
        self.image_width = self.image.shape[1]
        self.image_height = self.image.shape[0]
        self.image.fill(255)

        # base elements
        self.current_former_x = 0
        self.current_former_y = 0
        self.size = 5
        self.color = (0, 0, 255)

        self.drawing = False
        self.mode = True

        # setters for the tools
        self.set_line = True
        self.set_circle = False
        self.set_plus = False
        self.tool_index = 0

        # sets the current draw tool for the ui
        self.current_object = 'Line'

        # ui elements
        self.ui_index = 0
        self.index_x = 0
        self.index_y = 0
        self.set_cursor()

        self.can_move = True
        self.selection_time = None
        self.color_index = 0

        self.color_list = [(0, 0, 255), (255, 0, 0), (0, 0, 0), (255, 255, 255), (0, 255, 0)]

        # crosshair
        self.crosshair_enabled = False
        self.crosshair_color = self.color_list[self.color_index]

        self.pre = self.image.copy()
        self.cross = self.image.copy()

        # starting state
        self.state = 'main_menu'

        self.border_drawn = False

    # base components

    # sets the cursor for it's default position, because I use the same cursor index in both states
    def set_cursor(self):
        self.index_x = 10
        self.index_y = 20

    # pygame draw
    def draw_text(self, text, x, y, color):
        # converter between RGB and BGR for pygame
        if color == (0, 0, 255):
            color = (255, 0, 0)
        elif color == (255, 0, 0):
            color = (0, 0, 255)

        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

        # idk it throws syntax on match

    # cooldown for swapping the menu options
    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 200:
                self.can_move = True

    def state_manager(self):
        self.set_cursor()
        self.ui_index = 0

        if self.state == 'main_menu':
            self.main_menu()
        elif self.state == 'paint':
            self.paint()

    def run(self):
        self.state_manager()

    # / base components

    # paint state components
    def paint(self):
        cv2.namedWindow("Paint2")
        cv2.setMouseCallback('Paint2', self.paint_draw)
        self.input_loop()

        cv2.destroyAllWindows()

    def paint_draw(self, event, former_x, former_y, flags, param):
        # setting the base positions for drawing on click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.current_former_x = former_x
            self.current_former_y = former_y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                if self.mode:
                    if self.set_line:
                        cv2.line(self.image, (self.current_former_x, self.current_former_y), (former_x, former_y),
                                 self.color, self.size)
                    if self.set_circle:
                        # size equals to radius
                        cv2.circle(self.image, (self.current_former_x, self.current_former_y), self.size,
                                   self.color, self.size)
                    if self.set_plus:
                        cv2.line(self.image, (self.current_former_x, self.current_former_y), (former_x, former_y),
                                 self.color, self.size)
                        cv2.line(self.image, (self.current_former_x + self.size, self.current_former_y), (former_x, former_y),
                                 self.color, self.size)
                        cv2.line(self.image, (self.current_former_x, self.current_former_y + self.size), (former_x, former_y),
                                 self.color, self.size)
                        cv2.line(self.image, (self.current_former_x - self.size, self.current_former_y), (former_x, former_y),
                                 self.color, self.size)
                    self.current_former_x = former_x
                    self.current_former_y = former_y
            else:
                self.current_former_x = former_x
                self.current_former_y = former_y

                # cv2.imshow('Paint2', self.pre)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            if self.mode:
                if self.set_line:
                    cv2.line(self.image, (self.current_former_x, self.current_former_y), (former_x, former_y),
                             self.color,
                             5)
                # size equals to radius
                if self.set_circle:
                    cv2.circle(self.image, (self.current_former_x, self.current_former_y), self.size,
                               self.color, self.size)
                if self.set_plus:
                    cv2.line(self.image, (self.current_former_x + self.size, self.current_former_y), (former_x, former_y),
                             self.color, self.size)
                    cv2.line(self.image, (self.current_former_x, self.current_former_y + self.size),
                             (former_x, former_y),
                             self.color, self.size)
                    cv2.line(self.image, (self.current_former_x - self.size, self.current_former_y),
                             (former_x, former_y),
                             self.color, self.size)
                    cv2.line(self.image, (self.current_former_x, self.current_former_y - self.size),
                             (former_x, former_y),
                             self.color, self.size)
                self.current_former_x = former_x
                self.current_former_y = former_y

        self.preview_x_crosshair()

        return former_x, former_y

    # crosshair
    def preview_x_crosshair(self):
        former_x = self.current_former_x
        former_y = self.current_former_y

        # for grey picture
        if len(self.image.shape) < 3:
            self.crosshair_color = Grey

        # I'm a bit color blind, I think this is yellow
        self.crosshair_color = (0, 150, 150)

        if not self.drawing:
            self.pre = self.image.copy()
            # size equals to radius
            if self.set_line:
                cv2.line(self.pre, (former_x, former_y), (former_x, former_y),
                         self.color, self.size)
            if self.set_circle:
                # size equals to radius
                cv2.circle(self.pre, (former_x, former_y), self.size,
                           self.color, self.size)
            if self.set_plus:
                cv2.line(self.pre, (former_x, former_y), (former_x, former_y),
                         self.color, self.size)
                cv2.line(self.pre, (former_x + self.size, former_y), (former_x, former_y),
                         self.color, self.size)
                cv2.line(self.pre, (former_x, former_y + self.size), (former_x, former_y),
                         self.color, self.size)
                cv2.line(self.pre, (former_x - self.size, former_y), (former_x, former_y),
                         self.color, self.size)
            if self.crosshair_enabled:
                cv2.line(self.pre, (former_x, 0), (former_x, self.image_height),
                         self.crosshair_color, 1)
                cv2.line(self.pre, (0, former_y), (self.image_width, former_y),
                         self.crosshair_color, 1)
            cv2.imshow('Paint2', self.pre)
        elif self.drawing:
            self.cross = self.image.copy()
            if self.crosshair_enabled:
                cv2.line(self.cross, (0, former_y), (self.image_width, former_y),
                         self.crosshair_color, 1)
                cv2.line(self.cross, (former_x, 0), (former_x, self.image_height),
                         self.crosshair_color, 1)
            cv2.imshow('Paint2', self.cross)

    # border draw function
    def draw_border(self):
        row, col = self.image.shape[:2]
        bottom = self.image[row - 2:row, 0:col]
        mean = self.color
        bordersize = self.size

        border = cv2.copyMakeBorder(
            self.image,
            top=bordersize,
            bottom=bordersize,
            left=bordersize,
            right=bordersize,
            borderType=cv2.BORDER_CONSTANT,
            value=[mean[0], mean[1], mean[2]]
        )

        cv2.imshow('Bordered image', border)
        cv2.imwrite("paint/image_bordered.png", border)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def tool_indexer(self, index):
        if index == 0:
            self.set_line = True
            self.set_circle = False
            self.set_plus = False
            self.current_object = 'Line'

        # sets the drawing tool to line
        if index == 1:
            self.set_line = False
            self.set_circle = True
            self.set_plus = False
            self.current_object = 'Circle'

        # sets the drawing tool to star
        if index == 2:
            self.set_line = False
            self.set_circle = False
            self.set_plus = True
            self.current_object = 'Plus'

    def trigger(self, index):
        if index == 1:
            if self.tool_index < 2:
                self.tool_index += 1
            else:
                self.tool_index = 0
            self.tool_indexer(self.tool_index)

        if index == 2:
            if self.color_index < len(self.color_list) - 1:
                self.color_index += 1
            else:
                self.color_index = 0

            self.color = self.color_list[self.color_index]
        if index == 3:
            self.image = cv2.imread("paint/image.png")
        if index == 4:
            cv2.imwrite("paint/image.png", self.image)
        if index == 5:
            cv2.destroyAllWindows()
            self.state = 'main_menu'
            self.state_manager()
        if index == 6:
            cv2.imwrite("paint/save.png", self.image)
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()

    def input_loop(self):
        while 1:
            self.pygame_input()
            self.selection_cooldown()
            self.draw_text('Size: ' + str(self.size), 35, 20, self.TEXT_COLOR)
            self.draw_text('Current tool: ' + str(self.current_object), 35, 50, self.TEXT_COLOR)
            self.draw_text('Color', 35, 80, self.color)
            self.draw_text('Load image', 35, 110, self.TEXT_COLOR)
            self.draw_text('Save image', 35, 140, self.TEXT_COLOR)
            self.draw_text('Back to menu', 35, 170, self.TEXT_COLOR)
            self.draw_text('Quit', 35, 200, self.TEXT_COLOR)
            self.draw_text('*', self.index_x, self.index_y, self.TEXT_COLOR)
            cv2.imshow('Paint2', self.image)
            k = cv2.waitKey(1)
            if k == 27:  # Escape, saves the img in jpg
                cv2.imwrite("paint/image.png", self.image)
                break
            # numpad minus
            if k == 45:
                if self.size >= 6:
                    self.size -= 5
            # numpad plus
            if k == 43:
                if self.size <= 99:
                    self.size += 5
            # g button, sets the color to green
            if k == 103:
                self.color = (0, 255, 0)
            # r button, sets the color to red
            if k == 114:
                self.color = (0, 0, 255)
            # b button, sets the color to blue
            if k == 98:
                self.color = (255, 0, 0)
            # k button, sets the color to black
            if k == 107:
                self.color = (0, 0, 0)
            # w button, sets the color to white
            if k == 119:
                self.color = (255, 255, 255)

            # t button, fills the whole page with the default values
            if k == 116:
                # if we want to use np we can use this:
                # self.image = np.zeros((480, 640, 3), np.uint8)
                # self.image.fill(255)

                # if we want to load a set image:
                self.image = cv2.imread("paint/image.png")

            # s button, saves the image in png
            if k == 115:
                cv2.imwrite("paint/image.png", self.image)

            # l button, loads an image
            if k == 108:
                self.image = cv2.imread("paint/image.png")

            # m button, sets the drawing tool to circle
            if k == 109:
                self.set_line = False
                self.set_circle = True
                self.set_plus = False
                self.current_object = 'Circle'

            # n button, sets the drawing tool to line
            if k == 110:
                self.set_line = True
                self.set_circle = False
                self.set_plus = False
                self.current_object = 'Line'

            # ',' or '?' button, sets the drawing tool to plus
            if k == 44:
                self.set_line = False
                self.set_circle = False
                self.set_plus = True
                self.current_object = 'Plus'

            # space
            if k == 32:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.trigger(self.ui_index)

            # j button, turns off the crosshair
            if k == 106:
                self.crosshair_enabled = False

            # p button, draws border
            if k == 112:
                self.border_drawn = True
                self.draw_border()
            pygame.display.update()
            self.screen.blit(self.background_image, (0, 0))

    # had to make a pygame input because the cv2 key handler doesn't recognise the arrow keys
    def pygame_input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_DOWN]:
                if self.ui_index < 6:
                    self.ui_index += 1
                    self.index_y += 30
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_UP]:
                if self.ui_index > 0:
                    self.ui_index -= 1
                    self.index_y -= 30
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.trigger(self.ui_index)

    # / paint state components

    # main menu state components
    def menu_input(self):
        keys = pygame.key.get_pressed()
        if self.can_move:
            if keys[pygame.K_DOWN]:
                if self.ui_index < 2:
                    self.ui_index += 1
                    self.index_y += 30
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_UP]:
                if self.ui_index > 0:
                    self.ui_index -= 1
                    self.index_y -= 30
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.menu_trigger(self.ui_index)

    def menu_trigger(self, index):
        # loads in an empty sheet
        if index == 0:
            self.state = 'paint'
            self.image.fill(255)
            self.state_manager()
        # loads in a set image
        if index == 1:
            self.state = 'paint'
            self.image = cv2.imread("paint/image.png")
            self.state_manager()
        # quit
        if index == 2:
            pygame.quit()
            sys.exit()

    def main_menu(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.draw_text('Start painting', 35, 20, self.TEXT_COLOR)
            self.draw_text('Load image', 35, 50, self.TEXT_COLOR)
            self.draw_text('Quit', 35, 80, self.TEXT_COLOR)
            self.draw_text('*', self.index_x, self.index_y, self.TEXT_COLOR)
            self.menu_input()
            self.selection_cooldown()
            pygame.display.update()
            self.screen.blit(self.background_image, (0, 0))

    # / main menu state components


if __name__ == '__main__':
    beadando = Beadando()
    beadando.run()
