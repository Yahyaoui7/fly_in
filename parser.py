from pathlib import Path
from typing import Callable

from errors import ParseError
from model import Connection, Zone, MapData, Drone

Line = tuple[str, int]
ParserFunction = Callable[[str, str, int], None]

VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}
SUPPORTED_COLOR = {
    "crimson",
    "violet",
    "darkred",
    "maroon",
    "black",
    "red",
    "blue",
    "purple",
    "yellow",
    "orange",
    "cyan",
    "brown",
    "lime",
    "green",
    "gold",
    "magenta",
    "rainbow",
}


class MapParser:
    """Parse a Fly-in map file and build a MapData object."""

    def __init__(self, file_path: str | Path) -> None:
        """Initialize the parser with the map file path."""

        self.file_path: str | Path = file_path
        self.data_map: MapData = MapData()
        self.connection_keys: set[frozenset[str]] = set()

        self.funs_of_parser: dict[str, ParserFunction] = {
            "start_hub": self._parse_zone,
            "hub": self._parse_zone,
            "end_hub": self._parse_zone,
            "connection": self._parse_connection,
        }

    def parse(self) -> None:
        """Read the file and parse all valid map lines."""
        with open(self.file_path, "r", encoding="utf-8") as file:
            raw_lines = file.readlines()

        numbered_lines = self._add_number_of_line(raw_lines)
        valid_lines = self._remove_comments(numbered_lines)

        self._parser_all(valid_lines)

    def _add_number_of_line(self, lines: list[str]) -> list[Line]:
        """Attach line numbers to raw file lines."""
        numbered_lines: list[Line] = []

        for index, line in enumerate(lines, start=1):
            numbered_lines.append((line, index))

        return numbered_lines

    def _remove_comments(self, lines: list[Line]) -> list[Line]:
        """Remove comments and empty lines from parsed input."""

        valid_lines: list[Line] = []

        for line_text, line_number in lines:
            clean_line = line_text.split("#", 1)[0].strip()

            if clean_line:
                valid_lines.append((clean_line, line_number))

        return valid_lines

    def _parser_all(self, lines: list[Line]) -> None:
        """Parse all cleaned lines and validate the final map."""

        if not lines:
            raise ParseError("File is empty or contains only comments")

        self._parse_nb_drones(lines[0])

        for line_text, line_number in lines[1:]:
            if ":" not in line_text:
                raise ParseError(f"Line {line_number}: missing ':'")

            kind, body = line_text.split(":", 1)
            kind = kind.strip().lower()
            body = body.strip().lower()

            if kind == "nb_drones":
                raise ParseError(
                    f"Line {line_number}: duplicate nb_drones declaration"
                )

            parser_function = self.funs_of_parser.get(kind)

            if parser_function is None:
                raise ParseError(
                    f"Line {line_number}: invalid line type '{kind}'"
                )

            parser_function(kind, body, line_number)
        self.add_drones_to_map()
        self._validate_final_result()

    def _parse_nb_drones(self, line: Line) -> None:
        """Parse the number of drones from the first line."""

        line_text, line_number = line

        if ":" not in line_text:
            raise ParseError(f"Line {line_number}: missing ':'")

        name, value_text = line_text.split(":", 1)
        name = name.strip().lower()
        value_text = value_text.strip()

        if name != "nb_drones":
            raise ParseError(
                f"Line {line_number}: expected 'nb_drones', got '{name}'"
            )

        self.data_map.nb_drones = self._parse_positive_int(
            value_text,
            "nb_drones",
            line_number,
        )

    def _parse_zone(self, kind: str, body: str, line_number: int) -> None:
        """Parse a start, end, or normal zone line."""

        parts = body.split(maxsplit=3)

        if len(parts) < 3:
            raise ParseError(
                f"Line {line_number}: zone must have name, x, and y"
            )

        zone_name = parts[0]
        x_text = parts[1]
        y_text = parts[2]
        metadata_text = parts[3] if len(parts) == 4 else None

        self._validate_zone_name(zone_name, line_number)

        x, y = self._parse_coordinates(x_text, y_text, line_number)
        zone_type, color, max_drones = self._parse_zone_metadata(
            kind,
            metadata_text,
            line_number,
        )

        zone = Zone(
            name=zone_name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
        )

        if kind == "start_hub":
            if self.data_map.start is not None:
                raise ParseError(f"Line {line_number}: duplicate start_hub")
            self.data_map.start = zone_name

        elif kind == "end_hub":
            if self.data_map.end is not None:
                raise ParseError(f"Line {line_number}: duplicate end_hub")
            self.data_map.end = zone_name

        self.data_map.zones[zone_name] = zone

    def _parse_connection(
        self, kind: str, body: str, line_number: int
    ) -> None:
        """Parse a bidirectional connection line."""

        parts = body.split(maxsplit=1)
        if not parts:
            raise ParseError(f"Line {line_number}: connection is missing data")

        connection_text = parts[0]
        metadata_text = parts[1] if len(parts) == 2 else None

        if connection_text.count("-") != 1:
            raise ParseError(
                f"Line {line_number}: connection must be like zone1-zone2"
            )

        zone_a, zone_b = connection_text.split("-", 1)

        if not zone_a or not zone_b:
            raise ParseError(
                f"Line {line_number}: connection has empty zone name"
            )

        if zone_a == zone_b:
            raise ParseError(
                f"Line {line_number}: connection cannot link zone to itself"
            )

        if zone_a not in self.data_map.zones:
            raise ParseError(
                f"Line {line_number}: unknown zone '{zone_a}' in connection"
            )

        if zone_b not in self.data_map.zones:
            raise ParseError(
                f"Line {line_number}: unknown zone '{zone_b}' in connection"
            )

        connection_key = frozenset((zone_a, zone_b))
        if connection_key in self.connection_keys:
            raise ParseError(
                f"Line {line_number}: duplicate connection '{zone_a}-{zone_b}'"
            )

        max_link_capacity = self._parse_connection_metadata(
            metadata_text,
            line_number,
        )

        self.connection_keys.add(connection_key)
        self.data_map.connections.append(
            Connection(
                zone_a=zone_a,
                zone_b=zone_b,
                max_link_capacity=max_link_capacity,
            )
        )

    def _parse_coordinates(
        self,
        x_text: str,
        y_text: str,
        line_number: int,
    ) -> tuple[int, int]:
        """Parse and validate zone coordinates."""

        try:
            x = int(x_text)
            y = int(y_text)
            pos = (x, y)
            for zone in self.data_map.zones.values():
                if pos == (zone.x, zone.y):
                    raise ParseError(
                        f"Line {line_number}: this coordinates duplicate {pos}"
                    )
        except ValueError:
            raise ParseError(
                f"Line {line_number}: coordinates must be integers"
            )

        return x, y

    def _parse_zone_metadata(
        self,
        zone_name: str,
        metadata_text: str | None,
        line_number: int,
    ) -> tuple[str, str, int]:
        """Parse optional zone metadata."""

        zone_type = "normal"
        color = "none"
        max_drones = 1

        if metadata_text is None:
            return zone_type, color, max_drones

        metadata_text = metadata_text.strip()

        if not metadata_text:
            return zone_type, color, max_drones

        if not metadata_text.startswith("[") or not metadata_text.endswith(
            "]"
        ):
            raise ParseError(
                f"Line {line_number}: metadata must be inside '[' and ']'"
            )
        if metadata_text.count("[") != 1 or metadata_text.count("]") != 1:
            raise ParseError(
                "metadata must contain exactly one '[' and one ']'"
            )
        metadata_content = metadata_text[1:-1].strip()

        if not metadata_content:
            return zone_type, color, max_drones

        seen_keys: set[str] = set()
        for item in metadata_content.split():
            if item.count("=") != 1:
                raise ParseError(
                    f"Line {line_number}: metadata item must be key=value"
                )

            key, value = item.split("=", 1)

            if key in seen_keys:
                raise ParseError(
                    f"Line {line_number}: duplicate metadata key '{key}'"
                )

            seen_keys.add(key)

            if key == "zone":
                if value not in VALID_ZONE_TYPES:
                    raise ParseError(
                        f"Line {line_number}: invalid zone type '{value}'"
                    )
                zone_type = value

            elif key == "color":
                if not value:
                    raise ParseError(
                        f"Line {line_number}: color cannot be empty"
                    )
                elif value.lower() not in SUPPORTED_COLOR:
                    raise ParseError(
                        f"Line: {line_number}: this not valid color !"
                    )
                color = value

            elif key == "max_drones":

                max_drones = self._parse_positive_int(
                    value,
                    "max_drones",
                    line_number,
                )
                if zone_name in ["start_hub", "end_hub"]:
                    if max_drones < self.data_map.nb_drones:
                        raise ParseError(
                            f"Line {line_number}: max drone cannot "
                            f"be less then {self.data_map.nb_drones}"
                        )

            else:
                raise ParseError(
                    f"Line {line_number}: invalid zone metadata key '{key}'"
                )
        if zone_name in ["start_hub", "end_hub"]:
            max_drones = self.data_map.nb_drones
        return zone_type, color, max_drones

    def _parse_connection_metadata(
        self,
        metadata_text: str | None,
        line_number: int,
    ) -> int:
        """Parse optional connection metadata."""

        max_link_capacity = 1

        if metadata_text is None:
            return max_link_capacity

        metadata_text = metadata_text.strip()

        if not metadata_text:
            return max_link_capacity

        if not metadata_text.startswith("[") or not metadata_text.endswith(
            "]"
        ):

            raise ParseError(f"Line {line_number}: metadata must use [ ]")

        if metadata_text.count("[") != 1 or metadata_text.count("]") != 1:
            raise ParseError(
                "metadata must contain exactly one '[' and one ']'"
            )

        metadata_content = metadata_text[1:-1].strip()

        if not metadata_content:
            return max_link_capacity

        seen_keys: set[str] = set()

        for item in metadata_content.split():
            if item.count("=") != 1:
                raise ParseError(f"Line {line_number}: expected key=value")

            key, value = item.split("=", 1)

            if key in seen_keys:
                raise ParseError(f"Line {line_number}: duplicate key '{key}'")

            seen_keys.add(key)

            if key != "max_link_capacity":
                raise ParseError(f"Line {line_number}: invalid key '{key}'")

            max_link_capacity = self._parse_positive_int(
                value,
                "max_link_capacity",
                line_number,
            )

        return max_link_capacity

    def _parse_positive_int(
        self,
        value_text: str,
        field_name: str,
        line_number: int,
    ) -> int:
        """Parse a positive integer field."""

        try:
            value = int(value_text)
        except ValueError:
            raise ParseError(
                f"Line {line_number}: {field_name} must be an integer"
            )

        if value <= 0:
            raise ParseError(
                f"Line {line_number}: {field_name} must be greater than 0"
            )

        return value

    def _validate_zone_name(self, zone_name: str, line_number: int) -> None:
        """Validate a zone name."""
        if not zone_name:
            raise ParseError(f"Line {line_number}: zone name cannot be empty")

        if "-" in zone_name:
            raise ParseError(
                f"Line {line_number}: zone name cannot contain '-'"
            )

        if " " in zone_name:
            raise ParseError(
                f"Line {line_number}: zone name cannot contain spaces"
            )
        if zone_name in self.data_map.zones:
            raise ParseError(
                f"Line {line_number}: duplicate zone name '{zone_name}'"
            )

    def _validate_final_result(self) -> None:
        """Validate the parsed map after all lines are processed."""

        if self.data_map.nb_drones is None:
            raise ParseError("Missing nb_drones")

        if self.data_map.start is None:
            raise ParseError("Missing start_hub")

        if self.data_map.end is None:
            raise ParseError("Missing end_hub")

        if self.data_map.zones[self.data_map.start].zone_type == "blocked":
            raise ParseError("start_hub cannot be blocked")

        if self.data_map.zones[self.data_map.end].zone_type == "blocked":
            raise ParseError("end_hub cannot be blocked")

        adjacency: dict[str, list[str]] = {}

        for zone_name in self.data_map.zones:
            adjacency[zone_name] = []

        for connection in self.data_map.connections:
            adjacency[connection.zone_a].append(connection.zone_b)
            adjacency[connection.zone_b].append(connection.zone_a)

        self.data_map.adjacency = adjacency
        self._validate_path_exists(adjacency)

    def _validate_path_exists(self, adjacency: dict[str, list[str]]) -> None:
        """Validate that the graph is connected and has a path to the end."""

        if self.data_map.start is None or self.data_map.end is None:
            return

        visited: set[str] = set()
        stack: list[str] = [self.data_map.start]
        found_end = False

        while stack:
            current_zone = stack.pop()

            if current_zone in visited:
                continue

            visited.add(current_zone)

            if current_zone == self.data_map.end:
                found_end = True

            for neighbor in adjacency[current_zone]:
                if neighbor not in visited:
                    if self.data_map.zones[neighbor].zone_type != "blocked":
                        stack.append(neighbor)

        if not found_end:
            raise ParseError("No valid path from start_hub to end_hub")

        graph_zones = {
            zone_name for zone_name, zone in self.data_map.zones.items()
        }
        visited.update(
            zone_name
            for zone_name, zone in self.data_map.zones.items()
            if zone.zone_type == "blocked"
        )

        if visited != graph_zones:
            disconnected = graph_zones - visited
            raise ParseError(f"Disconnected zones: {disconnected}")

    def add_drones_to_map(self) -> None:
        self.data_map.drones = {
            drone_id: Drone(drone_id, [])
            for drone_id in range(1, self.data_map.nb_drones + 1)
        }
