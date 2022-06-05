import pygame
import numpy as np
import time
import sys
from image_preprocessing import *

pygame.init()
BORDER_SIZE = 32 #left and right marging for well + right side margin
FREE_FALL = 512 #must be power of 2
WINDOW_SIZE = (1024 + 3*BORDER_SIZE, 512 + FREE_FALL)
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()
pygame.display.set_caption("Tetris Slicer")

# square class
class Square:

    sound_left = pygame.mixer.Sound(os.path.join("sounds", "left.wav"))
    sound_right = pygame.mixer.Sound(os.path.join("sounds", "right.wav"))
    sound_down = pygame.mixer.Sound(os.path.join("sounds", "down.wav"))
    sound_mirror = pygame.mixer.Sound(os.path.join("sounds", "down.wav"))

    def __init__(self, image_name):
        # x coordinate at the top left corner
        self.x = BORDER_SIZE
        # y coordinate at top of screen
        self.y = 0
        # pre-choosen fragment of whole image
        self.image = pygame.image.load(os.path.join('pool', image_name))
        # set random rotation
        self.rotation = random.randrange(0, 360, 90)
        # apply random rotation to an image
        self.image = pygame.transform.rotate(self.image, self.rotation)
        # mirrored
        if random.randrange(0, 2) == 1:
            self.image = flip_image(self.image) # vertical flip = True, horizontal flip = False
            self.shift = True
        else:
            self.shift = False
        rect = self.image.get_rect()
        # get square size
        self.size = rect[2]

        # array where [row_index, column_index]
        self.correct_place = [int(image_name[:2]), int(image_name[2:4])]
        # tile index for easier checking of position
        self.current_column = 0
        # offset for freefall at the top
        self.current_row = - FREE_FALL / self.size

        # time since last user action
        self.last = pygame.time.get_ticks()
        # time in which player can do another action (in miliseconds)
        self.cooldown = 250

    def rotate_left(self):
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            self.image = rotate_left(self.image)
            if self.shift:
                self.rotation += 270
            else:
                self.rotation += 90
        if self.rotation >= 360:
            self.rotation = self.rotation % 360
    
    def rotate_right(self):
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            self.image = rotate_right(self.image)
            if self.shift:
                self.rotation += 90
            else:
                self.rotation += 270
        if self.rotation >= 360:
            self.rotation = self.rotation % 360

    # in all below functions uncomment self.sound_<>.play() to allow sound effects
    def go_right(self):
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            self.x += self.size
            self.current_column += 1
            #self.sound_right.play()

    def go_left(self):
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            self.x += -self.size
            self.current_column -= 1
            #self.sound_left.play()

    def go_down(self):
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            self.y += self.size
            self.current_row += 1
            #self.sound_down.play()

    def mirror(self):
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            self.image = flip_image(self.image) # vertical flip = True, horizontal flip = False
            self.shift = not self.shift
            #self.sound_mirror.play()

    def go_down_auto(self):
        self.y += self.size
        self.current_row += 1

