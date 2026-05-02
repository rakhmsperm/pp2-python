import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import pygame

from persistence import CAR_COLORS, DIFFICULTY_CONFIG, add_score
from ui import WHITE, BLACK, GRAY, YELLOW, GREEN, RED, BLUE, draw_text, Button

WIDTH = 700
HEIGHT = 800
FPS = 60
ROAD_X = 120
ROAD_W = 460
LANES = 4
LANE_W = ROAD_W // LANES
PLAYER_W = 48
PLAYER_H = 78

POWERUP_COLORS = {
    "nitro": (50, 220, 255),
    "shield": (120, 110, 255),
    "repair": (80, 230, 130)
}

POWERUP_LABELS = {
    "nitro": "N",
    "shield": "S",
    "repair": "R"
}


@dataclass
class Entity:
    rect: pygame.Rect
    kind: str
    lane: int
    speed: float = 0
    value: int = 0
    ttl: int = 0
    direction: int = 1


class RacerGame:
    def __init__(self, screen: pygame.Surface, username: str, settings: Dict):
        self.screen = screen
        self.username = username or "Player"
        self.settings = settings
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 44, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.config = DIFFICULTY_CONFIG[self.settings["difficulty"]]
        self.reset()

    def reset(self) -> None:
        self.running = True
        self.finished = False
        self.base_speed = self.config["base_speed"]
        self.road_speed = self.base_speed
        self.distance = 0
        self.coins = 0
        self.coin_score = 0
        self.power_bonus = 0
        self.score = 0
        self.finish_distance = self.config["finish_distance"]
        self.spawn_timer = 0
        self.event_timer = 0
        self.line_offset = 0
        self.active_power: Optional[str] = None
        self.power_timer = 0
        self.shield_hits = 0
        self.message = ""
        self.message_timer = 0

        car_color = CAR_COLORS[self.settings["car_color"]]
        self.player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 125, PLAYER_W, PLAYER_H)
        self.player_color = tuple(car_color)

        self.traffic: List[Entity] = []
        self.obstacles: List[Entity] = []
        self.coins_list: List[Entity] = []
        self.powerups: List[Entity] = []
        self.dynamic_events: List[Entity] = []

    def lane_center(self, lane: int) -> int:
        return ROAD_X + lane * LANE_W + LANE_W // 2

    def random_lane(self) -> int:
        return random.randint(0, LANES - 1)

    def safe_to_spawn(self, lane: int, y: int) -> bool:
        player_lane = max(0, min(LANES - 1, (self.player.centerx - ROAD_X) // LANE_W))
        if lane == player_lane and y > HEIGHT - 260:
            return False

        future_rect = pygame.Rect(self.lane_center(lane) - 25, y, 50, 80)
        all_entities = self.traffic + self.obstacles + self.coins_list + self.powerups + self.dynamic_events
        for entity in all_entities:
            if future_rect.colliderect(entity.rect.inflate(20, 40)):
                return False
        return True

    def spawn_traffic(self) -> None:
        lane = self.random_lane()
        if not self.safe_to_spawn(lane, -100):
            return
        rect = pygame.Rect(self.lane_center(lane) - 24, -90, 48, 76)
        self.traffic.append(Entity(rect=rect, kind="traffic", lane=lane, speed=self.road_speed + random.uniform(1.2, 3.0)))

    def spawn_obstacle(self) -> None:
        lane = self.random_lane()
        if not self.safe_to_spawn(lane, -70):
            return
        kind = random.choice(["barrier", "oil", "pothole", "slow"])
        rect = pygame.Rect(self.lane_center(lane) - 28, -70, 56, 38)
        self.obstacles.append(Entity(rect=rect, kind=kind, lane=lane, speed=self.road_speed))

    def spawn_coin(self) -> None:
        lane = self.random_lane()
        if not self.safe_to_spawn(lane, -40):
            return
        value = random.choices([1, 2, 5], weights=[65, 25, 10])[0]
        rect = pygame.Rect(self.lane_center(lane) - 13, -35, 26, 26)
        self.coins_list.append(Entity(rect=rect, kind="coin", lane=lane, speed=self.road_speed, value=value))

    def spawn_powerup(self) -> None:
        if self.active_power is not None:
            return
        lane = self.random_lane()
        if not self.safe_to_spawn(lane, -45):
            return
        kind = random.choice(["nitro", "shield", "repair"])
        rect = pygame.Rect(self.lane_center(lane) - 16, -45, 32, 32)
        self.powerups.append(Entity(rect=rect, kind=kind, lane=lane, speed=self.road_speed, ttl=FPS * 7))

    def spawn_dynamic_event(self) -> None:
        kind = random.choice(["moving_barrier", "speed_bump", "nitro_strip"])
        lane = self.random_lane()
        if not self.safe_to_spawn(lane, -60):
            return
        rect = pygame.Rect(self.lane_center(lane) - 35, -60, 70, 28)
        direction = random.choice([-1, 1])
        self.dynamic_events.append(Entity(rect=rect, kind=kind, lane=lane, speed=self.road_speed, direction=direction))

    def handle_events(self) -> str:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
        return "game"

    def handle_movement(self) -> None:
        keys = pygame.key.get_pressed()
        move_speed = 7
        if self.active_power == "nitro":
            move_speed = 9
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.x -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.x += move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.y -= move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.y += move_speed

        self.player.left = max(ROAD_X + 8, self.player.left)
        self.player.right = min(ROAD_X + ROAD_W - 8, self.player.right)
        self.player.top = max(40, self.player.top)
        self.player.bottom = min(HEIGHT - 30, self.player.bottom)

    def update_difficulty(self) -> Tuple[float, float]:
        progress_factor = min(2.2, 1 + self.distance / 2200)
        traffic_rate = self.config["traffic_rate"] * progress_factor
        obstacle_rate = self.config["obstacle_rate"] * progress_factor
        return traffic_rate, obstacle_rate

    def update_spawning(self) -> None:
        traffic_rate, obstacle_rate = self.update_difficulty()

        if random.random() < traffic_rate:
            self.spawn_traffic()
        if random.random() < obstacle_rate:
            self.spawn_obstacle()
        if random.random() < 0.040:
            self.spawn_coin()
        if random.random() < self.config["powerup_rate"]:
            self.spawn_powerup()
        if random.random() < 0.006 + min(0.010, self.distance / 300000):
            self.spawn_dynamic_event()

    def update_entities(self) -> None:
        groups = [self.traffic, self.obstacles, self.coins_list, self.powerups, self.dynamic_events]
        for group in groups:
            for entity in group:
                entity.rect.y += int(entity.speed)
                if entity.kind == "moving_barrier":
                    entity.rect.x += entity.direction * 2
                    if entity.rect.left < ROAD_X + 4 or entity.rect.right > ROAD_X + ROAD_W - 4:
                        entity.direction *= -1
                if entity.ttl > 0:
                    entity.ttl -= 1

        self.traffic = [e for e in self.traffic if e.rect.top < HEIGHT + 120]
        self.obstacles = [e for e in self.obstacles if e.rect.top < HEIGHT + 80]
        self.coins_list = [e for e in self.coins_list if e.rect.top < HEIGHT + 50]
        self.powerups = [e for e in self.powerups if e.rect.top < HEIGHT + 50 and e.ttl > 0]
        self.dynamic_events = [e for e in self.dynamic_events if e.rect.top < HEIGHT + 80]

    def activate_powerup(self, kind: str) -> None:
        self.active_power = kind
        self.power_bonus += 25
        if kind == "nitro":
            self.power_timer = FPS * 4
            self.message = "Nitro activated!"
        elif kind == "shield":
            self.power_timer = 0
            self.shield_hits = 1
            self.message = "Shield ready!"
        elif kind == "repair":
            self.power_timer = 1
            if self.obstacles:
                self.obstacles.pop(0)
            self.message = "Repair used: obstacle cleared!"
            self.active_power = None
        self.message_timer = FPS * 2

    def handle_collision_damage(self) -> bool:
        if self.active_power == "shield" and self.shield_hits > 0:
            self.shield_hits = 0
            self.active_power = None
            self.message = "Shield absorbed collision!"
            self.message_timer = FPS * 2
            return False
        return True

    def check_collisions(self) -> bool:
        for coin in self.coins_list[:]:
            if self.player.colliderect(coin.rect):
                self.coins += coin.value
                self.coin_score += coin.value * 10
                self.coins_list.remove(coin)

        for powerup in self.powerups[:]:
            if self.player.colliderect(powerup.rect):
                if self.active_power is None:
                    self.activate_powerup(powerup.kind)
                self.powerups.remove(powerup)

        for traffic in self.traffic[:]:
            if self.player.colliderect(traffic.rect):
                if self.handle_collision_damage():
                    return True
                self.traffic.remove(traffic)

        for obstacle in self.obstacles[:]:
            if self.player.colliderect(obstacle.rect):
                if obstacle.kind in ["oil", "slow"]:
                    self.player.y += 18
                    self.obstacles.remove(obstacle)
                else:
                    if self.handle_collision_damage():
                        return True
                    self.obstacles.remove(obstacle)

        for event in self.dynamic_events[:]:
            if self.player.colliderect(event.rect):
                if event.kind == "nitro_strip":
                    self.activate_powerup("nitro")
                    self.dynamic_events.remove(event)
                elif event.kind == "speed_bump":
                    self.player.y += 25
                    self.dynamic_events.remove(event)
                elif event.kind == "moving_barrier":
                    if self.handle_collision_damage():
                        return True
                    self.dynamic_events.remove(event)

        return False

    def update_powerups(self) -> None:
        if self.active_power == "nitro":
            self.power_timer -= 1
            self.road_speed = self.base_speed + 4
            if self.power_timer <= 0:
                self.active_power = None
                self.road_speed = self.base_speed
        else:
            self.road_speed = self.base_speed + min(5, self.distance // 1200)

        if self.message_timer > 0:
            self.message_timer -= 1

    def update_score(self) -> None:
        self.distance += int(self.road_speed / 2)
        distance_score = self.distance // 5
        self.score = distance_score + self.coin_score + self.power_bonus
        if self.distance >= self.finish_distance:
            self.finished = True

    def draw_road(self) -> None:
        self.screen.fill((25, 115, 55))
        pygame.draw.rect(self.screen, (45, 45, 48), (ROAD_X, 0, ROAD_W, HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (ROAD_X - 5, 0, 5, HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (ROAD_X + ROAD_W, 0, 5, HEIGHT))

        self.line_offset = (self.line_offset + self.road_speed) % 60
        for lane in range(1, LANES):
            x = ROAD_X + lane * LANE_W
            for y in range(-60, HEIGHT, 60):
                pygame.draw.rect(self.screen, (230, 230, 230), (x - 3, y + self.line_offset, 6, 35))

    def draw_car(self, rect: pygame.Rect, color: Tuple[int, int, int]) -> None:
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, (rect.x + 8, rect.y + 12, rect.w - 16, 18), border_radius=6)
        pygame.draw.rect(self.screen, BLACK, (rect.x + 6, rect.y + 52, 10, 18), border_radius=4)
        pygame.draw.rect(self.screen, BLACK, (rect.right - 16, rect.y + 52, 10, 18), border_radius=4)

    def draw_entities(self) -> None:
        for traffic in self.traffic:
            self.draw_car(traffic.rect, RED)

        for obstacle in self.obstacles:
            if obstacle.kind == "barrier":
                pygame.draw.rect(self.screen, (230, 120, 40), obstacle.rect, border_radius=6)
                pygame.draw.rect(self.screen, WHITE, obstacle.rect, 2, border_radius=6)
            elif obstacle.kind == "oil":
                pygame.draw.ellipse(self.screen, BLACK, obstacle.rect)
            elif obstacle.kind == "pothole":
                pygame.draw.ellipse(self.screen, (35, 25, 20), obstacle.rect)
            else:
                pygame.draw.rect(self.screen, (150, 150, 150), obstacle.rect, border_radius=8)

        for coin in self.coins_list:
            pygame.draw.ellipse(self.screen, YELLOW, coin.rect)
            label = self.small_font.render(str(coin.value), True, BLACK)
            self.screen.blit(label, label.get_rect(center=coin.rect.center))

        for powerup in self.powerups:
            pygame.draw.ellipse(self.screen, POWERUP_COLORS[powerup.kind], powerup.rect)
            label = self.small_font.render(POWERUP_LABELS[powerup.kind], True, BLACK)
            self.screen.blit(label, label.get_rect(center=powerup.rect.center))

        for event in self.dynamic_events:
            if event.kind == "moving_barrier":
                pygame.draw.rect(self.screen, (190, 50, 210), event.rect, border_radius=6)
            elif event.kind == "speed_bump":
                pygame.draw.rect(self.screen, (210, 210, 70), event.rect, border_radius=10)
            elif event.kind == "nitro_strip":
                pygame.draw.rect(self.screen, (40, 230, 255), event.rect, border_radius=12)

    def draw_hud(self) -> None:
        remaining = max(0, self.finish_distance - self.distance)
        draw_text(self.screen, f"Player: {self.username}", self.small_font, WHITE, 12, 12)
        draw_text(self.screen, f"Score: {self.score}", self.font, WHITE, 12, 36)
        draw_text(self.screen, f"Coins: {self.coins}", self.font, YELLOW, 12, 66)
        draw_text(self.screen, f"Distance: {self.distance} m", self.font, WHITE, 12, 96)
        draw_text(self.screen, f"Remaining: {remaining} m", self.font, WHITE, 12, 126)

        if self.active_power == "nitro":
            seconds = max(0, self.power_timer // FPS)
            power_text = f"Power: Nitro {seconds}s"
        elif self.active_power == "shield":
            power_text = "Power: Shield x1"
        else:
            power_text = "Power: none"
        draw_text(self.screen, power_text, self.font, GREEN, 12, 156)

        progress_width = 220
        pygame.draw.rect(self.screen, GRAY, (WIDTH - progress_width - 20, 20, progress_width, 18), border_radius=8)
        fill = int(progress_width * min(1, self.distance / self.finish_distance))
        pygame.draw.rect(self.screen, GREEN, (WIDTH - progress_width - 20, 20, fill, 18), border_radius=8)
        draw_text(self.screen, "Finish", self.small_font, WHITE, WIDTH - 80, 42)

        if self.message_timer > 0:
            draw_text(self.screen, self.message, self.font, BLUE, WIDTH // 2, 74, center=True)

    def draw(self) -> None:
        self.draw_road()
        self.draw_entities()
        self.draw_car(self.player, self.player_color)
        self.draw_hud()
        pygame.display.flip()

    def save_result(self) -> None:
        add_score(self.username, self.score, self.distance, self.coins, self.settings["difficulty"])

    def run(self) -> str:
        while self.running:
            state = self.handle_events()
            if state == "quit":
                return "quit"

            self.handle_movement()
            self.update_spawning()
            self.update_entities()
            crashed = self.check_collisions()
            self.update_powerups()
            self.update_score()
            self.draw()
            self.clock.tick(FPS)

            if crashed or self.finished:
                self.save_result()
                return "game_over"
        return "menu"

