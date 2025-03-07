import pygame
import math
import random
from collections import Counter

# Constants
WIDTH, HEIGHT = 800, 700  # Increased height for additional controls
GRID_SIZE = 5  # Each grid cell is 5x5 pixels
TEMP_GRID_SIZE = 9  # Temporary lower resolution while dragging
POINTS_PER_COLOR = 4  # Initial number of points per color
K = 2  # Initial number of neighbors
MAX_COLORS = 6  # Maximum number of colors

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (255, 0, 255), (0, 255, 255)
]

# Global variables
num_colors = 3  # Initial number of colors used
points_per_color = POINTS_PER_COLOR  # User-adjustable points per color
dragging = False  # Flag to track if a point is being dragged

def lighten_color(color, factor=2.5):  # Increase factor to make colors much lighter
    return tuple(min(255, int(c * factor)) for c in color)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 100))  # Extra space for buttons
pygame.display.set_caption("K-Nearest Neighbors Visualization")
font = pygame.font.Font(None, 24)

def generate_points(existing_points=None):
    points = existing_points if existing_points else []
    color_counts = {color: sum(1 for p in points if p[2] == color) for color in COLORS[:num_colors]}
    
    for color in COLORS[:num_colors]:
        cluster_x = random.randint(100, WIDTH - 100)
        cluster_y = random.randint(100, HEIGHT - 150)
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
        for y in range(0, HEIGHT, grid_size):
            neighbors = find_k_nearest((x, y), points, K)
            if neighbors:
                most_common_color = Counter([p[2] for p in neighbors]).most_common(1)[0][0]
                lighter_color = lighten_color(most_common_color)
                pygame.draw.rect(screen, lighter_color, (x, y, grid_size, grid_size))

buttons = {
    "Increase K": (50, HEIGHT + 10, 100, 30),
    "Decrease K": (200, HEIGHT + 10, 100, 30),
    "Add Color": (350, HEIGHT + 10, 100, 30),
    "Remove Color": (500, HEIGHT + 10, 120, 30),
    "Increase Points": (50, HEIGHT + 50, 150, 30),
    "Decrease Points": (250, HEIGHT + 50, 150, 30)
}

def draw_buttons():
    for text, (x, y, w, h) in buttons.items():
        pygame.draw.rect(screen, BLACK, (x, y, w, h), 2)
        label = font.render(text, True, BLACK)
        screen.blit(label, (x + 10, y + 5))
    
    k_label = font.render(f"K: {K}", True, BLACK)
    colors_label = font.render(f"Colors: {num_colors}", True, BLACK)
    points_label = font.render(f"Points/Color: {points_per_color}", True, BLACK)
    screen.blit(k_label, (650, HEIGHT + 10))
    screen.blit(colors_label, (650, HEIGHT + 30))
    screen.blit(points_label, (650, HEIGHT + 50))

running = True
while running:
    screen.fill(WHITE)
    classify_grid(TEMP_GRID_SIZE if dragging else GRID_SIZE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if my < HEIGHT:
                for i, p in enumerate(points):
                    if euclidean_distance((mx, my), (p[0], p[1])) < 10:
                        selected_index = i
                        dragging = True
                        break
            else:
                for key, (x, y, w, h) in buttons.items():
                    if x <= mx <= x + w and y <= my <= y + h:
                        if key == "Increase K":
                            K += 1
                        elif key == "Decrease K" and K > 1:
                            K -= 1
                        elif key == "Add Color" and num_colors < MAX_COLORS:
                            num_colors += 1
                            points = generate_points(points)
                        elif key == "Remove Color" and num_colors > 1:
                            num_colors -= 1
                            points = [p for p in points if p[2] in COLORS[:num_colors]]
                        elif key == "Increase Points":
                            points_per_color += 1
                            points = generate_points(points)
                        elif key == "Decrease Points" and points_per_color > 1:
                            points_per_color -= 1
                            points = generate_points(points)
        elif event.type == pygame.MOUSEBUTTONUP:
            selected_index = None
            dragging = False
        elif event.type == pygame.MOUSEMOTION and selected_index is not None:
            mx, my = event.pos
            x = max(0, min(WIDTH, mx))
            y = max(0, min(HEIGHT, my))
            points[selected_index] = (x, y, points[selected_index][2])
    
    for p in points:
        pygame.draw.circle(screen, p[2], (p[0], p[1]), 6)
        pygame.draw.circle(screen, BLACK, (p[0], p[1]), 7, 1)
    
    draw_buttons()
    pygame.display.flip()

pygame.quit()
