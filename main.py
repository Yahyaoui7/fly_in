import sys
from pathlib import Path

from parser import MapParser


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        return 1

    file_path = Path(sys.argv[1])

    try:
        parser = MapParser(file_path)
        parser.parse()
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}")
        return 1
    except PermissionError:
        print(f"Error: permission denied: {file_path}")
        return 1
    except ValueError as e:
        print(f"Error : {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
