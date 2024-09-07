from collections import deque
import pygame
import random
import copy
from pygments.styles.paraiso_dark import RED

pygame.init()

# Screen dimensions and setup
WIDTH = 1400
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Wordsprint Showdown!')
timer = pygame.time.Clock()
fps = 120

# Fonts setup
font = pygame.font.Font('Pixel Tandy.otf', 30)
header_font = pygame.font.SysFont('Pixel Tandy.otf', 35)
pause_font = pygame.font.SysFont('Sans', 38)
banner_font = pygame.font.SysFont('Pixel Modex.otf', 30)

# List of words to be displayed
words_list = ["Acknowledge", "Achievement", "Administration", "Agreement", "Alternative", "Anniversary",
              "Appointment", "Approximately", "Assessment", "Atmosphere", "Background", "Basketball", "Beginning",
              "Biological", "Boundary", "Breakfast", "Business", "Brilliant", "Beneath", "Behavior", "Campaign",
              "Candidate", "Capability", "Capacity", "Celebration", "Celebrate", "Ceremony", "Certainly",
              "Championship", "Champion", "Changing", "Characteristic", "Characterize", "Chemical", "Childhood",
              "Chicken", "Chocolate", "Cholesterol", "Circumstance", "Cigarette", "Communicate", "Communication",
              "Community", "Comprehensive", "Concentration", "Concerned", "Congressional", "Consciousness",
              "Constitutional", "Decrease", "Defendant", "Defensive", "Democracy", "Democratic", "Demonstrate",
              "Demonstration", "Department", "Dependent", "Depending", "Depression", "Description", "Desperate",
              "Destruction", "Developing", "Development", "Difference", "Discrimination", "Economist", "Economics",
              "Education", "Educational", "Effectively", "Electricity", "Elsewhere", "Emergency", "Emotional",
              "Employment", "Enforcement", "Engineering", "Entertainment", "Environmental", "Establishment",
              "Examination", "Expectation", "Extraordinary", "Financial", "Following", "Football", "Formation",
              "Foundation", "Framework"]

# Load assets
Background = pygame.image.load('bg.png')
char1 = pygame.image.load('char.png')
char2 = pygame.image.load('char.png')


def Background_sky(bg):
    """
    Draws the background image scaled to fit the screen.
    """
    size = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    screen.blit(size, (0, 0))


def word_box(screen, word, x, y, width, height):
    """
    Draws a rectangle with a word centered inside it.

    :param screen: The screen surface to draw on.
    :param word: The word to display.
    :param x: The x-coordinate of the rectangle's top-left corner.
    :param y: The y-coordinate of the rectangle's top-left corner.
    :param width: The width of the rectangle.
    :param height: The height of the rectangle.
    """
    pygame.draw.rect(screen, RED, (x, y, width, height), 2)
    text_surface = font.render(word, True, RED)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


def draw_screen():
    """
    Draws the main screen elements including outlines, headers, and status texts.
    """
    # Draw screen outlines
    pygame.draw.rect(screen, 'white', [0, 0, WIDTH, HEIGHT], 5)
    pygame.draw.rect(screen, 'black', [0, 0, WIDTH, HEIGHT], 3)

    # Draw text and input displays
    screen.blit(header_font.render(f'"{active_string}"', True, 'Black'), (50, HEIGHT - 70))
    screen.blit(header_font.render(f'"{active_string2}"', True, 'Black'), (1250, HEIGHT - 70))
    screen.blit(banner_font.render(f'P1 Life: {life}', True, 'Black'), (10, 650))
    screen.blit(banner_font.render(f'P2 Life: {life2}', True, 'Black'), (1270, 650))


def update_words():
    """
    Selects a new random word from the words list to display.
    """
    global random_word
    random_word = random.sample(words_list, 1)


# Game variables
active_string = "P1 Tank"
active_string2 = "P2 Tank"
life = 200
life2 = 200
streak = 0

# Initial word update
update_words()

# Timing variables for word updates
change_interval = 4000  # Update interval in milliseconds (2.5 seconds)
last_change_time = pygame.time.get_ticks()  # Time of last update

# Main game loop
run = True
while run:
    timer.tick(fps)  # Maintain game frame rate
    Background_sky(Background)  # Draw background
    draw_screen()  # Draw main screen elements

    current_time = pygame.time.get_ticks()  # Get current time
    if current_time - last_change_time >= change_interval:  # Check if it's time to update words
        update_words()  # Update words
        last_change_time = current_time  # Update last change time

    for i in range(1):  # Display words (currently showing one word)
        word_box(screen, random_word[i], 600, 50 + i * 200, 260, 100)

    pygame.display.flip()  # Update the display

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False  # Exit the game loop if the window is closed

pygame.quit()  # Quit pygame when done
