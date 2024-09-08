import pygame
import random

# Initialisiere Pygame
pygame.init()

# Spieleinstellungen
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 550
GROUND_HEIGHT = 100
BIRD_WIDTH = 70
BIRD_HEIGHT = 70
PIPE_WIDTH = 70
PIPE_HEIGHT = 500
PIPE_GAP = 200
GRAVITY = 0.5
FLAP_STRENGTH = -5  # Verringert, um weniger empfindlich zu sein
BASE_PIPE_SPEED = 5
SPEED_INCREASE_FACTOR = 1.25

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Bildschirm einrichten
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Rocket")

# Bilder laden
background_img = pygame.image.load("background.png")
rocket_img = pygame.image.load("rocket.png")
rocket_img = pygame.transform.scale(rocket_img, (BIRD_WIDTH, BIRD_HEIGHT))
meteor_img = pygame.image.load("meteor.png")
meteor_img = pygame.transform.scale(meteor_img, (PIPE_WIDTH, PIPE_HEIGHT))

# Soundeffekte laden
score_sound = pygame.mixer.Sound("score.mp3")
hit_sound = pygame.mixer.Sound("hit.mp3")

# Schriftart laden
font = pygame.font.SysFont(None, 48)

# Highscores laden und speichern
HIGHSCORE_FILE = "highscores.txt"

def load_highscores():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            highscores = [int(line.strip()) for line in f.readlines()]
    except FileNotFoundError:
        highscores = []
    return highscores

def save_highscore(score):
    highscores = load_highscores()
    highscores.append(score)
    highscores = sorted(highscores, reverse=True)[:5]  # Nur die Top 5 Scores speichern
    with open(HIGHSCORE_FILE, "w") as f:
        for hs in highscores:
            f.write(f"{hs}\n")

def display_highscores(screen, highscores):
    # Hintergrundbild anzeigen
    screen.blit(background_img, (0, 0))

    # Bestenliste anzeigen
    title_text = font.render("Bestenliste", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    for i, score in enumerate(highscores):
        score_text = font.render(f"{i + 1}. {score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 150 + i * 50))

    pygame.display.update()

# Raketenklasse
class Rocket:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.image = rocket_img
        self.rect = self.image.get_rect()

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Hindernisklasse
class Meteor:
    def __init__(self, x, speed):
        self.x = x
        self.height = random.randint(100, 400)
        self.top_meteor = meteor_img
        self.bottom_meteor = meteor_img
        self.top_rect = self.top_meteor.get_rect(midbottom=(self.x, self.height - PIPE_GAP // 2))
        self.bottom_rect = self.bottom_meteor.get_rect(midtop=(self.x, self.height + PIPE_GAP // 2))
        self.passed = False
        self.speed = speed

    def update(self):
        self.x -= self.speed
        self.top_rect.topleft = (self.x, self.height - PIPE_GAP // 2 - PIPE_HEIGHT)
        self.bottom_rect.topleft = (self.x, self.height + PIPE_GAP // 2)

    def draw(self, screen):
        screen.blit(self.top_meteor, self.top_rect.topleft)
        screen.blit(self.bottom_meteor, self.bottom_rect.topleft)

# Hauptmenü
def main_menu():
    menu_font = pygame.font.SysFont(None, 72)
    run_menu = True

    while run_menu:
        # Hintergrundbild anzeigen
        screen.blit(background_img, (0, 0))

        title_text = menu_font.render("Flappy Rocket", True, WHITE)
        start_text = font.render("Drücke ENTER zum Starten", True, WHITE)
        quit_text = font.render("Drücke ESC zum Beenden", True, WHITE)

        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 400))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_menu = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter gedrückt, Spiel starten
                    return True
                if event.key == pygame.K_ESCAPE:  # Escape gedrückt, Spiel beenden
                    run_menu = False
                    return False

# Hauptspielfunktion
def main():
    clock = pygame.time.Clock()
    rocket = Rocket()
    speed = BASE_PIPE_SPEED
    meteors = [Meteor(SCREEN_WIDTH + i * 300, speed) for i in range(3)]
    score = 0
    running = True
    has_passed_first_meteor = False  # Neue Variable zum Verfolgen, ob ein Hindernis passiert wurde

    while running:
        screen.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                rocket.flap()

        rocket.update()

        for meteor in meteors:
            meteor.update()
            if meteor.x + PIPE_WIDTH < 0:
                meteors.remove(meteor)
                meteors.append(Meteor(SCREEN_WIDTH + 300, speed))

            if not meteor.passed and meteor.x < rocket.x:
                meteor.passed = True
                score += 1
                score_sound.play()  # Score-Sound abspielen
                has_passed_first_meteor = True  # Markiere, dass das erste Hindernis passiert wurde
                if score == 20 or score == 40:
                    speed *= SPEED_INCREASE_FACTOR
                    for m in meteors:
                        m.speed = speed

            if rocket.rect.colliderect(meteor.top_rect) or rocket.rect.colliderect(meteor.bottom_rect):
                hit_sound.play()  # Hit-Sound abspielen
                running = False

        # Überprüfen, ob die Rakete außerhalb des Bildschirms fällt, bevor das erste Hindernis passiert wurde
        if rocket.y >= SCREEN_HEIGHT and not has_passed_first_meteor:
            hit_sound.play()  # Hit-Sound abspielen
            running = False

        rocket.draw(screen)
        for meteor in meteors:
            meteor.draw(screen)

        # Punktestand anzeigen
        score_text = font.render(str(score), True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2, 50))

        pygame.display.update()
        clock.tick(30)

    # Highscore speichern und Bestenliste anzeigen
    save_highscore(score)
    highscores = load_highscores()
    display_highscores(screen, highscores)

    # Warte auf Eingabe der Enter-Taste zum Neustarten oder Beenden
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False
                return True

# Hauptschleife mit Menü
while True:
    if not main_menu():  # Hauptmenü anzeigen
        break
    if not main():  # Spiel starten
        break

pygame.quit()
