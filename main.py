import sys
from pathlib import Path

from parser import MapParser
from errors import ParseError
from fake_simulator import Simulator
from fake_simulator import ReservationTable
from visualiser import Visualization


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        return 1

    file_path = Path(sys.argv[1])
    try:
        Map = MapParser(file_path)
        Map.parse()
        data_map = Map.data_map
        simulator = Simulator(data_map, ReservationTable(data_map))
        path = simulator.plan_all_drones()
        print(path)

        lines = simulator.build_output(path)
        # for line in lines:
        #     print(line)
        va = Visualization(data_map, len(lines))
        va.display()
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}")
        return 1
    except PermissionError:
        print(f"Error: permission denied: {file_path}")
        return 1
    except ValueError as e:
        print(f"Error: ValueError {e}")
        return 1
    except ParseError as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
