from model import MapData

import heapq


class ReservationTable:

    def __init__(self, data_map: MapData) -> None:
        self.data_map: MapData = data_map
        self.zone_reservations: dict[int, dict[str, list[int]]] = {}
        self.edge_reservations: dict[int, dict[tuple[str, str], list[int]]] = (
            {}
        )
        self.edge_capacities: dict[tuple[str, str], int] = {
            self._edge_key(conn.zone_a, conn.zone_b): conn.max_link_capacity
            for conn in data_map.connections
        }

    def _edge_key(self, from_zone: str, to_zone: str) -> tuple[str, str]:
        return tuple(sorted((from_zone, to_zone)))

    def is_zone_available(self, zone: str, turn: int) -> bool:
        if zone == self.data_map.end or zone == self.data_map.start:
            return True  # Start and end zones have unlimited capacity
        capacity = self.data_map.zones[zone].max_drones
        reserved_drones = self.zone_reservations.get(turn, {}).get(zone, [])
        return len(reserved_drones) < capacity

    def is_edge_available(
        self, from_zone: str, to_zone: str, turn: int
    ) -> bool:
        edge_key = self._edge_key(from_zone, to_zone)
        capacity = self.edge_capacities.get(edge_key, None)
        if capacity is None:
            return False  # No connection between these zones
        reserved_drones = self.edge_reservations.get(turn, {}).get(
            edge_key, []
        )
        return len(reserved_drones) < capacity

    def reserve_zone(self, zone: str, turn: int, drone_id: int) -> None:
        if turn not in self.zone_reservations:
            self.zone_reservations[turn] = {}
        if zone not in self.zone_reservations[turn]:
            self.zone_reservations[turn][zone] = []
        self.zone_reservations[turn][zone].append(drone_id)

    def reserve_edge(
        self, from_zone: str, to_zone: str, turn: int, drone_id: int
    ) -> None:
        edge_key = self._edge_key(from_zone, to_zone)
        if turn not in self.edge_reservations:
            self.edge_reservations[turn] = {}
        if edge_key not in self.edge_reservations[turn]:
            self.edge_reservations[turn][edge_key] = []
        self.edge_reservations[turn][edge_key].append(drone_id)

    def reserve_path(self, drone_id: int, path: list[tuple[str, int]]) -> None:
        if not path:
            return

        start_zone, start_turn = path[0]
        self.reserve_zone(start_zone, start_turn, drone_id)

        for i in range(len(path) - 1):
            from_zone, from_turn = path[i]
            to_zone, to_turn = path[i + 1]

            # If drone waits in the same zone
            if from_zone == to_zone:
                self.reserve_zone(to_zone, to_turn, drone_id)
                continue

            # Reserve edge for every travel turn
            for turn in range(from_turn, to_turn):
                self.reserve_edge(from_zone, to_zone, turn, drone_id)

            # Reserve destination zone when drone arrives
            self.reserve_zone(to_zone, to_turn, drone_id)


class Simulator:
    def __init__(
        self, data_map: MapData, reservation_table: ReservationTable
    ) ->None:

        self.data_map = data_map
        self.reservation_table = reservation_table

    def get_arrival_turn(self, turn: int, to_zone: str) -> int:
        if self.data_map.zones[to_zone].zone_type == "restricted":
            return (
                turn + 2
            )  # Assume it takes 2 turns to pass through a restricted zone
        else:
            return turn + 1  # Normal zones take 1 turn to pass through

    def can_move(self, from_zone: str, to_zone: str, turn: int) -> bool:
        if self.data_map.zones[to_zone].zone_type == "blocked":
            return False
        arrive_turn = self.get_arrival_turn(turn, to_zone)

        for edge_turn in range(turn, arrive_turn):
            if not self.reservation_table.is_edge_available(
                from_zone, to_zone, edge_turn
            ):
                return False

        if not self.reservation_table.is_zone_available(to_zone, arrive_turn):
            return False

        return True

    def find_path_for_drone(
        self,
        start_zone: str,
        end_zone: str,
        max_turns: int,
    ) -> list[tuple[str, int]]:
        """Find a valid path for one drone using turn-based search."""
        queue = [(0, 0, start_zone, [])]
        visited: set[tuple[str, int]] = set()

        while queue:
            turn, priority_score, current_zone, path = heapq.heappop(queue)
            current_state = (current_zone, turn)

            if current_state in visited or turn > max_turns:
                continue
            visited.add(current_state)

            new_path = path + [(current_zone, turn)]

            if current_zone == end_zone:
                return new_path

            # Option 1: wait inside the current zone
            wait_turn = turn + 1
            if wait_turn <= max_turns:
                if self.reservation_table.is_zone_available(
                    current_zone,
                    wait_turn,
                ):
                    heapq.heappush(
                        queue,
                        (wait_turn, priority_score, current_zone, new_path),
                    )

            # Option 2: move to a connected zone
            for neighbor in self.data_map.adjacency.get(current_zone, []):
                arrival_turn = self.get_arrival_turn(turn, neighbor)

                if arrival_turn > max_turns:
                    continue

                if self.can_move(current_zone, neighbor, turn):
                    if self.data_map.zones[neighbor].zone_type == "priority":
                        zone_priority = (
                            0  # Prioritize paths through priority zones
                        )
                    else:
                        zone_priority = 1
                    new_priority_score = priority_score + zone_priority

                    heapq.heappush(
                        queue,
                        (arrival_turn, new_priority_score, neighbor, new_path),
                    )

        return []

    def plan_all_drones(self) -> dict[int, list[tuple[str, int]]]:
        drone_paths: dict[int, list[tuple[str, int]]] = {}
        max_turns = max(
            100, self.data_map.nb_drones * len(self.data_map.zones) * 5
        )
        if self.data_map.start is None or self.data_map.end is None:
            raise ValueError("Start or end zone is missing")

        for drone_id in range(1, self.data_map.nb_drones + 1):
            path = self.find_path_for_drone(
                self.data_map.start,
                self.data_map.end,
                max_turns,  # Example max_turns value
            )
            if not path:
                print(f"Warning: No path found for drone {drone_id}")
            else:
                self.reservation_table.reserve_path(drone_id, path)
            drone_paths[drone_id] = path
        return drone_paths

    def build_output(
        self,
        planned_paths: dict[int, list[tuple[str, int]]],
    ) -> list[str]:

        movements_by_turn: dict[int, list[str]] = {}
        for drone_id, path in planned_paths.items():
            for index in range(len(path) - 1):
                from_zone, from_turn = path[index]
                to_zone, to_turn = path[index + 1]

                # If drone waits, do not print anything
                if from_zone == to_zone:
                    continue

                # Normal move: takes 1 turn
                if to_turn == from_turn + 1:
                    movements_by_turn.setdefault(to_turn, []).append(
                        f"D{drone_id}-{to_zone}"
                    )
                    continue

                # Restricted move: drone is on connection first
                connection_name = f"{from_zone}-{to_zone}"
                duration = to_turn - from_turn
                if duration == 2:
                    movements_by_turn.setdefault(from_turn + 1, []).append(
                        f"D{drone_id}-{connection_name}"
                    )
                else:
                    raise ValueError("Invalid movement duration")

                # Arrival to restricted zone
                movements_by_turn.setdefault(to_turn, []).append(
                    f"D{drone_id}-{to_zone}"
                )

        if not movements_by_turn:
            return []

        output_lines: list[str] = []
        last_turn = max(movements_by_turn)

        for turn in range(1, last_turn + 1):
            line = " ".join(movements_by_turn.get(turn, []))
            output_lines.append(line)

        return output_lines
