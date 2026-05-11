from pathlib import Path
from typing import Callable

from model import Connection, Zone

Line = tuple[str, int]
ParserFunction = Callable[[Line, str], None]
zone: dict[str, tuple | dict] = {
    "name": None,
    "coordinates": None,
    "data": {"zone": "normal",
             "color": None,
             "max_drones": 1}
}


class MapParser:
    def __init__(self, file_path: str | Path) -> None:
        self.file_path = file_path
        self.nb_drones: int | None = None
        self.start: dict | None = None
        self.end: dict | None = None
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.connection_keys: set[frozenset[str]] = set()

        self.funs_of_parser: dict[str, ParserFunction] = {
            "start_hub": self._parse_zone,
            "hub": self._parse_zone,
            "end_hub": self._parse_zone,
            "connection": self._parse_connection,
        }

    def parse(self) -> None:
        with open(self.file_path, "r", encoding="utf-8") as file:
            raw_lines = file.readlines()

        numbered_lines = self._add_number_of_line(raw_lines)
        valid_lines = self._remove_comments(numbered_lines)

        self._parser_all(valid_lines)

    def _add_number_of_line(self, lines: list[str]) -> list[Line]:
        numbered_lines: list[Line] = []

        for index, line in enumerate(lines, start=1):
            numbered_lines.append((line, index))

        return numbered_lines

    def _remove_comments(self, lines: list[Line]) -> list[Line]:
        valid_lines: list[Line] = []

        for line_text, line_number in lines:
            clean_line = line_text.split("#", 1)[0].strip()

            if clean_line:
                valid_lines.append((clean_line, line_number))

        return valid_lines

    def _parse_nb_drones(self, line: Line) -> None:
        line_text, line_number = line

        if ":" not in line_text:
            raise ValueError(f"Line {line_number}: missing ':'")

        name, value_text = line_text.split(":", 1)

        if name.strip() != "nb_drones":
            raise ValueError(
                f"Line {line_number}: expected 'nb_drones', got '{name.strip()}'"
            )

        try:
            value = int(value_text.strip())
        except ValueError:
            raise ValueError(
                f"Line {line_number}: nb_drones must be an integer"
            )

        if value <= 0:
            raise ValueError(
                f"Line {line_number}: nb_drones must be greater than 0"
            )

        self.nb_drones = value

    def _parser_all(self, lines: list[Line]) -> None:
        if not lines:
            raise ValueError("File is empty or contains only comments")

        self._parse_nb_drones(lines[0])

        for line in lines[1:]:
            line_text, line_number = line

            if ":" not in line_text:
                raise ValueError(f"Line {line_number}: missing ':'")

            data = line_text.split(":", 1)
            kind, meta_data = data

            fun = self.funs_of_parser.get(kind.strip())

            if fun is None:
                raise ValueError(
                    f"Line {line_number}: invalid line type '{kind.strip()}'"
                )

            fun(kind.strip(), meta_data, line_number)

    def _parse_zone(self, kind, meta_data, line_number: int) -> None:
        if kind == "start_hub":
            if self.start is not None:
                raise ValueError(f"Line {line_number}: start zone is duplicate !!")
        else:
            

        print("ZONE:",line)

    def _parse_connection(self, line: Line,) -> None:
        print("CONNECTION:",line)

    def _parse_metadata():
        pass

    def _validate_final_result():
        pass
