import pygame
import random

pygame.init()
pygame.mixer.init()

# Declaring window size, columns, and rows
WIDTH, HEIGHT = 600, 800
CELLSIZE = 28
ROWS = 20
COLUMNS = 10
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

FPS = 60

# color codes
RED = (255, 0, 0)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Fonts
score_font = pygame.font.SysFont("Adobe Gothic Std Kalin", 55)
lvl_font = pygame.font.SysFont("Futura Black", 30)
# load sounds
# taken from OpengameArt and Freesound
level_completion = pygame.mixer.Sound('sounds\lvl_complete.mp3')
background_noise = pygame.mixer.Sound('sounds\/background_noise.mp3')
game_over_sound = pygame.mixer.Sound('sounds\game_over.mp3')
hard_mode = pygame.mixer.Sound('sounds\push_ahead.ogg')

# load all images
img1 = pygame.image.load('Pieces\I_piece.png')
img2 = pygame.image.load('Pieces\J_piece.png')
img3 = pygame.image.load('Pieces\L_piece.png')
img4 = pygame.image.load('Pieces\O_piece.png')
img5 = pygame.image.load('Pieces\S_piece.png')
img6 = pygame.image.load('Pieces\T_piece.png')
img7 = pygame.image.load('Pieces\Z_piece.png')

IMAGE_SCALING = (26, 26)

# scaling of images

img1 = pygame.transform.scale(img1, IMAGE_SCALING)
img2 = pygame.transform.scale(img2, IMAGE_SCALING)
img3 = pygame.transform.scale(img3, IMAGE_SCALING)
img4 = pygame.transform.scale(img4, IMAGE_SCALING)
img5 = pygame.transform.scale(img5, IMAGE_SCALING)
img6 = pygame.transform.scale(img6, IMAGE_SCALING)
img7 = pygame.transform.scale(img7, IMAGE_SCALING)

IMAGES = {
    "I": img1,
    "J": img2,
    "L": img3,
    "O": img4,
    "S": img5,
    "T": img6,
    "Z": img7,
}


class Tetramino:

    # dictionary of tetramino to its shape + rotation variants
    SHAPE = {
        "I": [[1, 5, 9, 13], [4, 5, 6, 7], [2, 6, 10, 14], [8, 9, 10, 11]],
        "J": [[1, 2, 5, 9], [4, 5, 6, 10], [1, 5, 9, 8], [0, 4, 5, 6]],
        "L": [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        "O": [[1, 2, 5, 6], [1, 2, 5, 6], [1, 2, 5, 6], [1, 2, 5, 6]],
        "S": [[2, 3, 5, 6], [2, 6, 7, 11], [6, 7, 9, 10], [1, 5, 6, 10]],
        "T": [[1, 4, 5, 6], [1, 5, 6, 9], [4, 5, 6, 9], [1, 4, 5, 9]],
        "Z": [[0, 1, 5, 6], [2, 5, 6, 9], [4, 5, 9, 10], [2, 5, 6, 9]]
    }

    TYPES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']

    def __init__(self, x, y):
        self.x = x + (160 + 2 + 3*CELLSIZE)
        self.y = y + (120 + 2)
        self.type = random.choice(self.TYPES)
        self.shape = self.SHAPE[self.type]
        self.color = self.type
        self.rotation = 0

    # returns current rotation arrangement
    def image(self):
        return self.shape[self.rotation]

    # rotates tetramino clockwise
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)


class Tetris:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.level = 0
        self.score = 0
        self.next = None
        self.next1 = None
        self.next2 = None
        self.hold = None
        # 20x10 array to act as board
        self.board = [[0 for j in range(cols)] for i in range(rows)]
        self.gameover = False
        self.new_figure()

    # draws column and row lines of grid on board
    def draw_grid(self):
        for i in range(1, self.rows):
            pygame.draw.line(win, GRAY, (162, CELLSIZE*i + 120),
                             (WIDTH - 163, CELLSIZE*i + 120), 2)
        for j in range(1, self.cols):
            pygame.draw.line(win, GRAY, (CELLSIZE*j + 160, 122),
                             (CELLSIZE*j + 160, HEIGHT - 123), 2)

    def new_figure(self):
        if not self.next:
            self.next = Tetramino(0, 0)
        if not self.next1:
            self.next1 = Tetramino(0, 0)
        if not self.next2:
            self.next2 = Tetramino(0, 0)
        self.figure = self.next
        self.next = self.next1
        self.next1 = self.next2
        self.next2 = Tetramino(0, 0)

    def hold_figure(self):
        if not self.hold:
            self.hold = self.figure
            self.new_figure()
        else:
            temp = self.hold
            self.hold = self.figure
            self.figure = temp

