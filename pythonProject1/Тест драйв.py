import pygame
import sys
import random

pygame.init()

enemy_image1 = pygame.image.load('2.jpg')
enemy_image2 = pygame.image.load('3.jpg')
enemy_skipped_turn = False
enemy_stunned = False
defence_cooldown = 0
defence_limit = 2  # Максимальное количество последовательных защит
defence_penalty = 5  # Урон от усталости при защите


# Устанавливаем размеры окна
window_width = 1000
window_height = 800
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("RussiaGame")

# Устанавливаем цвет объекта и его начальные координаты
object_size = 75
object_x = window_width // 2
object_y = window_height // 2

player_image = pygame.image.load('man.jpg')
player_image = pygame.transform.scale(player_image, (object_size, object_size))

# Начальные показатели здоровья и брони персонажа
player_health = 100
player_armor = 50
player_damage = 10

# Шрифт для отображения характеристик
font = pygame.font.SysFont(None, 24)
game_over_font = pygame.font.SysFont('arial', 90)  # Большой шрифт для сообщения о проигрыше

# Создаем список для хранения координат противников и их характеристик
enemies = []

# Состояние боя
in_battle = False
current_enemy = None
player_turn = True

# Кнопки действий
buttons = {
    'attack': pygame.Rect(50, 500, 100, 50),
    'defend': pygame.Rect(200, 500, 100, 50)
}

# Функция для отрисовки кнопок
def draw_buttons():
    for action, rect in buttons.items():
        pygame.draw.rect(window, (0, 0, 0), rect)
        text = font.render(action.capitalize(), True, (255, 255, 255))
        window.blit(text, rect.move(10, 10))

