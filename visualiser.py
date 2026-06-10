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

    def handle_even(self) -> None:
        """Processes user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
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
                    pygame.quit()

    def display(self):

        running = True

        while running:
            self.handle_even()
            self.screen.fill((20, 20, 25))

            mouse_pos = pygame.mouse.get_pos()

            self.display_connection(self.screen)
            self.display_zones(self.screen, mouse_pos)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def world_to_screen(self, x: int, y: int) -> tuple[int, int]:
        return (
            self.WIDTH // 2 + (x * self.SCALE) + (self.camera_x * self.SCALE),
            self.HEIGHT // 2 + (y * self.SCALE) + (self.camera_y * self.SCALE),
        )

    def display_connection(self, screen):
        for connection in self.data_map.connections:
            a = connection.zone_a
            b = connection.zone_b

            zone_a = self.data_map.zones[a]
            zone_b = self.data_map.zones[b]
            start = self.world_to_screen(zone_a.x, zone_a.y)
            end = self.world_to_screen(zone_b.x, zone_b.y)
            pygame.draw.line(
                screen,
                (120, 120, 120),
                start,
                end,
                2,
            )

    def display_zones(
        self,
        screen: pygame.Surface,
        mouse_pos: tuple[int, int],
    ) -> None:
        font = pygame.font.SysFont(None, 22)
        hovered_zone = self.get_hovered_zone(mouse_pos)

        for zone in self.data_map.zones.values():
            position = self.world_to_screen(zone.x, zone.y)
            color = self.get_zone_color(zone.color)

            pygame.draw.circle(screen, color, position, 10)
            pygame.draw.circle(screen, color, position, 10, 1)

            if zone.name == hovered_zone:
                text = font.render(zone.name, True, (255, 255, 255))
                text_pos = (
                    position[0] - text.get_width() // 2,
                    position[1] - 30,
                )
                screen.blit(text, text_pos)

    def get_zone_color(self, color):
        if color == "none":
            color = "gray"
        if color == "rainbow":
            color = "magenta"
        return color

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
