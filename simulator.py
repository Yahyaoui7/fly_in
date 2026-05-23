import heapq

from model import Drone, MapData, Zone

State = tuple[str, int]
Score = tuple[int, int]


class ReservationTable:
    def __init__(self) -> None:
        self.zone_bookings: dict[tuple[int, str], list[int]] = {}
        self.edge_bookings: dict[tuple[int, str, str], list[int]] = {}

    def is_zone_available(
        self,
        turn: int,
        zone: str,
        capacity: int,
    ) -> bool:
        key = (turn, zone)
        drones = self.zone_bookings.get(key, [])

        return len(drones) < capacity

    def book_zone(self, turn: int, zone: str, drone_id: int) -> None:
        key = (turn, zone)

        if key not in self.zone_bookings:
            self.zone_bookings[key] = []

        self.zone_bookings[key].append(drone_id)

    def is_edge_available(
        self,
        turn: int,
        from_zone: str,
        to_zone: str,
        capacity: int,
    ) -> bool:
        key = self._edge_key(turn, from_zone, to_zone)
        drones = self.edge_bookings.get(key, [])

        return len(drones) < capacity

    def book_edge(
        self,
        turn: int,
        from_zone: str,
        to_zone: str,
        drone_id: int,
    ) -> None:
        key = self._edge_key(turn, from_zone, to_zone)

        if key not in self.edge_bookings:
            self.edge_bookings[key] = []

        self.edge_bookings[key].append(drone_id)

    def _edge_key(
        self,
        turn: int,
        from_zone: str,
        to_zone: str,
    ) -> tuple[int, str, str]:
        zone_a = min(from_zone, to_zone)
        zone_b = max(from_zone, to_zone)

        return turn, zone_a, zone_b


