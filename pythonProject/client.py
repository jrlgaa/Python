import pygame
import socket
import threading
import pickle
import random
import time
import os

# Define the server details
SERVER_IP = '192.168.1.10'
PORT = 5555
ADDR = (SERVER_IP, PORT)

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect(ADDR)
except ConnectionRefusedError:
    print(f"Failed to connect to {SERVER_IP}:{PORT}. Is the server running?")
    exit(1)
except Exception as e:
    print(f"Error connecting to server: {e}")
    exit(1)

# Initialize Pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load('bg music.wav')
pygame.mixer.music.play(1)

# Game variables
active_string = "Game Start"
life = 200
life2 = 200
countdown_started = False
change_interval = 4000  # Duration between word changes in milliseconds

# Text input variables
input_text_p1 = ""
input_text_p2 = ""
input_rect_p1 = pygame.Rect(50, 550, 300, 70)
input_rect_p2 = pygame.Rect(1040, 550, 300, 70)
input_active_p1 = False
input_active_p2 = False
font = pygame.font.Font('Pixel Coleco.otf', 30)
base_font = pygame.font.Font('Pixel Coleco.otf', 30)

def receive_data():
    global active_string, life, life2
    while True:
        try:
            data = client.recv(4096)
            if not data:
                print("No data received or connection closed")
                break

            try:
                game_state = pickle.loads(data)
                if isinstance(game_state, dict):
                    if 'word' in game_state and 'player1_life' in game_state and 'player2_life' in game_state:
                        active_string = game_state['word']
                        life = game_state['player1_life']
                        life2 = game_state['player2_life']
                    else:
                        print("Received dictionary does not contain expected keys")
                else:
                    print("Received data is not a dictionary")
            except pickle.UnpicklingError as e:
                print(f"Error unpickling data: {e}")

        except ConnectionResetError as e:
            print(f"Connection was reset by the server: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

def send_data():
    game_state = {
        'word': active_string,
        'player1_life': life,
        'player2_life': life2
    }
    try:
        client.send(pickle.dumps(game_state))
    except Exception as e:
        print(f"Error sending data: {e}")

def update_words():
    global active_string
    active_string = random.choice(words_list)
    send_data()

def check_input():
    global input_text_p1, input_text_p2, active_string, life, life2, p1_fire, p2_fire

    # Convert the active string and input texts to lowercase for case-insensitive comparison
    active_string_lower = active_string.lower()
    input_text_p1_lower = input_text_p1.lower()
    input_text_p2_lower = input_text_p2.lower()

    if input_text_p1_lower == active_string_lower:
        life2 -= 10  # Decrease player 2's life
        life2 = max(life2, 0)
        input_text_p1 = ""
        update_words()
        p1_fire = True  # Trigger player 1 firing animation
    elif input_text_p2_lower == active_string_lower:
        life -= 10  # Decrease player 1's life
        life = max(life, 0)
        input_text_p2 = ""
        update_words()
        p2_fire = True  # Trigger player 2 firing animation
    else:
        p1_fire = False
        p2_fire = False

    send_data()

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



WIDTH = 1400
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Wordsprint Showdown!')
timer = pygame.time.Clock()
fps = 30

# Load images
Background = pygame.image.load('bg.png')
textbox = pygame.image.load('Main_textbox.png')
char1 = pygame.image.load('tank1.png')
char2 = pygame.image.load('char2.png')
p1text = pygame.image.load('textbox1.png')
p2text = pygame.image.load('textbox2.png')
p1Fire = pygame.image.load('Tank_Fire1.png')
p2Fire = pygame.image.load('Tank_Fire.png')
p1Shell = pygame.image.load('Tank_Shells.png')
p2Shell = pygame.image.load('Tank_Shells2.png')

def animate_firing(player):
    """Animate the firing sequence for the specified player."""
    if player == 1:
        # Player 1 firing animation
        fire_size1 = pygame.transform.scale(p1Fire, (80, 80))
        screen.blit(fire_size1, (175, HEIGHT - 143))
        bullet1 = pygame.transform.scale(p1Shell, (80, 80))
        for alpha in range(255, 0, -15):  # Fade out effect
            bullet1.set_alpha(alpha)
            screen.blit(bullet1, (650, HEIGHT -135))
            pygame.draw.line(screen, 'grey', (220, HEIGHT -100),(680, HEIGHT - 100), 5)
            pygame.display.flip()
            pygame.time.delay(10)
        bullet1.set_alpha(255)  # Reset alpha value
    elif player == 2:
        # Player 2 firing animation
        fire_size2 = pygame.transform.scale(p2Fire, (80, 80))
        screen.blit(fire_size2, (1135, HEIGHT - 143))
        bullet2 = pygame.transform.scale(p2Shell, (80, 80))
        for alpha in range(255, 0, -15):  # Fade out effect
            bullet2.set_alpha(alpha)
            screen.blit(bullet2, (700, HEIGHT -135))
            pygame.draw.line(screen, 'grey', (750, HEIGHT - 100), (1180, HEIGHT - 100), 5)
            pygame.display.flip()
            pygame.time.delay(10)
        bullet2.set_alpha(255)  # Reset alpha value
    pygame.display.flip()

def player_1():
    tsize1 = pygame.transform.scale(char1, (160, 100))
    screen.blit(tsize1, (50, HEIGHT - 140))

def p1_textbox():
    text1size1 = pygame.transform.scale(p1text, (300, 70))
    screen.blit(text1size1, (50, 550))

def player_2():
    tsize2 = pygame.transform.scale(char2, (160, 100))
    screen.blit(tsize2, (1180, HEIGHT - 140))

def p2_textbox():
    text2size1 = pygame.transform.scale(p2text, (300, 70))
    screen.blit(text2size1, (1040, 550))

def Background_sky():
    size = pygame.transform.scale(Background, (WIDTH, HEIGHT))
    screen.blit(size, (0, 0))

def word_box(word, x, y, padding):
    text_surface = font.render(word, True, 'grey')
    text_width, text_height = text_surface.get_size()
    box_width = text_width + 2 * padding
    box_height = text_height + 2 * padding
    bgsize = pygame.transform.scale(textbox, (box_width, box_height))
    screen.blit(bgsize, (x, y))
    """pygame.draw.rect(screen, 'Black', (x, y, box_width, box_height), 2)"""
    text_rect = text_surface.get_rect(center=(x + box_width // 2, y + box_height // 2))
    screen.blit(text_surface, text_rect,)

def draw_screen():

    screen.blit(base_font.render(f'P1 Life: {life}', True, 'Black'), (50, 620))
    screen.blit(base_font.render(f'P2 Life: {life2}', True, 'Black'), (1145, 620))

def countdown():
    global active_string
    countdown_font = pygame.font.Font(None, 100)
    countdown_start_time = time.time()
    countdown_duration = 3
    while time.time() - countdown_start_time < countdown_duration:
        screen.fill((0, 0, 0))
        remaining_time = countdown_duration - int(time.time() - countdown_start_time)
        countdown_surface = countdown_font.render(f'Game Start in {remaining_time}', True, 'White')
        countdown_rect = countdown_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(countdown_surface, countdown_rect)
        pygame.display.flip()
        timer.tick(1)
    update_words()

# Start the receive_data thread
thread = threading.Thread(target=receive_data, daemon=True)
thread.start()

# Display countdown before starting the game
countdown()

p1_fire = False
p2_fire = False

run = True
while run:
    timer.tick(fps)
    Background_sky()
    draw_screen()
    player_1()
    player_2()
    p1_textbox()
    p2_textbox()
    word_box(active_string, 600, 50, 20)

    if p1_fire:
        animate_firing(1)
        p1_fire = False

    if p2_fire:
        animate_firing(2)
        p2_fire = False

    # Draw text input for player 1
    txt_surface_p1 = base_font.render(input_text_p1, True, 'black')
    screen.blit(txt_surface_p1, (input_rect_p1.x + 20, input_rect_p1.y + 13))
    #pygame.draw.rect(screen, 'black', input_rect_p1, 2)

    # Draw text input for player 2
    txt_surface_p2 = base_font.render(input_text_p2, True, 'black')
    screen.blit(txt_surface_p2, (input_rect_p2.x + 20, input_rect_p2.y + 13))
    #pygame.draw.rect(screen, 'black', input_rect_p2, 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if input_active_p1:
                    input_text_p1 = input_text_p1[:-1]
                elif input_active_p2:
                    input_text_p2 = input_text_p2[:-1]
            elif event.key == pygame.K_RETURN:
                check_input()
                if input_active_p1:
                    input_text_p1 = ""
                elif input_active_p2:
                    input_text_p2 = ""
            elif event.key == pygame.K_TAB:
                input_active_p1 = not input_active_p1
                input_active_p2 = not input_active_p2
            elif event.key == pygame.K_LEFT:
                input_active_p1 = True
                input_active_p2 = False
            elif event.key == pygame.K_RIGHT:
                input_active_p1 = False
                input_active_p2 = True
            else:
                if input_active_p1:
                    input_text_p1 += event.unicode
                elif input_active_p2:
                    input_text_p2 += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if input_rect_p1.collidepoint(event.pos):
                input_active_p1 = True
                input_active_p2 = False
            elif input_rect_p2.collidepoint(event.pos):
                input_active_p2 = True
                input_active_p1 = False
            else:
                input_active_p1 = False
                input_active_p2 = False

    pygame.display.flip()

pygame.quit()
client.close()
