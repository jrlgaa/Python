import pygame
import socket
import threading
import pickle
import random
from pygments.styles.paraiso_dark import RED

# Define the server details
SERVER_IP = '192.168.1.19'  # Use localhost if running on the same machine
PORT = 5555
ADDR = (SERVER_IP, PORT)

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect(ADDR)
except ConnectionRefusedError:
    print(f"Failed to connect to {SERVER_IP}:{PORT}. Is the server running?")
    exit(1)

# Initialize Pygame
pygame.init()

# Game variables
active_string = "P1 Tank"
active_string2 = "P2 Tank"
life = 200
life2 = 200


def receive_data():
    global active_string, active_string2, life, life2
    while True:
        try:
            data = client.recv(4096)
            if data:
                game_state = pickle.loads(data)
                active_string = game_state['word']
                life = game_state['player1_life']
                life2 = game_state['player2_life']
        except ConnectionResetError:
            break


def send_data():
    game_state = {
        'word': active_string,
        'player1_life': life,
        'player2_life': life2
    }
    client.send(pickle.dumps(game_state))


# Start a thread to receive data
thread = threading.Thread(target=receive_data)
thread.start()

# Screen dimensions and setup
WIDTH, HEIGHT = 1400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Wordsprint Showdown!')
timer = pygame.time.Clock()
fps = 120

# Load assets
Background = pygame.image.load('bg.png')
char1 = pygame.image.load('char.png')
char2 = pygame.image.load('char.png')


def resize_assets():
    """ Resize game assets dynamically based on window size """
    global font, header_font, banner_font, Background
    # Dynamic font scaling
    font_size = int(WIDTH * 0.022)
    header_font_size = int(WIDTH * 0.025)
    banner_font_size = int(WIDTH * 0.02)
    font = pygame.font.Font('Pixel Tandy.otf', font_size)
    header_font = pygame.font.SysFont('Pixel Tandy.otf', header_font_size)
    banner_font = pygame.font.SysFont('Pixel Modex.otf', banner_font_size)

    # Dynamic background scaling
    Background = pygame.transform.scale(pygame.image.load('bg.png'), (WIDTH, HEIGHT))


# Call to initialize fonts and assets
resize_assets()


def Background_sky(bg):
    screen.blit(bg, (0, 0))


def word_box(screen, word, x, y, width, height):
    pygame.draw.rect(screen, RED, (x, y, width, height), 2)
    text_surface = font.render(word, True, RED)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


def draw_screen():
    pygame.draw.rect(screen, 'white', [0, 0, WIDTH, HEIGHT], 5)
    pygame.draw.rect(screen, 'black', [0, 0, WIDTH, HEIGHT], 3)
    screen.blit(header_font.render(f'"{active_string}"', True, 'Black'), (WIDTH * 0.05, HEIGHT - 70))
    screen.blit(header_font.render(f'"{active_string2}"', True, 'Black'), (WIDTH * 0.9 - 200, HEIGHT - 70))
    screen.blit(banner_font.render(f'P1 Life: {life}', True, 'Black'), (WIDTH * 0.01, HEIGHT * 0.85))
    screen.blit(banner_font.render(f'P2 Life: {life2}', True, 'Black'), (WIDTH * 0.9, HEIGHT * 0.85))


def update_words():
    global active_string
    active_string = random.choice(words_list)
    send_data()


# Timing variables for word updates
change_interval = 4000
last_change_time = pygame.time.get_ticks()

# Main game loop
run = True
while run:
    timer.tick(fps)
    Background_sky(Background)
    draw_screen()

    current_time = pygame.time.get_ticks()
    if current_time - last_change_time >= change_interval:
        update_words()
        last_change_time = current_time

    word_box(screen, active_string, int(WIDTH * 0.43), int(HEIGHT * 0.05), int(WIDTH * 0.2), int(HEIGHT * 0.1))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.VIDEORESIZE:  # Handle window resize
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            resize_assets()  # Adjust elements when resizing

pygame.quit()
client.close()

