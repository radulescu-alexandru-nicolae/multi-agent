import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 1200, 800
CONSTRUCTOR_COLOR = (255, 0, 0)
MINER_COLOR = (0, 0, 255)
RESOURCE_COLOR = (0, 255, 0)

class Constructor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.resources = 0

    def draw(self, screen):
        pygame.draw.circle(screen, CONSTRUCTOR_COLOR, (self.x, self.y), 20)

class Miner:
    def __init__(self, x, y, color, strategy):
        self.x = x
        self.y = y
        self.color = color
        self.strategy = strategy
        self.resources = 0
        self.target_x = None
        self.target_y = None
        self.collecting_resources = False
        self.delivering_resources = False

    def move_towards(self, target_x, target_y, speed=5):
        if target_x is not None and target_y is not None:
            dx = target_x - self.x
            dy = target_y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance != 0:
                move_amount = min(speed, distance)
                self.x += move_amount * dx / distance
                self.y += move_amount * dy / distance
                return move_amount

    def mine_resources(self):
        mined_amount = random.randint(1, 5)
        print(f"Miner mined {mined_amount} resources.")
        return mined_amount

    def choose_resource(self, resources_coordinates, selected_resources):
        if self.strategy == "random":
            return random.choice(resources_coordinates)
        elif self.strategy == "closest":
            return self.choose_closest_resource(resources_coordinates, selected_resources)
        else:
            raise ValueError("Invalid strategy")

    def choose_closest_resource(self, resources_coordinates, selected_resources):
        if not resources_coordinates:
            return None
        available_resources = [coord for coord in resources_coordinates if coord not in selected_resources]
        if not available_resources:
            return None
        distances = [((self.x - coord[0]) ** 2 + (self.y - coord[1]) ** 2) ** 0.5 for coord in available_resources]
        min_distance_index = distances.index(min(distances))
        selected_resources.add(available_resources[min_distance_index])
        return available_resources[min_distance_index]

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multi-Agent System Simulation")

constructor = Constructor(WIDTH // 2, HEIGHT // 2)
miners = [
    Miner(WIDTH // 2, HEIGHT // 2, MINER_COLOR, strategy="random"),
    Miner(WIDTH // 2, HEIGHT // 2, MINER_COLOR, strategy="closest"),
    Miner(WIDTH // 2, HEIGHT // 2, MINER_COLOR, strategy="random"),
    Miner(WIDTH // 2, HEIGHT // 2, MINER_COLOR, strategy="closest")
]
resources_coordinates = [(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)) for _ in range(100)]
selected_resources = set()

clock = pygame.time.Clock()
FPS = 30

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for miner in miners:
        if miner.collecting_resources:
            move_amount = miner.move_towards(miner.target_x, miner.target_y)
            if miner.target_x is not None and miner.target_y is not None and move_amount:
                if pygame.Rect(miner.x - 1, miner.y - 1, 2, 2).colliderect(pygame.Rect(miner.target_x - 1, miner.target_y - 1, 2, 2)):
                    resources_collected = miner.mine_resources()
                    miner.resources += resources_collected
                    miner.collecting_resources = False
                    miner.delivering_resources = True
        elif miner.delivering_resources:
            move_amount = miner.move_towards(constructor.x, constructor.y)
            if move_amount:
                if pygame.Rect(miner.x - 1, miner.y - 1, 2, 2).colliderect(pygame.Rect(constructor.x - 1, constructor.y - 1, 2, 2)):
                    constructor.resources += miner.resources
                    miner.resources = 0
                    miner.delivering_resources = False
                    miner.target_x = None
        else:
            if resources_coordinates:
                resource = miner.choose_resource(resources_coordinates, selected_resources)
                if resource:
                    miner.target_x, miner.target_y = resource
                    miner.collecting_resources = True

    for miner in miners:
        if miner.collecting_resources or miner.delivering_resources:
            break
    else:
        for miner in miners:
            if miner.target_x is not None and miner.target_y is not None:
                resources_coordinates.remove((miner.target_x, miner.target_y))
                miner.target_x = None

    resources_coordinates = [coord for coord in resources_coordinates if
                              all(pygame.Rect(coord[0] - 1, coord[1] - 1, 2, 2).colliderect(pygame.Rect(miner.x - 1, miner.y - 1, 2, 2)) == False for miner in miners)]

    screen.fill((255, 255, 255))
    constructor.draw(screen)
    for miner in miners:
        miner.draw(screen)
    for coord in resources_coordinates:
        pygame.draw.circle(screen, RESOURCE_COLOR, coord, 10)

    if not resources_coordinates:
        running = False

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()
