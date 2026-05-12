from pathlib import Path
from typing import Callable

from model import Connection, Zone

Line = tuple[str, int]
ParserFunction = Callable[[Line, str], None]
zone: dict[str, tuple | dict] = {
    "name": None,
    "coordinates": None,
    "data": {"zone": "normal", "color": None, "max_drones": 1},
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

    def parse(self) -> None:
        with open(self.file_path, "r", encoding="utf-8") as file:
            raw_lines = file.readlines()

        numbered_lines = self._add_number_of_line(raw_lines)
        valid_lines = self._remove_comments(numbered_lines)

        self._parser_all(valid_lines)

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

            valid_meta_data = fun(kind.strip(), meta_data, line_number)
            print(valid_meta_data, end="\n\n")

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

    def _parse_zone(self, kind, meta_data, line_number: int) -> None:
        meta = meta_data.strip()
        config = meta.split(" ", 3)

        this_zone = zone
        if kind == "start_hub":
            if self.start is not None:
                raise ValueError(
                    f"Line {line_number}: start zone is duplicate !!"
                )
            else:
                this_zone["name"] = config[0]
                this_zone["coordinates"] = self._parse_coordinates(
                    config[1], config[2], line_number
                )

                if "[" in meta_data and "]" in meta_data:

                    this_zone["data"] = self._parse_metadata(
                        config[3], line_number
                    )

        elif kind == "end_hub":
            if self.end is not None:
                raise ValueError(
                    f"Line {line_number}: start zone is duplicate !!"
                )
            else:
                this_zone["name"] = config[0]
                this_zone["coordinates"] = self._parse_coordinates(
                    config[1], config[2], line_number
                )

                if "[" in meta_data and "]" in meta_data:

                    this_zone["data"] = self._parse_metadata(
                        config[3], line_number
                    )

        else:
            this_zone["name"] = config[0]
            this_zone["coordinates"] = self._parse_coordinates(
                config[1], config[2], line_number
            )

            if "[" in meta_data and "]" in meta_data:

                this_zone["data"] = self._parse_metadata(
                    config[3], line_number
                )
        print(type(this_zone))
        return this_zone

    def _parse_coordinates(self, x, y, line_number):
        try:
            x = int(x)
            y = int(y)
        except ValueError:
            raise ValueError(
                f"Line {line_number}: this coordinates is not valid"
            )
        return x, y

    def _parse_metadata(self, data, line_number):
        deffult: dict = {"zone": "normal", "color": None, "max_drones": 1}
        lst: list = [
            "zone",
            "color",
            "max_drones",
        ]
        valid_zone = ["normal", "blocked", "restricted", "priority"]
        data = data.replace("[", "").replace("]", "").strip()

        meta = data.split(" ")
        for ta in meta:
            ta = ta.split("=")
            if ta[0] in lst:
                if ta[0] == "zone":
                    if ta[1] in valid_zone:
                        deffult["zone"] = ta[1]
                    else:
                        raise ValueError(
                            f"Line {line_number}: value of zone not valid ?"
                        )

                elif ta[0] == "max_drones":
                    deffult["max_drones"] = self._check_valid_number(
                        ta[1], line_number
                    )
                elif ta[0] == "color":
                    deffult["color"] = ta[1]
            else:
                raise ValueError(
                    f"Line {line_number}: this metadata not valid ??"
                )
        return deffult

    def _check_valid_number(self, number, line_number):
        try:
            number = int(number)
            if number <= 0:
                raise ValueError(
                    f"Line {line_number}: value of max_drones should be positive"
                )
        except ValueError:
            raise (f"Line {line_number}: value of max_drones should be int")
        return number

    def _parse_connection(self, kind, meta_data, line_number: int) -> None:
        meta = meta_data.strip()
        config = meta.split(" ")
        return meta_data

    def _validate_final_result():
        pass
