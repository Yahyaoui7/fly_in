from dataclasses import dataclass, field


@dataclass
class Zone:
    """Store information about one zone in the map."""
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str = "none"
    max_drones: int = 1


@dataclass
class Connection:
    """Store a connection between two zones."""

    zone_a: str
    zone_b: str
    max_link_capacity: int = 1


class Drone:
    """Store drone state and planned path."""

    def __init__(self, drone_id: int, path: list[tuple[str, int]]) -> None:
        self.id = drone_id
        self.path = path
        self.position_index = 0
        self.finished = False


@dataclass
class MapData:
    """Store all parsed map data used by the simulator."""

    nb_drones: int = 0
    drones: dict[int, Drone] = field(default_factory=dict)
    start: str | None = None
    end: str | None = None
    zones: dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)
    adjacency: dict[str, list[str]] = field(default_factory=dict)
