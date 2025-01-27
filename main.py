import random
import os
import pygame
from pygame.constants import QUIT, K_w, K_a, K_s, K_d, K_SPACE

pygame.init()

# Константи
HEIGHT = 700
WIDTH = 1100

FONT = pygame.font.SysFont('Verdana', 20)

FPS = pygame.time.Clock()

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 222, 0)

IMAGE_PATH = "animation_goose"
PLAYER_IMAGES = os.listdir(IMAGE_PATH)

# Встановлення розміру екрану для відображення гри
display = pygame.display.set_mode((WIDTH, HEIGHT))

# Завантаження фону
background = pygame.transform.scale(pygame.image.load('image/background.png'), (WIDTH, HEIGHT))
background_X1 = 0
background_X2 = background.get_width()
background_move = 3

# Завантаження гравця
player = pygame.image.load('image/player.png').convert_alpha()
player_rect = player.get_rect()
player_rect.center = display.get_rect().center

# Напрями руху гравця
player_move_up = [0, -4]
player_move_down = [0, 4]
player_move_right = [4, 0]
player_move_left = [-4, 0]

# Завантаження і масштабування серця
heart_image = pygame.image.load('image/heart.png').convert_alpha()
HEART_WIDTH, HEART_HEIGHT = heart_image.get_width() // 6, heart_image.get_height() // 6
heart_image = pygame.transform.scale(heart_image, (HEART_WIDTH, HEART_HEIGHT))

# Функція для збереження найкращого результату в файл
def save_best_score(score):
    with open("best_score.txt", "w") as f:
        f.write(str(score))

# Функція для зчитування найкращого результату з файлу
def load_best_score():
    if os.path.exists("best_score.txt"):
        with open("best_score.txt", "r") as f:
            return int(f.read())
    else:
        return 0

# Створення ворога
def create_enemy():
    enemy = pygame.image.load('image/enemy.png').convert_alpha()
    enemy = pygame.transform.scale(enemy, (int(enemy.get_width() * 0.5), int(enemy.get_height() * 0.5)))
    enemy_rect = pygame.Rect(WIDTH, random.randint(enemy.get_height(), HEIGHT - enemy.get_height()), *enemy.get_size())
    enemy_move = [random.randint(-8, -4), 0]
    return [enemy, enemy_rect, enemy_move]

# Створення бонусу
def create_bonus():
    bonus = pygame.image.load('image/bonus.png').convert_alpha()
    bonus = pygame.transform.scale(bonus, (int(bonus.get_width() * 0.6), int(bonus.get_height() * 0.6)))
    bonus_width = bonus.get_width()
    bonus_rect = pygame.Rect(random.randint(bonus_width, WIDTH - bonus_width), -bonus.get_height(), *bonus.get_size())
    bonus_move = [0, random.randint(4, 8)]
    return [bonus, bonus_rect, bonus_move]

# Виведення екрану програшу
def show_game_over(best_score):
    game_over_text = FONT.render('Game Over! Press Space to Restart', True, COLOR_YELLOW)
    best_score_text = FONT.render(f"Best Score: {best_score}", True, COLOR_YELLOW)
    display.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 30))
    display.blit(best_score_text, (WIDTH // 2 - best_score_text.get_width() // 2, HEIGHT // 2 + 10))

# Виведення життів
def show_lives():
    for i in range(lives):
        display.blit(heart_image, (20 + i * (HEART_WIDTH + 10), 20))

# Створення ворогів кожні 1500 мс, бонусів кожні 3000 мс 
# та зміна зображення гравця кожні 200 мс
CREATE_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(CREATE_ENEMY, 1500)

CREATE_BONUS = pygame.USEREVENT + 2
pygame.time.set_timer(CREATE_BONUS, 3000)

CHANGE_IMAGE = pygame.USEREVENT + 3
pygame.time.set_timer(CHANGE_IMAGE, 200)

enemies = []
bonuses = []

score = 0
best_score = load_best_score() 
lives = 3
image_index = 0

playing = True
game_over = False

while playing:
    FPS.tick(240)

    for event in pygame.event.get():
        if event.type == QUIT:
            playing = False
        if event.type == CREATE_ENEMY:
            enemies.append(create_enemy())
        if event.type == CREATE_BONUS:
            bonuses.append(create_bonus())  
        if event.type == CHANGE_IMAGE:
            player = pygame.image.load(os.path.join(IMAGE_PATH, PLAYER_IMAGES[image_index]))
            image_index += 1
            if image_index >= len(PLAYER_IMAGES):
                image_index = 0

    if not game_over:
        background_X1 -= background_move
        background_X2 -= background_move

        if background_X1 < -background.get_width():
            background_X1 = background.get_width()

        if background_X2 < -background.get_width():
            background_X2 = background.get_width()

        display.blit(background, (background_X1, 0))
        display.blit(background, (background_X2, 0))

        # Отримання натиснутих клавіш
        keys = pygame.key.get_pressed()

        if keys[K_s] and player_rect.bottom < HEIGHT:
            player_rect = player_rect.move(player_move_down)

        if keys[K_d] and player_rect.right < WIDTH:
            player_rect = player_rect.move(player_move_right)    

        if keys[K_w] and player_rect.top > 0:
            player_rect = player_rect.move(player_move_up)   

        if keys[K_a] and player_rect.left > 0:
            player_rect = player_rect.move(player_move_left) 

        for enemy in enemies:
            enemy[1] = enemy[1].move(enemy[2])
            display.blit(enemy[0], enemy[1])

            if player_rect.colliderect(enemy[1]): # Перевірка на зіткнення з ворогом
                lives -= 1
                enemies.pop(enemies.index(enemy))
                if lives <= 0:
                    game_over = True

        for bonus in bonuses:
            bonus[1] = bonus[1].move(bonus[2])
            display.blit(bonus[0], bonus[1])

            if player_rect.colliderect(bonus[1]): # Перевірка на зіткнення з бонусом
                score += 1
                bonuses.pop(bonuses.index(bonus))

        score_text = FONT.render(f"Score: {score}", True, COLOR_BLACK)
        display.blit(score_text, (WIDTH - 125, 30))
        display.blit(player, player_rect)

        show_lives()

        pygame.display.flip()

        for enemy in enemies:
            if enemy[1].right < 0: # Видалення ворогів, що вийшли за межі екрану
                enemies.pop(enemies.index(enemy))

        for bonus in bonuses:
            if bonus[1].top > HEIGHT: # Видалення бонусів, що вийшли за межі екрану
                bonuses.pop(bonuses.index(bonus))
    else:
        if score > best_score:
            best_score = score
            save_best_score(best_score)
        show_game_over(best_score)
        pygame.display.flip()

        keys = pygame.key.get_pressed()
        if keys[K_SPACE]: # Перезапуск гри
            game_over = False
            score = 0
            lives = 3
            player_rect.center = display.get_rect().center
            enemies = []
            bonuses = []
