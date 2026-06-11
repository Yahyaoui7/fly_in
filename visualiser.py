import pygame
from model import MapData


class Visualization:
    WIDTH = 1400
    HEIGHT = 800
    SCALE = 100
    camera_scalar = 1

    def __init__(self, data_map: MapData) -> None:
        self.data_map = data_map
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.camera_x = -5
        self.camera_y = 0
        self.running = True

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
            self.screen.fill((20, 20, 25))

            mouse_pos = pygame.mouse.get_pos()

            self.display_connection()
            self.display_zones(mouse_pos)
            self.display_drone()
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
        mouse_pos: tuple[int, int],
    ) -> None:
        font = pygame.font.SysFont("Courier New", 22)
        hovered_zone = self.get_hovered_zone(mouse_pos)

        for zone in self.data_map.zones.values():
            position = self.world_to_screen(zone.x, zone.y)
            color = self.get_zone_color(zone.color)

            pygame.draw.circle(self.screen, color, position, 15)
            pygame.draw.circle(self.screen, (255, 255, 255), position, 15, 1)

            if zone.name == hovered_zone:
                text = font.render(zone.name, True, (255, 255, 255))
                text_pos = (
                    position[0] - text.get_width() // 2,
                    position[1] - 60,
                )
                self.screen.blit(text, text_pos)

    def display_drone(self):

        for drone in self.data_map.drones.values():
            current_zone = drone.current_zone
            zone = self.data_map.zones[current_zone[0]]

            position = self.world_to_screen(zone.x, zone.y)
            color = "red"
            pygame.draw.circle(self.screen, color, position, 10)
            pygame.draw.circle(self.screen, (255, 255, 255), position, 10, 1)

    def world_to_screen(self, x: int, y: int) -> tuple[int, int]:
        return (
            self.WIDTH // 2 + (x * self.SCALE) + (self.camera_x * self.SCALE),
            self.HEIGHT // 2 + (y * self.SCALE) + (self.camera_y * self.SCALE),
        )

    def get_hovered_zone(
        self,
        mouse_pos: tuple[int, int],
    ) -> str | None:
        for zone in self.data_map.zones.values():
            position = self.world_to_screen(zone.x, zone.y)

            dx = mouse_pos[0] - position[0]
            dy = mouse_pos[1] - position[1]

            if dx * dx + dy * dy <= 20 * 20:
                return zone.name

        return None

    def get_zone_color(self, color):
        if color == "none":
            color = "gray"
        if color == "rainbow":
            color = "magenta"
        return color