def show_game_over_screen():
    window.fill((0, 0, 0))  # Заливаем экран черным цветом
    game_over_text = game_over_font.render('YOU DIED', True, (255, 0, 0))
    text_rect = game_over_text.get_rect()
    text_rect.center = (window_width // 2, window_height // 2)
    window.blit(game_over_text, text_rect)
    pygame.display.flip()  # Обновляем экран, чтобы отобразить сообщение
    pygame.time.wait(5000)  # Пауза перед закрытием игры

# Функция для обработки клика по кнопке
def handle_button_click(mouse_pos):
    for action, rect in buttons.items():
        if rect.collidepoint(mouse_pos):
            return action
    return None

# Функция для создания нового противника в случайном месте на экране
enemy_health = 50
enemy_armor = 20
enemy_damage = 5
def create_enemy():
    enemy_size = 100
    collision = True
    while collision:  # Повторяем попытки создания противника, пока не найдем свободное место
        enemy_x = random.randint(0, window_width - enemy_size)
        enemy_y = random.randint(0, window_height - enemy_size)
        collision = False
        for enemy in enemies:
            if check_collision((enemy_x, enemy_y), enemy):
                collision = True  # Если обнаружено пересечение, пробуем снова
                break

    enemy_image = random.choice([enemy_image1, enemy_image2])
    enemy_image = pygame.transform.scale(enemy_image, (enemy_size, enemy_size))
    enemies.append({'position': (enemy_x, enemy_y), 'health': enemy_health, 'armor': enemy_armor, 'damage': enemy_damage, 'size': enemy_size, 'image': enemy_image})


# Функция для проверки столкновения
def check_collision(player_pos, enemy):
    player_x, player_y = player_pos
    enemy_x, enemy_y = enemy['position']
    size = enemy['size']
    return (player_x < enemy_x + size and player_x + size > enemy_x and
            player_y < enemy_y + size and player_y + size > enemy_y)


def battle_action(player_action, enemy_action):
    global player_health, current_enemy, player_damage, enemy_damage, enemy_stunned, defence_cooldown, defence_limit, enemy_skipped_turn
    stun_chance = 0.25  # Шанс оглушения противника

    # Вывод действий противника
    print(f"Действие противника: {enemy_action}")

    if player_action == 'defend' and enemy_action == 'attack':
        if defence_cooldown < defence_limit:
            defence_cooldown += 1
        else:
            player_health -= defence_penalty  # Накладываем штраф за усталость
            print("Вы устали от защиты и получаете урон!")
        if random.random() < stun_chance:
            enemy_stunned = True
            print("Противник оглушен!")
        return False

    if enemy_stunned:
        current_enemy['health'] -= player_damage * 2  # Удвоенный урон, если противник оглушен и не защищается
        print("Противник оглушен и получает удвоенный урон!")
        enemy_stunned = False
        enemy_skipped_turn = True  # Противник пропускает следующий ход
    elif player_action == 'attack' and enemy_action != 'defend':
        current_enemy['health'] -= player_damage  # Наносим урон только если противник не защищается
        print("Вы атакуете и наносите урон противнику!")
        defence_cooldown = 0
    elif player_action == 'attack' and enemy_action == 'defend':
        defence_cooldown = 0

    if enemy_action == 'attack' and player_action != 'defend':
        if not enemy_skipped_turn:
            player_health -= enemy_damage  # Наносим урон игроку, если он не защищается
            print("Противник атакует и наносит вам урон!")

    if player_action == 'defend':
        if defence_cooldown < defence_limit:
            defence_cooldown += 1
        else:
            player_health -= defence_penalty  # Накладываем штраф за усталость
            print("Вы устали от защиты и получаете урон!")

    # Проверяем, закончился ли бой
    if current_enemy['health'] <= 0:
        return True  # Бой закончен, игрок победил
    elif player_health <= 0:
        show_game_over_screen()  # Показываем экран проигрыша
        pygame.quit()
        sys.exit()  # Завершаем игру, если здоровье игрока <= 0
    return False  # Бой продолжается


# Основной игровой цикл
player_defended_last_turn = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and in_battle and player_turn:
            mouse_pos = event.pos
            player_action = handle_button_click(mouse_pos)
            enemy_action = random.choice(['attack', 'defend'])
            if player_action:
                player_defended_last_turn = (player_action == 'defend')
                battle_over = battle_action(player_action, enemy_action)
                if battle_over:
                    in_battle = False
                    if current_enemy['health'] <= 0:
                        enemies.remove(current_enemy)
                    current_enemy = None
                    player_turn = True  # Сброс хода для следующего боя

    keys = pygame.key.get_pressed()
    if not in_battle:
        if keys[pygame.K_LEFT]:
            object_x -= 0.1
        if keys[pygame.K_RIGHT]:
            object_x += 0.1
        if keys[pygame.K_UP]:
            object_y -= 0.1
        if keys[pygame.K_DOWN]:
            object_y += 0.1

        # Проверяем, чтобы объект не выходил за границы окна
        object_x = max(0, min(window_width - object_size, object_x))
        object_y = max(0, min(window_height - object_size, object_y))

        # Проверяем столкновения
        for enemy in enemies:
            if check_collision((object_x, object_y), enemy):
                in_battle = True
                current_enemy = enemy
                player_turn = True  # Игрок начинает первым
                break

        # Создаем нового противника с вероятностью 1%
    if random.random() < 0.01 and len(enemies) < 3:
        create_enemy()

        # Если в бою, обрабатываем действия игрока и противника
    if in_battle and not player_turn:
        if not enemy_stunned and not enemy_skipped_turn:  # Добавляем проверку, не пропускает ли противник ход
            enemy_action = random.choice(['attack', 'defend'])
            print(f"Противник выбирает действие: {enemy_action}")  # Выводим выбранное действие противника
            player_action = 'defend' if player_defended_last_turn else 'attack'
            battle_over = battle_action(player_action, enemy_action)
        else:
            print("Противник пропускает ход")
            enemy_skipped_turn = False  # Сбрасываем флаг пропуска хода
        if battle_over:
            in_battle = False
            if current_enemy['health'] <= 0:
                enemies.remove(current_enemy)
            current_enemy = None
            player_turn = True  # Сброс хода для следующего боя

    window.fill((255, 255, 255))  # Заливаем окно белым цветом

    # Рисуем объект игрока
    window.blit(player_image, (object_x, object_y))


    # Рисуем противников
    for enemy in enemies:
        enemy_position = enemy['position']
        enemy_image = enemy['image']  # Получаем изображение противника
        window.blit(enemy_image, enemy_position)

    # Отображаем характеристики персонажа
    stats_text = f"Здоровье: {player_health} Защита: {player_armor} Урон: {player_damage}"
    text = font.render(stats_text, True, (0, 0, 0))
    window.blit(text, (5, window_height - 30))  # Размещаем текст в нижнем левом углу

    # Если в бою, отображаем характеристики противника
    if in_battle:
        enemy_stats = f"Здоровье: {current_enemy['health']} Защита: {current_enemy['armor']} Урон: {current_enemy['damage']}"
        enemy_text = font.render(enemy_stats, True, (0, 0, 0))
        window.blit(enemy_text, (window_width - 200, window_height - 30))  # Размещаем текст в нижнем правом углу

    # Если в бою, отображаем кнопки действий
    if in_battle:
        draw_buttons()

    pygame.display.update()