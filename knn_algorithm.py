import pygame
import math
import random
from collections import Counter

WIDTH, HEIGHT = 900, 700
GRID_SIZE = 5
TEMP_GRID_SIZE = 9
POINTS_PER_COLOR = 4
K = 3
MAX_COLORS = 6

WHITE = (243, 234, 214)
BLACK = (40, 41, 34)
TAN = (215, 203, 178)
BROWN = (73, 50, 34)

COLORS = [
    (133, 147, 143),
    (221, 178, 172),
    (225, 218, 174),
    (231, 209, 207),
    (62, 67, 67),
    (109, 102, 73)
]

LIGHTER_COLORS = [
    (180, 200, 195),
    (240, 200, 190),
    (240, 230, 190),
    (240, 220, 215),
    (120, 130, 130),
    (150, 140, 110)
]

num_colors = 3
points_per_color = POINTS_PER_COLOR
dragging = False

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("K-Nearest Neighbours Visualisation")
font = pygame.font.Font("MinecraftRegular-Bmg3.otf", 16) 
title_font = pygame.font.Font("MinecraftRegular-Bmg3.otf", 36)
menu_font = pygame.font.Font("MinecraftRegular-Bmg3.otf", 20)

def generate_points(existing_points=None):
    points = existing_points if existing_points else []
    color_counts = {color: sum(1 for p in points if p[2] == color) for color in COLORS[:num_colors]}
    
    for color in COLORS[:num_colors]:
        cluster_x = random.randint(100, WIDTH - 100)
        cluster_y = random.randint(100, HEIGHT - 260)
        while color_counts[color] < points_per_color:
            points.append((
                cluster_x + random.randint(-20, 20),
                cluster_y + random.randint(-20, 20),
                color
            ))
            color_counts[color] += 1
        while color_counts[color] > points_per_color:
            for i, p in enumerate(points):
                if p[2] == color:
                    points.pop(i)
                    color_counts[color] -= 1
                    break
    return points

points = generate_points()
selected_index = None

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def find_k_nearest(point, points, k):
    distances = [(p, euclidean_distance(point, (p[0], p[1]))) for p in points if (p[0], p[1]) != point]
    distances.sort(key=lambda x: x[1])
    return [p[0] for p in distances[:k]]

