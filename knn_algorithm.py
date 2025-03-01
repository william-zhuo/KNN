import pygame
import random
import math
from collections import Counter

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 3  # Each grid cell is 3x3 pixels
POINT_COUNT = 10  # Initial number of random points
K = 3  # Initial number of neighbors

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

def lighten_color(color, factor=1.5):
    return tuple(min(255, int(c * factor)) for c in color)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))  # Extra space for buttons
pygame.display.set_caption("K-Nearest Neighbors Visualization")
font = pygame.font.Font(None, 24)

# Generate random points
def generate_points(n, width, height):
    return [(random.randint(20, width - 20), random.randint(20, height - 70), random.choice(COLORS)) for _ in range(n)]

points = generate_points(POINT_COUNT, WIDTH, HEIGHT)
selected_point = None

# Compute Euclidean distance
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Find K-nearest neighbors
def find_k_nearest(point, points, k):
    distances = [(p, euclidean_distance(point, (p[0], p[1]))) for p in points if (p[0], p[1]) != point]
    distances.sort(key=lambda x: x[1])
    return [p[0] for p in distances[:k]]

# Classify grid cells
def classify_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        for y in range(0, HEIGHT, GRID_SIZE):
            neighbors = find_k_nearest((x, y), points, K)
            if neighbors:
                most_common_color = Counter([p[2] for p in neighbors]).most_common(1)[0][0]
                lighter_color = lighten_color(most_common_color)
                pygame.draw.rect(screen, lighter_color, (x, y, GRID_SIZE, GRID_SIZE))

# Buttons
buttons = {
    "Increase K": (50, HEIGHT + 10, 100, 30),
    "Decrease K": (200, HEIGHT + 10, 100, 30),
    "Add Point": (350, HEIGHT + 10, 100, 30),
    "Remove Point": (500, HEIGHT + 10, 100, 30)
}

def draw_buttons():
    for text, (x, y, w, h) in buttons.items():
        pygame.draw.rect(screen, BLACK, (x, y, w, h), 2)
        label = font.render(text, True, BLACK)
        screen.blit(label, (x + 10, y + 5))
    
    # Display K value and point count
    k_label = font.render(f"K: {K}", True, BLACK)
    points_label = font.render(f"Points: {len(points)}", True, BLACK)
    screen.blit(k_label, (650, HEIGHT + 10))
    screen.blit(points_label, (650, HEIGHT + 30))

# Main loop
running = True
while running:
    screen.fill(WHITE)
    classify_grid()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if my < HEIGHT:
                for p in points:
                    if euclidean_distance((mx, my), (p[0], p[1])) < 10:
                        selected_point = p
                        break
            else:
                for key, (x, y, w, h) in buttons.items():
                    if x <= mx <= x + w and y <= my <= y + h:
                        if key == "Increase K":
                            K += 1
                        elif key == "Decrease K" and K > 1:
                            K -= 1
                        elif key == "Add Point":
                            points.append((random.randint(20, WIDTH - 20), random.randint(20, HEIGHT - 70), random.choice(COLORS)))
                        elif key == "Remove Point" and points:
                            points.pop()
        elif event.type == pygame.MOUSEBUTTONUP:
            selected_point = None
        elif event.type == pygame.MOUSEMOTION and selected_point:
            selected_point = (event.pos[0], event.pos[1], selected_point[2])
            points = [selected_point if p == selected_point else p for p in points]
    
    for p in points:
        pygame.draw.circle(screen, p[2], (p[0], p[1]), 6)  # Slightly larger for better visibility
    
    draw_buttons()
    pygame.display.flip()

pygame.quit()
