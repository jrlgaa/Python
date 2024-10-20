import pygame
import socket
import threading
import pickle
import random
import time
from pygame.sprite import Group

def get_local_ip():
    try:
        # Connect to an external server to find out the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))  # Connect to Google's DNS server to determine local IP
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"Error determining local IP address: {e}")
        # Fallback to local IP from hostname
        local_ip = socket.gethostbyname(socket.gethostname())
        if local_ip.startswith("127."):
            local_ip = "192.168.1.19"  # Last fallback
    return local_ip

# Get local IP dynamically
SERVER_IP = get_local_ip()
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

#tank animation
class TankAnimation(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = [pygame.image.load(f'tankfire{i}.png') for i in range(1, 12)]
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.image = pygame.transform.scale(self.image, (160, 100))
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        self.animation_finished = False

    def update(self):
        if not self.animation_finished:
            self.current_sprite += 1
            if self.current_sprite >= len(self.sprites):
                self.animation_finished = True
                self.kill()
            else:
                self.image = pygame.transform.scale(self.sprites[self.current_sprite], (160, 100))

class TankAnimation2(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = [pygame.image.load(f'p2tankfire{i}.png') for i in range(1, 12)]
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.image = pygame.transform.scale(self.image, (160, 100))
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        self.animation_finished = False

    def update(self):
        if not self.animation_finished:
            self.current_sprite += 1
            if self.current_sprite >= len(self.sprites):
                self.animation_finished = True
                self.kill()
            else:
                self.image = self.sprites[self.current_sprite]
                self.image = pygame.transform.scale(self.sprites[self.current_sprite], (160, 100))

#fire animation
class Fire(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = [pygame.image.load(f'p1_{i}.png') for i in range(1, 11)]
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        self.animation_finished = False

    def update(self):
        if not self.animation_finished:
            self.current_sprite += 1
            if self.current_sprite >= len(self.sprites):
                self.animation_finished = True
                self.kill()
            else:
                self.image = self.sprites[self.current_sprite]

class Fire2(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = [pygame.image.load(f'p2_{i}.png') for i in range(1, 11)]
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        self.animation_finished = False

    def update(self):
        if not self.animation_finished:
            self.current_sprite += 1
            if self.current_sprite >= len(self.sprites):
                self.animation_finished = True
                self.kill()
            else:
                self.image = self.sprites[self.current_sprite]

#Explosion sprite
class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = [pygame.image.load(f'Nuclear_explosion{i}.png') for i in range(1, 11)]
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        self.animation_finished = False

    def update(self):
        if not self.animation_finished:
            self.current_sprite += 1
            if self.current_sprite >= len(self.sprites):
                self.animation_finished = True
                self.kill()
            else:
                self.image = self.sprites[self.current_sprite]

# Initialize Pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load('bg music.wav')
pygame.mixer.music.play(loops=-1)
sound_effect = pygame.mixer.Sound('Fire_sound.wav')

# Game variables
active_string = "Game Start"
life = 10
life2 = 10
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
        sound_effect.play(loops=0)
    elif input_text_p2_lower == active_string_lower:
        life -= 10  # Decrease player 1's life
        life = max(life, 0)
        input_text_p2 = ""
        update_words()
        p2_fire = True  # Trigger player 2 firing animation
        sound_effect.play(loops=0)
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
fps = 60

# Main menu
opponents = ["Player 1", "Player 2"]

# Menu function to display the Play button
def draw_menu():
    screen.fill((0, 0, 0))  # Black background

    # Draw title
    title_text = font.render("WordSprint Showdown", True, 'White')
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(title_text, title_rect)

    # Draw play button
    play_button_text = font.render("Play", True, 'White')
    play_button_rect = play_button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    pygame.draw.rect(screen, 'Grey', play_button_rect.inflate(20, 10))  # Button background
    screen.blit(play_button_text, play_button_rect)

    pygame.display.flip()
    return play_button_rect

def main_menu():
    menu_active = True
    while menu_active:
        play_button_rect = draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    menu_active = False  # Exit the menu loop and go to lobby

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Start game if ENTER is pressed
                    menu_active = False

        timer.tick(fps)

# Lobby function to display available opponents
def draw_lobby():
    screen.fill((0, 0, 0))  # Black background

    # Draw title
    title_text = font.render("Choose Side", True, 'White')
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
    screen.blit(title_text, title_rect)

    # Draw opponent buttons
    button_rects = []
    for idx, opponent in enumerate(opponents):
        opponent_text = font.render(opponent, True, 'White')
        opponent_rect = opponent_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + (idx * 80)))
        pygame.draw.rect(screen, 'Grey', opponent_rect.inflate(20, 10))  # Button background
        screen.blit(opponent_text, opponent_rect)
        button_rects.append(opponent_rect)

    pygame.display.flip()
    return button_rects

# Lobby function with server interaction for player choice
def lobby():
    global input_active_p1, input_active_p2  # Add these to modify input states
    lobby_active = True
    while lobby_active:
        button_rects = draw_lobby()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for idx, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        selected_opponent = opponents[idx]
                        print(f"Opponent selected: {selected_opponent}")

                        # Automatically set the input state based on the selected player
                        if selected_opponent == "Player 1":
                            input_active_p1 = True
                            input_active_p2 = False
                        elif selected_opponent == "Player 2":
                            input_active_p1 = False
                            input_active_p2 = True

                        lobby_active = False  # Exit the lobby loop and start the game
                        break

        timer.tick(fps)


# Call the main_menu function before the game starts
main_menu()

# After main menu, show the lobby
lobby()


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

#moving background
class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprites = [pygame.image.load(f'tile00{i}.png') for i in range(1, 8)]
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        # Scale the background image to fit the screen
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.rect = self.image.get_rect(topleft=(0, 0))

        # Timer variables
        self.last_update_time = pygame.time.get_ticks()
        self.update_interval = 75

    def update(self):
        # Check if enough time has passed to change the sprite
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.update_interval:
            self.current_sprite += 1
            if self.current_sprite >= len(self.sprites):
                self.current_sprite = 0

            # Update the image and reset the timer
            self.image = pygame.transform.scale(self.sprites[self.current_sprite], (WIDTH, HEIGHT))
            self.last_update_time = current_time

# Initialize background sprite
background_sprite = Background()

background_group = pygame.sprite.Group()
background_group.add(background_sprite)

#grouped tank animation
tank1_animations = Group()
tank2_animations = Group()

def animate_firing(player):
    global explosions, fire, fire2

    """Animate the firing sequence for the specified player."""
    if player == 1:
        # Player 1 firing animation
        tank1_animations.add(TankAnimation(133, HEIGHT - 90))
        fire.add(Fire(260, HEIGHT - 100))
        explosions.add(Explosion(1230, HEIGHT - 95))
        fire_size1 = pygame.transform.scale(p1Fire, (80, 80))
        screen.blit(fire_size1, (175, HEIGHT - 143))

    elif player == 2:
        # Player 2 firing animation
        tank2_animations.add(TankAnimation2(1258, HEIGHT - 90))
        fire2.add(Fire2(1135, HEIGHT - 100))
        explosions.add(Explosion(150, HEIGHT - 95))
        fire_size2 = pygame.transform.scale(p2Fire, (80, 80))
        screen.blit(fire_size2, (1135, HEIGHT - 143))
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

explosions = pygame.sprite.Group()
fire = pygame.sprite.Group()
fire2 = pygame.sprite.Group()


run = True

def display_winner(winner):
    screen.fill((0, 0, 0))  # Black background

    # Draw winning message
    win_text = font.render(f"{winner} Wins!", True, 'White')
    win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(win_text, win_rect)

    # Draw play again button
    play_again_text = font.render("Play Again", True, 'White')
    play_again_rect = play_again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    pygame.draw.rect(screen, 'Grey', play_again_rect.inflate(20, 10))  # Button background
    screen.blit(play_again_text, play_again_rect)

    # Draw exit button
    exit_text = font.render("Exit", True, 'White')
    exit_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
    pygame.draw.rect(screen, 'Grey', exit_rect.inflate(20, 10))  # Button background
    screen.blit(exit_text, exit_rect)

    pygame.display.flip()

    return play_again_rect, exit_rect

def check_winner():
    global life, life2, run
    if life == 0:
        return "Player 2"
    elif life2 == 0:
        return "Player 1"
    return None

while run:
    timer.tick(fps)
    # Update background
    background_sprite.update()

    winner = check_winner()
    if winner:
        play_again_rect, exit_rect = display_winner(winner)

        # Wait for the player's decision (play again or exit)
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    waiting_for_input = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_rect.collidepoint(event.pos):
                        # Reset game state to play again
                        life = 10
                        life2 = 10
                        active_string = random.choice(words_list)
                        p1_fire = False
                        p2_fire = False
                        waiting_for_input = False

                    elif exit_rect.collidepoint(event.pos):
                        run = False
                        waiting_for_input = False

    # Clear the screen
    screen.fill((0, 0, 0))  # Optional: fill with black before drawing

    # Draw the background
    background_group.draw(screen)

    #Background_sky()
    draw_screen()
    player_1()
    player_2()
    p1_textbox()
    p2_textbox()
    word_box(active_string, 600, 50, 20)

    fire.update()
    fire.draw(screen)

    fire2.update()
    fire2.draw(screen)

    explosions.update()
    explosions.draw(screen)

    tank1_animations.update()
    tank1_animations.draw(screen)

    tank2_animations.update()
    tank2_animations.draw(screen)

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