def classify_grid(grid_size):
    for x in range(0, WIDTH, grid_size):
        for y in range(0, HEIGHT - 200, grid_size):
            neighbors = find_k_nearest((x, y), points, K)
            if neighbors:
                most_common_color_index = Counter([p[2] for p in neighbors]).most_common(1)[0][0]
                color_index = COLORS.index(most_common_color_index)
                lighter_color = LIGHTER_COLORS[color_index]
                pygame.draw.rect(screen, lighter_color, (x, y, grid_size, grid_size))

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.dragging = False

    def draw(self, screen):
        pygame.draw.rect(screen, TAN, self.rect)
        pos = int((self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        pygame.draw.circle(screen, BROWN, (self.rect.x + pos, self.rect.y + self.rect.height // 2), 10)

    def update(self, mouse_pos):
        if self.dragging:
            pos = mouse_pos[0] - self.rect.x
            pos = max(0, min(self.rect.width, pos))
            self.val = self.min_val + (pos / self.rect.width) * (self.max_val - self.min_val)
            
buttons = {
    "Increase Points": (50, HEIGHT - 180, 150, 30),
    "Decrease Points": (250, HEIGHT - 180, 150, 30),
    "Add Colour": (450, HEIGHT - 180, 100, 30),
    "Remove Colour": (650, HEIGHT - 180, 130, 30)
}

def draw_controls():
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - 100, WIDTH, 200))

    draw_buttons()
    
    k_label = font.render(f"K: {int(K)}", True, BLACK)
    colors_label = font.render(f"Colours: {num_colors}", True, BLACK)
    points_label = font.render(f"Points/Colour: {points_per_color}", True, BLACK)
    screen.blit(k_label, (50, HEIGHT - 140))
    screen.blit(colors_label, (50, HEIGHT - 120))
    screen.blit(points_label, (50, HEIGHT - 100))

    slider_label = font.render("Adjust K:", True, BLACK)
    screen.blit(slider_label, (50, HEIGHT - 80))

k_slider = Slider(50, HEIGHT - 60, 200, 20, 1, 10, K)

main_title = title_font.render("KNN Visualiser", True, BLACK)
main_title_rect = main_title.get_rect(center=(WIDTH // 2, 50))

def draw_titles():
    title_box_width = main_title.get_width() + 40
    title_box_height = main_title.get_height() + 20
    title_box_x = main_title_rect.centerx - title_box_width // 2
    title_box_y = main_title_rect.centery - title_box_height // 2

    pygame.draw.rect(screen, WHITE, (title_box_x, title_box_y, title_box_width, title_box_height))
    pygame.draw.rect(screen, BROWN, (title_box_x, title_box_y, title_box_width, title_box_height), 3)

    screen.blit(main_title, main_title_rect)

BUTTON_WIDTH = 150
BUTTON_HEIGHT = 30
BUTTON_PADDING = 20

total_buttons_width = 4 * BUTTON_WIDTH + 3 * BUTTON_PADDING

start_x = (WIDTH - total_buttons_width) // 2

buttons = {
    "Increase Points": {
        "rect": (start_x, HEIGHT - 180, BUTTON_WIDTH, BUTTON_HEIGHT),
        "offset": (0, 0)
    },
    "Decrease Points": {
        "rect": (start_x + BUTTON_WIDTH + BUTTON_PADDING, HEIGHT - 180, BUTTON_WIDTH, BUTTON_HEIGHT),
        "offset": (0, 0)
    },
    "Add Colour": {
        "rect": (start_x + 2 * (BUTTON_WIDTH + BUTTON_PADDING), HEIGHT - 180, BUTTON_WIDTH, BUTTON_HEIGHT),
        "offset": (0, 0)
    },
    "Remove Colour": {
        "rect": (start_x + 3 * (BUTTON_WIDTH + BUTTON_PADDING), HEIGHT - 180, BUTTON_WIDTH, BUTTON_HEIGHT),
        "offset": (0, 0)
    }
}

def draw_buttons():
    for text, button_data in buttons.items():
        x, y, w, h = button_data["rect"]
        offset_x, offset_y = button_data["offset"]

        pygame.draw.rect(screen, BROWN, (x, y, w, h), border_radius=10)

        label = font.render(text, True, WHITE)

        text_width, text_height = label.get_size()

        label_x = x + (w - text_width) // 2 + offset_x
        label_y = y + (h - text_height) // 2 + offset_y

        screen.blit(label, (label_x, label_y))

running = True
while running:
    screen.fill(WHITE)
    classify_grid(TEMP_GRID_SIZE if dragging else GRID_SIZE)

    draw_titles()
    draw_buttons()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if my < HEIGHT - 200:
                for i, p in enumerate(points):
                    if euclidean_distance((mx, my), (p[0], p[1])) < 10:
                        selected_index = i
                        dragging = True
                        break
            else:
                for key, button_data in buttons.items():
                    x, y, w, h = button_data["rect"]
                    if x <= mx <= x + w and y <= my <= y + h:
                        if key == "Increase Points":
                            points_per_color += 1
                            points = generate_points(points)
                        elif key == "Decrease Points" and points_per_color > 1:
                            points_per_color -= 1
                            points = generate_points(points)
                        elif key == "Add Colour" and num_colors < MAX_COLORS:
                            num_colors += 1
                            points = generate_points(points)
                        elif key == "Remove Colour" and num_colors > 1:
                            num_colors -= 1
                            points = [p for p in points if p[2] in COLORS[:num_colors]]
                if k_slider.rect.collidepoint(mx, my):
                    k_slider.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            selected_index = None
            dragging = False
            k_slider.dragging = False
        elif event.type == pygame.MOUSEMOTION and selected_index is not None:
            mx, my = event.pos
            x = max(0, min(WIDTH, mx))
            y = max(0, min(HEIGHT - 200, my))
            points[selected_index] = (x, y, points[selected_index][2])
        elif event.type == pygame.MOUSEMOTION and k_slider.dragging:
            k_slider.update(event.pos)
            K = int(k_slider.val)
    
    for p in points:
        pygame.draw.circle(screen, p[2], (p[0], p[1]), 6)
        pygame.draw.circle(screen, BLACK, (p[0], p[1]), 7, 1)
    
    draw_controls()
    k_slider.draw(screen)
    pygame.display.flip()

pygame.quit()