class Game:
    def __init__(self):
        # x and y position of mouse
        self.x = 0
        self.y = 0
        # chosen size of image
        self.size = 0
        # chosen image
        self.image = 0
        # continue button
        self.continue_button = False

        self.state = 'menu'
        self.photos_to_choose = [pygame.transform.scale(pygame.image.load(os.path.join('images_to_choose', '1.png')), (256, 256)),\
                                 pygame.transform.scale(pygame.image.load(os.path.join('images_to_choose', 'Saul.png')), (256, 256)),\
                                 pygame.transform.scale(pygame.image.load(os.path.join('images_to_choose', 'Szeregowy.png')), (256, 256))]

    def draw_menu(self):
        # set color to bg of menu
        screen.fill((26,26,26))

        # photos to choose from
        x = 128
        for photo in self.photos_to_choose:             
            screen.blit(photo, (x , FREE_FALL + 70))
            x += 256 + BORDER_SIZE
        
        # all the text in menu
        font = pygame.font.Font('freesansbold.ttf', 32)

        header_1 = font.render('CHOOSE NUMBER OF SQUARES', False, (3, 232, 252), (26,26,26))
        header_2 = font.render('CHOOSE PHOTO', False, (3, 232, 252), (26,26,26))
        continue_button = font.render('CONTINUE', False, (3, 232, 252), (26,26,26))
        text_1 = font.render('4 SQUARES', False, (3, 232, 252), (26,26,26))
        text_2 = font.render('16 SQUARES', False, (3, 232, 252), (26,26,26))
        text_3 = font.render('64 SQUARES', False, (3, 232, 252), (26,26,26))
        text_4 = font.render('256 SQUARES', False, (3, 232, 252), (26,26,26))
    
        #highlight chosen size
        if self.size == 4:
            text_1 = font.render('4 SQUARES', False, (19, 191, 36), (26,26,26))
        if self.size == 16:
            text_2 = font.render('16 SQUARES', False, (19, 191, 36), (26,26,26))
        if self.size == 64:
            text_3 = font.render('64 SQUARES', False, (19, 191, 36), (26,26,26))
        if self.size == 256:
            text_4 = font.render('256 SQUARES', False, (19, 191, 36), (26,26,26))
            
        #highlight continue button
        if self.continue_button:
            continue_button = font.render('CONTINUE', False, (19, 191, 36), (26,26,26))

        headerRect_1 = header_1.get_rect()
        headerRect_1.center = (WINDOW_SIZE[0] / 2, (WINDOW_SIZE[1] - FREE_FALL) / 2 - 100)
        headerRect_2 = header_2.get_rect()
        headerRect_2.center = (WINDOW_SIZE[0] / 2, FREE_FALL)

        continueRect = continue_button.get_rect()
        continueRect.center = (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] - 50)

        textRect_1 = text_1.get_rect()
        textRect_1.center = (120, FREE_FALL - 250)
        textRect_2 = text_2.get_rect()
        textRect_2.center = (400, FREE_FALL - 250)
        textRect_3 = text_3.get_rect()
        textRect_3.center = (690, FREE_FALL - 250)
        textRect_4 = text_4.get_rect()
        textRect_4.center = (980, FREE_FALL - 250)

        textRects = [textRect_1, textRect_2, textRect_3, textRect_4, continueRect]

        screen.blit(continue_button, continueRect)
        screen.blit(header_1, headerRect_1)
        screen.blit(header_2, headerRect_2)
        screen.blit(text_1, textRect_1)
        screen.blit(text_2, textRect_2)
        screen.blit(text_3, textRect_3)
        screen.blit(text_4, textRect_4)

        # squares around pressable buttons with text
        offset = 10
        for text in textRects:
            #top horizontal lines
            pygame.draw.line(screen, color=(3, 232, 252),\
                            start_pos = (text.bottomleft[0] - offset, text.topleft[1] - offset),\
                            end_pos = (text.bottomright[0] + offset, text.topleft[1] - offset))
            #bottom horizontal lines
            pygame.draw.line(screen, color=(3, 232, 252),\
                            start_pos = (text.bottomleft[0] - offset, text.bottomleft[1] + offset),\
                            end_pos = (text.bottomright[0] + offset, text.bottomleft[1] + offset))
            #left vertical lines
            pygame.draw.line(screen, color=(3, 232, 252),\
                            start_pos = (text.bottomleft[0] - offset, text.topleft[1] - offset),\
                            end_pos = (text.bottomleft[0] - offset, text.bottomleft[1] + offset))
            #right vertical lines
            pygame.draw.line(screen, color=(3, 232, 252),\
                            start_pos = (text.bottomright[0] + offset, text.topright[1] - offset),\
                            end_pos = (text.bottomright[0] + offset, text.bottomright[1] + offset))

        # squares around photos:
        for x in range(128, 768 ,256 + BORDER_SIZE):
            #top horizontal lines    
            pygame.draw.line(screen, color=(3, 232, 252),\
                            start_pos = (x, FREE_FALL + 70),\
                            end_pos = (x + 256, FREE_FALL + 70))
            #bottom horizontal lines    
            pygame.draw.line(screen, color=(3, 232, 252),\
                            start_pos = (x, FREE_FALL + 70 + 256),\
                            end_pos = (x + 256, FREE_FALL + 70 + 256))
            #left vertical lines    
            pygame.draw.line(screen, color=(3, 232, 252),\
                            start_pos = (x, FREE_FALL + 70),\
                            end_pos = (x, FREE_FALL + 70 + 256))
            #right vertical lines    
            pygame.draw.line(screen, color=(3, 232, 252),\
                            start_pos = (x + 256, FREE_FALL + 70),\
                            end_pos = (x + 256, FREE_FALL + 70 + 256))
        
        #highlight chosen image
        if self.image != 0:
            #top horizontal lines    
            pygame.draw.line(screen, color=(19, 191, 36),\
                            start_pos = (self.image, FREE_FALL + 70),\
                            end_pos = (self.image + 256, FREE_FALL + 70))
            #bottom horizontal lines    
            pygame.draw.line(screen, color=(19, 191, 36),\
                            start_pos = (self.image, FREE_FALL + 70 + 256),\
                            end_pos = (self.image + 256, FREE_FALL + 70 + 256))
            #left vertical lines    
            pygame.draw.line(screen, color=(19, 191, 36),\
                            start_pos = (self.image, FREE_FALL + 70),\
                            end_pos = (self.image, FREE_FALL + 70 + 256))
            #right vertical lines    
            pygame.draw.line(screen, color=(19, 191, 36),\
                            start_pos = (self.image + 256, FREE_FALL + 70),\
                            end_pos = (self.image + 256, FREE_FALL + 70 + 256))

        pygame.display.update()