# GAME MECHANICS
    def gravity(self):
        self.figure.y += CELLSIZE
        if self.collision():
            self.figure.y -= CELLSIZE
            self.freeze()

    def sideways_movement(self, direction):
        # +1 : right
        # -1 : left
        self.figure.x += CELLSIZE*direction
        if self.collision():
            self.figure.x -= CELLSIZE*direction

    def down_movement(self):
        self.figure.y += CELLSIZE
        if self.collision():
            self.figure.y -= CELLSIZE
            self.freeze()

    def instant_drop(self):
        while not self.collision():
            self.figure.y += CELLSIZE
        self.figure.y -= CELLSIZE
        self.freeze()

    def rotate(self):
        self.figure.rotate()

    def collision(self):
        collision = False

        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if j*CELLSIZE + self.figure.x < 162 or \
                        j * CELLSIZE + self.figure.x > WIDTH - 162 or \
                            i * CELLSIZE + self.figure.y > 654 or \
                            self.board[i + (self.figure.y - 122) // CELLSIZE][j + (self.figure.x - 162) // CELLSIZE] != 0:
                        collision = True

        return collision

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.board[i + (self.figure.y - 122) // CELLSIZE][j +
                                                                      (self.figure.x - 162) // CELLSIZE] = self.figure.type
        self.clear_line()
        self.new_figure()
        if self.collision():
            self.gameover = True

    def clear_line(self):
        cleared_rows = 0
        recurse = False
        for row in range(self.rows - 1, -1, -1):
            cleared, skip = False, False
            for column in range(self.cols):
                if self.board[row][column] == 0:
                    skip = True
                    break
            if skip == True:
                continue
            cleared = True

            if cleared:
                pygame.mixer.Sound.stop(background_noise)
                pygame.mixer.Sound.play(level_completion)
                pygame.mixer.Sound.set_volume(level_completion, .5)

                del self.board[row]
                self.board.insert(0, [0 for i in range(self.cols)])
                cleared_rows += 1
                self.score += 10 * (self.level + 1)
                recurse = True

                if self.score % (80 + 20 * (self.level+1)) == 0:
                    self.level += 1
        if recurse:
            self.clear_line()

        return cleared_rows

# Board Outline


def draw_board():
    win.fill(BLACK)
    # frame 280 x 560
    pygame.draw.rect(win, RED, pygame.Rect(
        160, 120, WIDTH-160*2, HEIGHT-120*2), 2)


def main():
    playing = True
    clock = pygame.time.Clock()

    block_fall = pygame.USEREVENT + 1
    tetris = Tetris(ROWS, COLUMNS)
    # blocks fall periodically, faster when the level is higher
    pygame.time.set_timer(block_fall, 1000 - 50 * (tetris.level+1))

    is_paused = False
    hard = False

    while (playing):
        clock.tick(FPS)  # maintains 60 fps
        image = tetris.figure.image()
        next_block = tetris.next.image()
        next1_block = tetris.next1.image()
        next2_block = tetris.next2.image()
        key = pygame.key.get_pressed()

        # initialization of empty board/playing area
        draw_board()
        tetris.draw_grid()

        if tetris.level >= 5:
            hard = True

        # background noise
        if not hard:
            pygame.mixer.Sound.play(background_noise, -1)
            pygame.mixer.Sound.set_volume(background_noise, 0.04)
        else:
            pygame.mixer.Sound.stop(background_noise)
            pygame.mixer.Sound.play(hard_mode, -1)
            pygame.mixer.Sound.set_volume(hard_mode, 0.04)

        # monitors player inputs and game mechanics
        for event in pygame.event.get():
            if event.type == pygame.QUIT or key[pygame.K_ESCAPE] or key[pygame.K_q]:
                playing = False
                break
            if not is_paused:
                if key[pygame.K_LEFT]:
                    tetris.sideways_movement(-1)
                if key[pygame.K_RIGHT]:
                    tetris.sideways_movement(1)
                if key[pygame.K_DOWN]:
                    tetris.down_movement()
                if key[pygame.K_UP]:
                    tetris.rotate()
                if key[pygame.K_SPACE]:
                    tetris.instant_drop()
                if key[pygame.K_c]:
                    if tetris.hold:
                        tetris.hold.x = tetris.figure.x
                        tetris.hold.y = tetris.figure.y
                    tetris.hold_figure()
                    held_block = tetris.hold.image()
                if event.type == block_fall:
                    if not tetris.gameover:
                        tetris.gravity()
            if key[pygame.K_p]:
                is_paused = not is_paused
            if key[pygame.K_r]:
                tetris.__init__(ROWS, COLUMNS)
                is_paused = False

        # SHOWS PLACED PIECES
        for x in range(ROWS):
            for y in range(COLUMNS):
                if tetris.board[x][y] in IMAGES.keys():
                    val = tetris.board[x][y]
                    img_saved = IMAGES[val]
                    win.blit(img_saved, (y * CELLSIZE + 162, x * CELLSIZE + 122))

        # SPAWNS CURRENT PIECE
        for indx in range(len(image)):
            x = tetris.figure.x
            y = tetris.figure.y
            if 4 > image[indx]:
                x += image[indx] * CELLSIZE
            elif 4 <= image[indx] <= 7:
                x += (image[indx] % 4)*CELLSIZE
                y += CELLSIZE
            elif 8 <= image[indx] <= 11:
                x += (image[indx] % 4)*CELLSIZE
                y += CELLSIZE*2
            elif 12 <= image[indx]:
                x += (image[indx] % 4)*CELLSIZE
                y += CELLSIZE*3
            img = IMAGES[tetris.figure.color]
            win.blit(img, (x, y))

        # PAUSE MENU
        if is_paused:
            pygame.mixer.Sound.stop(background_noise)
            pause_box = pygame.Rect(189, 177, 8 * CELLSIZE, 12 * CELLSIZE)
            pygame.draw.rect(win, BLACK, pause_box)
            border = pygame.Rect(189, 177, 8 * CELLSIZE, 12 * CELLSIZE)
            pygame.draw.rect(win, RED, border, 2)

            gameover = score_font.render("Paused", True, WHITE)
            pause = lvl_font.render("Press 'p' to resume", True, WHITE)
            restart = lvl_font.render("Press 'r' to restart", True, WHITE)
            quit = lvl_font.render("Press 'q' to quit", True, WHITE)

            win.blit(gameover, (pause_box.centerx -
                     gameover.get_width()//2, pause_box.y + 2 * CELLSIZE))
            win.blit(pause, (pause_box.centerx-pause.get_width() //
                     2, pause_box.y + 6 * CELLSIZE))
            win.blit(restart, (pause_box.centerx-restart.get_width() //
                     2, pause_box.y + 7 * CELLSIZE))
            win.blit(quit, (pause_box.centerx-quit.get_width() //
                     2, pause_box.y + 8 * CELLSIZE))

        # HUD
        if tetris.next:
            # next piece
            for indx in range(len(next_block)):
                x = tetris.next.x + 8 * CELLSIZE
                y = tetris.next.y + 2 * CELLSIZE
                if 4 > next_block[indx]:
                    x += next_block[indx] * CELLSIZE
                elif 4 <= next_block[indx] <= 7:
                    x += (next_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE - 1
                elif 8 <= next_block[indx] <= 11:
                    x += (next_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE*2 - 1
                elif 12 <= next_block[indx]:
                    x += (next_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE*3 - 1
                img = IMAGES[tetris.next.color]
                win.blit(img, (x, y))

            # next next piece
            for indx in range(len(next1_block)):
                x = tetris.next.x + 8 * CELLSIZE
                y = tetris.next.y + 7 * CELLSIZE
                if 4 > next1_block[indx]:
                    x += next1_block[indx] * CELLSIZE
                elif 4 <= next1_block[indx] <= 7:
                    x += (next1_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE - 1
                elif 8 <= next1_block[indx] <= 11:
                    x += (next1_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE*2 - 1
                elif 12 <= next1_block[indx]:
                    x += (next1_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE*3 - 1
                img = IMAGES[tetris.next1.color]
                win.blit(img, (x, y))

            # next next next piece
            for indx in range(len(next2_block)):
                x = tetris.next.x + 8 * CELLSIZE
                y = tetris.next.y + 12 * CELLSIZE
                if 4 > next2_block[indx]:
                    x += next2_block[indx] * CELLSIZE
                elif 4 <= next2_block[indx] <= 7:
                    x += (next2_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE - 1
                elif 8 <= next2_block[indx] <= 11:
                    x += (next2_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE*2 - 1
                elif 12 <= next2_block[indx]:
                    x += (next2_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE*3 - 1
                img = IMAGES[tetris.next2.color]
                win.blit(img, (x, y))

        # DISPLAYS CURRENT HELD BLOCK
        if tetris.hold:
            for indx in range(len(held_block)):
                x = 162 - 5 * CELLSIZE
                y = 122 + 2 * CELLSIZE
                if 4 > held_block[indx]:
                    x += held_block[indx] * CELLSIZE
                elif 4 <= held_block[indx] <= 7:
                    x += (held_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE - 1
                elif 8 <= held_block[indx] <= 11:
                    x += (held_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE*2 - 1
                elif 12 <= held_block[indx]:
                    x += (held_block[indx] % 4)*CELLSIZE
                    y += CELLSIZE*3 - 1
                img = IMAGES[tetris.hold.color]
                win.blit(img, (x, y))

        score = score_font.render(f'{tetris.score}', True, WHITE)
        level = lvl_font.render(f'Level: {tetris.level}', True, WHITE)
        nxt_text = lvl_font.render(f'NEXT', True, WHITE)
        hold_text = lvl_font.render(f'HOLD',  True, WHITE)

        win.blit(score, (tetris.next.x + 8 * CELLSIZE,
                 HEIGHT - tetris.next.y - 3 * CELLSIZE))
        win.blit(level, (tetris.next.x + 8 * CELLSIZE,
                 HEIGHT - tetris.next.y - CELLSIZE))
        win.blit(nxt_text, (WIDTH-160 + nxt_text.get_width() //
                 2, tetris.next.y))
        win.blit(hold_text, (160 - 4 * CELLSIZE, tetris.next.y))

        # GAME OVER
        if not tetris.gameover:
            counter = 0
        else:
            if counter == 0:
                pygame.mixer.Sound.stop(background_noise)
                pygame.mixer.Sound.play(game_over_sound)
                pygame.mixer.Sound.set_volume(game_over_sound, 0.1)
            counter += 1
            end_prompt = pygame.Rect(189, 177, 8 * CELLSIZE, 12 * CELLSIZE)
            pygame.draw.rect(win, BLACK, end_prompt)
            border = pygame.Rect(189, 177, 8 * CELLSIZE, 12 * CELLSIZE)
            pygame.draw.rect(win, RED, border, 2)

            gameover = score_font.render("Game Over", True, WHITE)
            restart = lvl_font.render("Press 'r' to restart", True, WHITE)
            quit = lvl_font.render("Press 'q' to quit", True, WHITE)

            win.blit(gameover, (end_prompt.centerx -
                     gameover.get_width()//2, end_prompt.y + 2 * CELLSIZE))
            win.blit(restart, (end_prompt.centerx-restart.get_width() //
                     2, end_prompt.y + 6 * CELLSIZE))
            win.blit(quit, (end_prompt.centerx-quit.get_width() //
                     2, end_prompt.y + 7 * CELLSIZE))

            is_paused = True

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
