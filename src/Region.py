import cv2
import numpy as np
from matplotlib import pyplot as plt

# define the colors
# we will later count the amount of red and green in the image to determine the winner
RED = (0, 0, 255)
GREEN = (0, 176, 80)
DEFAULT_THRESHOLD = 2

# region dataclass
class Region:
    player: str
    opponent: str
    game: str
    TL: tuple
    TR: tuple
    BL: tuple
    BR: tuple

    image: np.ndarray

    def __init__(self, player, opponent, game, TL, TR, BL, BR, image):
        self.player = player
        self.opponent = opponent
        self.game = game
        self.TL = TL
        self.TR = TR
        self.BL = BL
        self.BR = BR
        self.image = image
    
    def __str__(self):

        string = f'{self.game} TL: {self.TL}, TR: {self.TR}, BL: {self.BL}, BR: {self.BR}'

        return string
    
    def count_color(self, r, g, b, threshold=DEFAULT_THRESHOLD):
        mask = cv2.inRange(self.image, (b-threshold, g-threshold, r-threshold), (b+threshold, g+threshold, r+threshold))
        return cv2.countNonZero(mask)

    def count_red(self, threshold=DEFAULT_THRESHOLD):

        # convert the colors to the right format
        # r, g, b = RED
        # r = r / 255
        # g = g / 255
        # b = b / 255

        # counts how often RED is in the image
        return self.count_color(RED[0], RED[1], RED[2], threshold)

    def count_green(self, threshold=DEFAULT_THRESHOLD):
        # counts how often GREEN is in the image
        return self.count_color(GREEN[2], GREEN[1], GREEN[0], threshold)
    
    def print_colors(self, threshold=DEFAULT_THRESHOLD):
        print(f'Red: {self.count_red(threshold)}, Green: {self.count_green(threshold)}')

    def get_win(self):
        red = self.count_red()
        green = self.count_green()

        if red > green:
            return 0
        elif green > red:
            return 1
        else:
            # no winner
            # red and green are equal (probably both 0)
            return 0.5
    
    def show_image(self):
        plt.imshow(self.image)
        plt.show()
    
    def get_image(self):
        return self.image
    
    def set_image(self, image):
        self.image = image
    
    def get_corners(self):
        return self.TL, self.TR, self.BL, self.BR