def grayscale(img):
    arr = pygame.surfarray.array3d(img)
    #luminosity filter
    avgs = [[(r*0.298 + g*0.587 + b*0.114) for (r,g,b) in col] for col in arr]
    arr = np.array([[[avg,avg,avg] for avg in col] for col in avgs])
    return pygame.surfarray.make_surface(arr)

def draw_window(x, y, size, falling_image, placed_images, gray_scale_image, preview_image, text, text_rect):
    # background color
    screen.fill((26,26,26))

    # preview image in well
    screen.blit(gray_scale_image, (BORDER_SIZE, FREE_FALL))

    # preview image
    screen.blit(preview_image, (WINDOW_SIZE[0] / 2 + BORDER_SIZE, WINDOW_SIZE[1] / 2 - 200))

    # falling image
    screen.blit(falling_image, (x, y))

    # horizontal lines in grid
    for i in range(FREE_FALL, WINDOW_SIZE[1], size):
        pygame.draw.line(screen, color=(76, 121, 125), start_pos=(BORDER_SIZE, i), end_pos=((WINDOW_SIZE[0] - 3*BORDER_SIZE)/2 + BORDER_SIZE, i))

    # vertical lines in grid
    for i in range(BORDER_SIZE + size, int((WINDOW_SIZE[0] - 3*BORDER_SIZE)/2 + BORDER_SIZE), size):
        pygame.draw.line(screen, color=(76, 121, 125), start_pos=(i, FREE_FALL), end_pos=(i, WINDOW_SIZE[1]))

    # correctly placed image
    for element in placed_images:
        if element != None:
            screen.blit(element.image, (element.x , element.y))
    
    # left line
    pygame.draw.line(screen, color=(3, 232, 252),\
                    start_pos=(BORDER_SIZE, 0),\
                    end_pos=(BORDER_SIZE, WINDOW_SIZE[1]))
    # middle line
    pygame.draw.line(screen, color=(3, 232, 252),\
                    start_pos=((WINDOW_SIZE[0] - 3*BORDER_SIZE)/2 + BORDER_SIZE, 0),\
                    end_pos=((WINDOW_SIZE[0] - 3*BORDER_SIZE)/2 + BORDER_SIZE, WINDOW_SIZE[1]))
    
    # points
    if text != None:
        screen.blit(text, text_rect)

    pygame.display.update()

