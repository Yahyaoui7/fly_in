import pygame
from model import MapData


class Visualization:
    def __init__(self, data_map: MapData) -> None:
        self.data_map = data_map
        self.padding = 80
        self.scale = 1.0
        self.min_x = 0
        self.max_y = 0
        self.offset_x = 0
        self.offset_y = 0

    def prepare_layout(self, width: int, height: int) -> None:
        xs = [zone.x for zone in self.data_map.zones.values()]
        ys = [zone.y for zone in self.data_map.zones.values()]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        map_width = max(max_x - min_x, 1)
        map_height = max(max_y - min_y, 1)

        available_width = width - self.padding * 2
        available_height = height - self.padding * 2

        scale_x = available_width / map_width
        scale_y = available_height / map_height

        self.scale = min(scale_x, scale_y, 70)

        self.min_x = min_x
        self.max_y = max_y

        drawn_width = map_width * self.scale
        drawn_height = map_height * self.scale

        self.offset_x = self.padding + (available_width - drawn_width) / 2
        self.offset_y = self.padding + (available_height - drawn_height) / 2

    def world_to_screen(self, x: int, y: int) -> tuple[int, int]:
        screen_x = self.offset_x + (x - self.min_x) * self.scale
        screen_y = self.offset_y + (self.max_y - y) * self.scale

        return int(screen_x), int(screen_y)

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
                (255, 25, 126),
                start,
                end,
                4,
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

            pygame.draw.circle(screen, (120, 120, 120), position, 10)
            pygame.draw.circle(screen, (230, 230, 230), position, 10, 1)

            if zone.name == hovered_zone:
                text = font.render(zone.name, True, (255, 255, 255))
                text_pos = (
                    position[0] - text.get_width() // 2,
                    position[1] - 30,
                )
                screen.blit(text, text_pos)

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

    def display(self):
        pygame.init()
        width = 1400
        height = 800

        screen = pygame.display.set_mode((width, height))
        self.prepare_layout(width, height)

        pygame.display.set_caption("fly_in visualizer")

        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((20, 20, 25))

            mouse_pos = pygame.mouse.get_pos()

            self.display_connection(screen)
            self.display_zones(screen, mouse_pos)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
