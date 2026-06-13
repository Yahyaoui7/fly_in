import pygame
from model import MapData


class Visualization:
    WIDTH = 1400
    HEIGHT = 800
    SCALE = 100
    camera_scalar = 1

    def __init__(self, data_map: MapData, max_turn) -> None:
        self.data_map = data_map
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.camera_x = -5
        self.camera_y = 0
        self.running = True
        self.current_turn = 0
        self.max_turn = max_turn

    def handle_even(self) -> None:
        """Processes user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.camera_y -= self.camera_scalar
                if event.key == pygame.K_UP:
                    self.camera_y += self.camera_scalar
                if event.key == pygame.K_LEFT:
                    self.camera_x += self.camera_scalar
                if event.key == pygame.K_RIGHT:
                    self.camera_x -= self.camera_scalar
                if event.key == pygame.K_SPACE:
                    self.turn()  # this is about move drone in one turn
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def display(self):

        while self.running:
            self.handle_even()
            self.screen.fill((0, 0, 80))

            self.display_connection()
            self.display_zones()
            self.display_drone()
            self.print_title()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def display_connection(self):
        for connection in self.data_map.connections:
            a = connection.zone_a
            b = connection.zone_b

            zone_a = self.data_map.zones[a]
            zone_b = self.data_map.zones[b]
            start = self.world_to_screen(zone_a.x, zone_a.y)
            end = self.world_to_screen(zone_b.x, zone_b.y)
            pygame.draw.line(
                self.screen,
                (120, 120, 120),
                start,
                end,
                2,
            )

    def display_zones(
        self,
    ) -> None:

        for zone in self.data_map.zones.values():
            position = self.world_to_screen(zone.x, zone.y)
            color = self.get_zone_color(zone.color)

            pygame.draw.circle(self.screen, color, position, 20)
            pygame.draw.circle(self.screen, (255, 255, 255), position, 20, 1)
            self.print_name_zone(zone.name, position)




    def display_drone(self) -> None:
        for drone_id, drone in self.data_map.drones.items():
            position = self.get_drone_position(drone)

            if position is None:
                continue

            pygame.draw.circle(self.screen, "black", position, 8)
            pygame.draw.circle(self.screen, "white", position, 8, 1)
            self.print_name_drone(drone_id, position)


    def print_name_zone(self, name, drone_pos):
        font = pygame.font.SysFont(None, 14)
        text = font.render(name, True, "white")
        self.screen.blit(text, (drone_pos[0] - 20, drone_pos[1] - 35))

    def print_title(self):
        font = pygame.font.SysFont(None, 25)
        text = font.render(f"{self.current_turn}", True, "white")
        self.screen.blit(text, (10, 10))

    def print_name_drone(self, name, drone_pos):
        font = pygame.font.SysFont(None, 14)
        text = font.render(f"D{name}", True, "white")
        self.screen.blit(text, (drone_pos[0] - 8, drone_pos[1] - 17))

    def world_to_screen(self, x: int, y: int) -> tuple[int, int]:
        return (
            self.WIDTH // 2 + (x * self.SCALE) + (self.camera_x * self.SCALE),
            self.HEIGHT // 2 + (y * self.SCALE) + (self.camera_y * self.SCALE),
        )


    def get_zone_color(self, color):
        if color == "none":
            color = "gray"
        if color == "rainbow":
            color = "magenta"
        return color

    def turn(self) -> None:
        """Move the visualization one simulation turn forward."""
        if self.current_turn >= self.max_turn:
            return

        self.current_turn += 1

        for drone in self.data_map.drones.values():
            if not drone.path:
                continue

            for index, (_, path_turn) in enumerate(drone.path):
                if path_turn <= self.current_turn:
                    drone.position_index = index

    def get_drone_position(self, drone) -> tuple[int, int] | None:
        current_turn = self.current_turn

        for index in range(len(drone.path) - 1):
            from_zone_name, from_turn = drone.path[index]
            to_zone_name, to_turn = drone.path[index + 1]

            from_zone = self.data_map.zones[from_zone_name]
            to_zone = self.data_map.zones[to_zone_name]

            if current_turn == from_turn:
                return self.world_to_screen(from_zone.x, from_zone.y)

            if from_turn < current_turn < to_turn:
                return self.get_position_betw_zones(from_zone, to_zone)

            if current_turn == to_turn:
                return self.world_to_screen(to_zone.x, to_zone.y)

        return None

    def wait_in_goal_zone(self, drone_id, position):

        pygame.draw.circle(self.screen, "black", position, 8)
        pygame.draw.circle(self.screen, "white", position, 8, 1)
        self.print_name_zone(drone_id, position)

    def get_position_betw_zones(self, from_zone, to_zone):
        x = (from_zone.x + to_zone.x) / 2
        y = (from_zone.y + to_zone.y) / 2
        return self.world_to_screen(x, y)
