import pygame
import random
import time
import os

# Pygame initialization
pygame.init()
pygame.display.init()  # Explicitly initialize the display module

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping-pong Game")

# Hello message from pygame community
print("Hello from the pygame community. https://www.pygame.org/contribute.html")

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Paddle class definition
class Paddle:
    def __init__(self, x, y, width, height, color, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = speed
        self.score = 0

    def move(self, dy):
        self.rect.y += dy * self.speed
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

# Ball class definition
class Ball:
    def __init__(self, x, y, size, speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.dx = speed
        self.dy = speed
        self.base_speed = speed
        self.rally_count = 0

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.dx = random.choice([-1, 1]) * self.base_speed
        self.dy = random.choice([-1, 1]) * self.base_speed
        self.rally_count = 0

    def increase_speed(self):
        self.rally_count += 1
        speed_increase = min(self.rally_count * 0.1, 5)  # Max speed increase of 5
        self.dx = (abs(self.dx) + speed_increase) * (1 if self.dx > 0 else -1)
        self.dy = (abs(self.dy) + speed_increase) * (1 if self.dy > 0 else -1)

# Button class definition
class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Game object creation
player = Paddle(50, HEIGHT // 2 - 50, 10, 100, GREEN, 6)
opponent = Paddle(WIDTH - 60, HEIGHT // 2 - 50, 10, 100, RED, 5)
interfering_paddle = Paddle(100, HEIGHT // 2 - 50, 10, 100, BLUE, 7)
ball = Ball(WIDTH // 2 - 15, HEIGHT // 2 - 15, 30, 5)
start_button = Button(WIDTH // 2 - 50, HEIGHT // 2 - 25, 100, 50, "Start", GREEN, WHITE)
restart_button = Button(WIDTH // 2 - 50, HEIGHT // 2 + 100, 100, 50, "Restart", GREEN, WHITE)

# Game variable initialization
interfering_paddle_active = False
interference_timer = 0
interference_duration = 0
game_started = False
game_over = False
point_loss_timer = 0
point_loss_message = ""

# Font setup
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)

# Function to reset the game
def reset_game():
    global player, opponent, interfering_paddle, ball, interfering_paddle_active, interference_timer, interference_duration, game_over, point_loss_timer, point_loss_message
    player.score = 0
    opponent.score = 0
    player.rect.centery = HEIGHT // 2
    opponent.rect.centery = HEIGHT // 2
    interfering_paddle.rect.centery = HEIGHT // 2
    ball.reset()
    interfering_paddle_active = False
    interference_timer = 0
    interference_duration = 0
    game_over = False
    point_loss_timer = 0
    point_loss_message = ""

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not game_started and start_button.is_clicked(event.pos):
                game_started = True
                reset_game()
            elif game_over and restart_button.is_clicked(event.pos):
                reset_game()
                game_started = True
                game_over = False

    if game_started and not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.move(-1)
        if keys[pygame.K_s]:
            player.move(1)

        # AI opponent movement with occasional mistakes
        if random.random() < 0.90:  # 90% chance to move correctly
            if ball.rect.centery < opponent.rect.centery:
                opponent.move(-1)
            elif ball.rect.centery > opponent.rect.centery:
                opponent.move(1)
        else:  # 10% chance to move in the wrong direction
            if ball.rect.centery < opponent.rect.centery:
                opponent.move(1)
            elif ball.rect.centery > opponent.rect.centery:
                opponent.move(-1)

        # Interfering paddle activation/deactivation logic
        if not interfering_paddle_active:
            interference_timer += 1
            if interference_timer >= random.randint(300, 600):  # Activate randomly between 5-10 seconds
                interfering_paddle_active = True
                interference_duration = random.randint(180, 300)  # Active for 3-5 seconds
                interference_timer = 0
        else:
            interference_duration -= 1
            if interference_duration <= 0:
                interfering_paddle_active = False

        # Interfering paddle movement
        if interfering_paddle_active:
            if ball.rect.centery < interfering_paddle.rect.centery:
                interfering_paddle.move(-1)
            elif ball.rect.centery > interfering_paddle.rect.centery:
                interfering_paddle.move(1)

        # Ball movement
        ball.move()

        # Collision detection
        if interfering_paddle_active and ball.rect.colliderect(interfering_paddle.rect):
            ball.dx *= -1
            ball.increase_speed()
        elif ball.rect.colliderect(player.rect) or ball.rect.colliderect(opponent.rect):
            ball.dx *= -1
            ball.increase_speed()

        # Scoring and reset
        if ball.rect.left <= 0:
            opponent.score += 1
            point_loss_message = "Point Lost!"
            point_loss_timer = time.time()
            ball.reset()
        elif ball.rect.right >= WIDTH:
            player.score += 1
            point_loss_message = "Point Scored!"
            point_loss_timer = time.time()
            ball.reset()

        # Game over condition
        if player.score >= 5 or opponent.score >= 5:
            game_over = True

    # Screen drawing
    screen.fill(BLACK)
    
    if game_started and not game_over:
        player.draw()
        opponent.draw()
        if interfering_paddle_active:
            interfering_paddle.draw()
        ball.draw()

        # Draw scores
        player_score_text = font.render(str(player.score), True, WHITE)
        opponent_score_text = font.render(str(opponent.score), True, WHITE)
        screen.blit(player_score_text, (WIDTH // 4, 20))
        screen.blit(opponent_score_text, (3 * WIDTH // 4, 20))

        # Draw point loss/gain message
        if time.time() - point_loss_timer < 1:
            message_text = font.render(point_loss_message, True, RED)
            screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2))

    elif game_over:
        game_over_text = large_font.render("GAME OVER!", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))

        final_score_text = large_font.render(f"{player.score} - {opponent.score}", True, WHITE)
        screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2 - 50))

        result_text = large_font.render("You Win!" if player.score > opponent.score else "You Lose!", True, GREEN if player.score > opponent.score else RED)
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 + 50))

        restart_button.draw()
    else:
        # Start screen
        title_text = large_font.render("Ping-pong Game", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
        
        start_button.draw()
        
        # Controls information
        controls_text = font.render("Controls: W (up), S (down)", True, WHITE)
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, HEIGHT // 2 + 50))
        
        # 5 point rule
        rule_text = font.render("First to score 5 points wins!", True, WHITE)
        screen.blit(rule_text, (WIDTH // 2 - rule_text.get_width() // 2, HEIGHT // 2 + 100))
        
        # Developer info
        dev_info = small_font.render("2024 Y. Seong", True, GRAY)
        screen.blit(dev_info, (WIDTH - dev_info.get_width() - 10, HEIGHT - dev_info.get_height() - 10))

    # Screen update
    pygame.display.flip()
    clock.tick(60)

# Pygame termination
pygame.quit()