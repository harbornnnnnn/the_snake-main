"""Игра «Змейка» (Изгиб Питона) на pygame с ООП."""

from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки (FPS):
SPEED = 8  # Уменьшил скорость для более комфортной игры

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self,
                 position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                 body_color=None):
        """Инициализирует позицию и цвет объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Шаблон метода отрисовки (переопределяется в наследниках)."""
        pass


class Apple(GameObject):
    """Яблоко, появляющееся в случайной свободной клетке."""

    def __init__(self):
        """Создаёт яблоко и задаёт стартовую позицию."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, occupied=None):
        """Ставит яблоко в случайную клетку, не занятую змейкой."""
        occupied = set(occupied) if occupied is not None else set()

        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            pos = (x, y)
            if pos not in occupied:
                self.position = pos
                return

    def draw(self):
        """Отрисовывает яблоко."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка: движение, рост, самоукус, сброс."""

    def __init__(self):
        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(position=center, body_color=SNAKE_COLOR)

        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применяет next_direction, если оно задано."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        # Проверка на столкновение с самой собой
        if new_head in self.positions[1:]:  # Исключаем голову из проверки
            self.reset()
            return

        self.positions.insert(0, new_head)

        # Удаляем хвост только если змейка не выросла
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        # Отрисовка тела змейки (все сегменты кроме головы)
        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Стираем последний удалённый сегмент
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def grow(self):
        """Увеличивает длину змейки на 1."""
        self.length += 1
        # Не удаляем хвост в следующем ходе

    def reset(self):
        """Сбрасывает змейку в начальное состояние после самоукуса."""
        self.length = 1
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.direction = RIGHT  # Начинаем всегда с движения вправо
        self.next_direction = None
        self.last = None
        print("Сброс! Начинаем заново.")


def handle_keys(game_object):
    """Обрабатывает управление стрелками и закрытие окна."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Запускает игру и содержит основной игровой цикл."""
    pygame.init()

    # Инициализация объектов
    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    print("Игра началась! Управление стрелками. Нажмите Esc для выхода.")

    while True:
        clock.tick(SPEED)  # Управление скоростью игры

        # Обработка событий
        handle_keys(snake)

        # Обновление направления
        snake.update_direction()

        # Движение змейки
        snake.move()

        # Очистка экрана
        screen.fill(BOARD_BACKGROUND_COLOR)

        # Проверка столкновения с яблоком
        if snake.get_head_position() == apple.position:
            snake.grow()  # Увеличиваем длину змейки
            apple.randomize_position(snake.positions)  # Новое яблоко
            print(f"Съедено яблоко! Длина змейки: {snake.length}")

        # Проверка, не появилось ли яблоко на змейке
        if apple.position in snake.positions:
            apple.randomize_position(snake.positions)

        # Отрисовка
        apple.draw()
        snake.draw()

        # Обновление экрана
        pygame.display.update()


if __name__ == "__main__":
    main()
