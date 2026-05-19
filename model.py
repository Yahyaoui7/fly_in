from dataclasses import dataclass, field


@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str = "none"
    max_drones: int = 1


@dataclass
class Connection:
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1


@dataclass
class MapData:
    nb_drones: int = 0
    start: str = None
    end: str = None
    zones: dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)
    adjacency: dict[str, list[str]] = field(default_factory=dict)


class Drone:
    def __init__(self, drone_id: int, path: list[str]):
        self.id = drone_id
        self.path = path
        self.position_index = 0
        self.finished = False

    @property
    def current_zone(self) -> str:
        return self.path[self.position_index]

    @property
    def next_zone(self) -> str | None:
        if len(self.path) > self.position_index + 1:
            return self.path[self.position_index + 1]
        else:
            return None