class Simulator:
    def __init__(self, data_map: MapData, path: list[str]) -> None:
        self.data_map: MapData = data_map
        self.drones: list[Drone] = [
            Drone(i + 1, path) for i in range(data_map.nb_drones)
        ]
        self.reservation = ReservationTable()

    def can_move(
        self,
        turn: int,
        from_zone: Zone,
        to_zone: Zone,
    ) -> bool:
        capacity = self._get_edge_capacity(from_zone.name, to_zone.name)

        if capacity is None:
            return False

        if to_zone.zone_type == "blocked":
            return False

        arrival_turn = self.get_arrival_turn(turn, to_zone)

        for edge_turn in range(turn, arrival_turn):
            if not self.reservation.is_edge_available(
                edge_turn,
                from_zone.name,
                to_zone.name,
                capacity,
            ):
                return False

        if to_zone.name == self.data_map.end:
            return True

        return self.reservation.is_zone_available(
            arrival_turn,
            to_zone.name,
            to_zone.max_drones,
        )

    def book_move(
        self,
        turn: int,
        from_zone: Zone,
        to_zone: Zone,
        drone_id: int,
    ) -> None:
        arrival_turn = self.get_arrival_turn(turn, to_zone)

        for edge_turn in range(turn, arrival_turn):
            self.reservation.book_edge(
                edge_turn,
                from_zone.name,
                to_zone.name,
                drone_id,
            )

        if to_zone.name != self.data_map.end:
            self.reservation.book_zone(
                arrival_turn,
                to_zone.name,
                drone_id,
            )

    def book_path(
        self,
        drone_id: int,
        path: list[tuple[str, int]],
    ) -> None:
        for index in range(len(path) - 1):
            current_zone_name, current_turn = path[index]
            next_zone_name, next_turn = path[index + 1]

            if current_zone_name == next_zone_name:
                if next_zone_name not in (
                    self.data_map.start,
                    self.data_map.end,
                ):
                    self.reservation.book_zone(
                        next_turn,
                        next_zone_name,
                        drone_id,
                    )
                continue

            from_zone = self.data_map.zones[current_zone_name]
            to_zone = self.data_map.zones[next_zone_name]

            self.book_move(
                current_turn,
                from_zone,
                to_zone,
                drone_id,
            )

    def find_path_for_drone(
        self,
        drone_id: int,
        start_zone: str,
        end_zone: str,
        start_turn: int,
        max_turns: int,
    ) -> list[tuple[str, int]]:
        start_state = (start_zone, start_turn)

        queue: list[tuple[int, int, int, str]] = [
            (0, 0, start_turn, start_zone)
        ]

        best_score: dict[State, Score] = {start_state: (0, 0)}

        parent: dict[State, State | None] = {start_state: None}

        while queue:
            cost, penalty, turn, current_zone = heapq.heappop(queue)
            current_state = (current_zone, turn)

            if best_score[current_state] != (cost, penalty):
                continue

            if current_zone == end_zone:
                return self._rebuild_path(parent, current_state)

            if turn >= max_turns:
                continue

            wait_turn = turn + 1
            wait_state = (current_zone, wait_turn)

            if wait_turn <= max_turns and self._can_stay(
                wait_turn,
                current_zone,
            ):
                wait_score = (cost + 1, penalty + 1)

                if self._is_better(wait_score, best_score.get(wait_state)):
                    best_score[wait_state] = wait_score
                    parent[wait_state] = current_state
                    heapq.heappush(
                        queue,
                        (
                            wait_score[0],
                            wait_score[1],
                            wait_turn,
                            current_zone,
                        ),
                    )

            for neighbor in self.data_map.adjacency[current_zone]:
                from_zone = self.data_map.zones[current_zone]
                to_zone = self.data_map.zones[neighbor]

                if not self.can_move(turn, from_zone, to_zone):
                    continue

                arrival_turn = self.get_arrival_turn(turn, to_zone)

                if arrival_turn > max_turns:
                    continue

                move_cost = arrival_turn - turn
                priority_penalty = 0 if to_zone.zone_type == "priority" else 1

                next_state = (neighbor, arrival_turn)
                next_score = (cost + move_cost, penalty + priority_penalty)

                if self._is_better(next_score, best_score.get(next_state)):
                    best_score[next_state] = next_score
                    parent[next_state] = current_state
                    heapq.heappush(
                        queue,
                        (
                            next_score[0],
                            next_score[1],
                            arrival_turn,
                            neighbor,
                        ),
                    )

        return []

    def plan_all_drones(
        self,
        max_turns: int,
    ) -> dict[int, list[tuple[str, int]]]:

        planned_paths: dict[int, list[tuple[str, int]]] = {}

        for drone in self.drones:
            drone_id = drone.id

            path = self.find_path_for_drone(
                drone_id=drone_id,
                start_zone=self.data_map.start,
                end_zone=self.data_map.end,
                start_turn=0,
                max_turns=max_turns,
            )

            if not path:
                raise RuntimeError(f"No path found for drone {drone_id}")

            planned_paths[drone_id] = path
            drone.path = [zone_name for zone_name, _turn in path]

            self.book_path(drone_id, path)

        return planned_paths

    def build_output(
        self,
        planned_paths: dict[int, list[tuple[str, int]]],
    ) -> list[str]:
        movements_by_turn: dict[int, list[str]] = {}

        for drone_id, path in planned_paths.items():
            for index in range(len(path) - 1):
                from_zone, from_turn = path[index]
                to_zone, to_turn = path[index + 1]

                if from_zone == to_zone:
                    continue

                if to_turn == from_turn + 1:
                    movements_by_turn.setdefault(to_turn, []).append(
                        f"D{drone_id}-{to_zone}"
                    )
                    continue

                for turn in range(from_turn + 1, to_turn):
                    connection_name = f"{from_zone}-{to_zone}"
                    movements_by_turn.setdefault(turn, []).append(
                        f"D{drone_id}-{connection_name}"
                    )

                movements_by_turn.setdefault(to_turn, []).append(
                    f"D{drone_id}-{to_zone}"
                )

        if not movements_by_turn:
            return []

        last_turn = max(movements_by_turn)
        output_lines: list[str] = []

        for turn in range(1, last_turn + 1):
            moves = movements_by_turn.get(turn, [])
            output_lines.append(" ".join(moves))

        return output_lines

    def get_arrival_turn(self, turn: int, to_zone: Zone) -> int:
        if to_zone.zone_type == "restricted":
            return turn + 2

        return turn + 1

    def _can_stay(self, turn: int, zone_name: str) -> bool:
        if zone_name == self.data_map.start:
            return True

        if zone_name == self.data_map.end:
            return True

        zone = self.data_map.zones[zone_name]

        if zone.zone_type == "blocked":
            return False

        return self.reservation.is_zone_available(
            turn,
            zone.name,
            zone.max_drones,
        )

    def _get_edge_capacity(
        self,
        zone_a: str,
        zone_b: str,
    ) -> int | None:
        wanted_key = self._edge_key(zone_a, zone_b)

        for connection in self.data_map.connections:
            connection_key = self._edge_key(
                connection.zone_a,
                connection.zone_b,
            )

            if connection_key == wanted_key:
                return connection.max_link_capacity

        return None

    def _edge_key(self, zone_a: str, zone_b: str) -> tuple[str, str]:
        zone_one = min(zone_a, zone_b)
        zone_two = max(zone_a, zone_b)

        return zone_one, zone_two

    def _is_better(
        self,
        new_score: Score,
        old_score: Score | None,
    ) -> bool:
        return old_score is None or new_score < old_score

    def _rebuild_path(
        self,
        parent: dict[State, State | None],
        end_state: State,
    ) -> list[tuple[str, int]]:
        path: list[tuple[str, int]] = []
        current: State | None = end_state

        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()
        return path