def main():
    game = Game()
    while game.state == 'menu':
        game.x, game.y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.state == 'terminate'
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # number of squares choosing
                if game.x > 14 and game.x < 207 and game.y > 246 and game.y < 278:
                    print("Chose 4 squares")
                    game.size = 4
                    size = 256
                if game.x > 305 and game.x < 648 and game.y > 246 and game.y < 278:
                    print("Chose 16 squares")
                    game.size = 16
                    size = 128
                if game.x > 605 and game.x < 816 and game.y > 246 and game.y < 278:
                    print("Chose 64 squares")
                    game.size = 64
                    size = 64
                if game.x > 896 and game.x < 1125 and game.y > 246 and game.y < 278:
                    print("Chose 256 squares")
                    game.size = 256
                    size = 32

                # photo choosing
                if game.x > 128 and game.x < 384 and game.y > 582 and game.y < 838:
                    choen_image_name = "1.png"
                    game.image = 128
                    print("Chose waves")
                if game.x > 416 and game.x < 672 and game.y > 582 and game.y < 838:
                    choen_image_name = "Saul.png"
                    game.image = 128 + 256 + BORDER_SIZE
                    print("Chose Saul")
                if game.x > 704 and game.x < 960 and game.y > 582 and game.y < 838:
                    choen_image_name = "Szeregowy.png"
                    game.image = 128 + 2*(256 + BORDER_SIZE)
                    print("Chose Szeregowy")
                
                # save choices and continue to actual game
                if game.x > 473 and game.x < 648 and game.y > 958 and game.y < 990:
                    game.continue_button = True
                    game.state = 'running'

        game.draw_menu()


    # initialization
    chosen_image_path = os.path.join("images_to_choose", choen_image_name)
    preview_image = pygame.image.load(chosen_image_path)
    gray_scale_image = grayscale(pygame.image.load(chosen_image_path))
    im = Image.open(chosen_image_path)
    im = im.resize((512,512)) # resize in case original photo isn't 512x512
    im.save(os.path.join("images_to_choose", choen_image_name))
    crop(chosen_image_path, size) # cuts photo into (512 / size)^2 squares
    row_index = int(512 / size) - 1
    correct_images = []
    speed = 1000

    # initalization of first falling square
    random_image = choose_radnom(row_index)
    tile = Square(random_image)
    move_to_processed(random_image)
    time_elapsed_since_last_action = 0
    start_timer = time.time()


    # main game loop
    while game.state == 'running':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.state = 'points_screen'
                pygame.quit()
        
        if tile.correct_place == [tile.current_row, tile.current_column] and tile.rotation == 0 and tile.shift == False:
            # correct place, keep this one, draw another

            if len(os.listdir("processed_tiles")) == int(512 / size):
                # clear processed_tiles
                [f.unlink() for f in Path("processed_tiles").glob("*") if f.is_file()]
                row_index -= 1

            correct_images.append(tile)

            if len(correct_images) == int(512 / size) * int(512 / size):
                game.state = 'points_screen'
                points = game.size*10000 / (time.time() - start_timer)
            else:
                random_image = choose_radnom(row_index)
                tile = Square(random_image)
                move_to_processed(random_image)
                time_elapsed_since_last_action = 0


        if tile.current_row == row_index and (tile.correct_place[1] != tile.current_column or tile.rotation != 0 or tile.shift == True):
            # wrong place, move this one back to pool, draw another
            move_to_pool(random_image)
            random_image = choose_radnom(row_index)
            tile = Square(random_image)
            move_to_processed(random_image)
            time_elapsed_since_last_action = 0

        userInput = pygame.key.get_pressed()
        dt = clock.tick()
        time_elapsed_since_last_action += dt
        if time_elapsed_since_last_action > speed:
            if tile.y + tile.size < WINDOW_SIZE[1]:
                tile.go_down_auto()
            time_elapsed_since_last_action = 0

        if (userInput[pygame.K_LEFT] or userInput[pygame.K_a]) and tile.x - tile.size > 0:
            tile.go_left()
        if (userInput[pygame.K_RIGHT] or userInput[pygame.K_d]) and tile.x + tile.size < (WINDOW_SIZE[0] - BORDER_SIZE)/2:
            tile.go_right()
        if userInput[pygame.K_SPACE] and tile.y + tile.size < WINDOW_SIZE[1]:
            tile.go_down()
        if (userInput[pygame.K_UP] or userInput[pygame.K_w]):
            tile.rotate_right()
        if (userInput[pygame.K_DOWN] or userInput[pygame.K_s]):
            tile.rotate_left()
        if (userInput[pygame.K_q]):
            tile.mirror()

        draw_window(tile.x, tile.y, tile.size, tile.image, correct_images, gray_scale_image, preview_image, text = None, text_rect = None)
    

    end_screen = True
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(f'Points: {round(points)}', False, (3, 232, 252), (26,26,26))
    textRect = text.get_rect()
    textRect.center = ((WINDOW_SIZE[0])/2 + 5*BORDER_SIZE, 200)


    while end_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_screen = False
                pygame.quit()
                sys.exit()
        draw_window(tile.x, tile.y, tile.size, tile.image, correct_images, gray_scale_image, preview_image, text, textRect)

# to not run other files while running main
if __name__ == "__main__":
    main()