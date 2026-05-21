from model import Drone, MapData, Connection, Zone
import heapq
from collections import deque
State = tuple[str, int]
Score = tuple[int, int]
class Simulator:
    def __init__(self, data_map, path):
        self.data_map: MapData = data_map
        self.drones = [Drone(i + 1, path) for i in range(data_map.nb_drones)]
        self.reservation = ReservationTable()


    def can_move(self, turn, from_zone: Zone, to_zone: Zone) -> bool:
        capacity = None
        zones = self._edge_key(from_zone.name, to_zone.name)
        for connection in self.data_map.connections:
            key = self._edge_key(connection.zone_a, connection.zone_b)
            if key == zones:
                capacity = connection.max_link_capacity

        if capacity is None:
            return False

        if to_zone.zone_type == "blocked":
            return False
        if not self.reservation.is_edge_available(
            turn, from_zone.name, to_zone.name, capacity
        ):
            return False
        if to_zone.zone_type == "restricted":
            arrival_turn = turn + 2
        else:
            arrival_turn = turn + 1
        if not self.reservation.is_zone_available(
            arrival_turn, to_zone.name, to_zone.max_drones
        ):
            return False
        return True

    def _edge_key(self, zone_a, zone_b):
        zone_one = min(zone_a, zone_b)
        zone_two = max(zone_a, zone_b)
        return zone_one, zone_two

    def book_move(
    self,
    turn: int,
    from_zone: Zone,
    to_zone: Zone,
    drone_id: int,
) -> None:
    pass


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

        best_score: dict[State, Score] = {
            start_state: (0, 0)
        }

        parent: dict[State, State | None] = {
            start_state: None
        }

        while queue:
            cost, penalty, turn, current_zone = heapq.heappop(queue)
            current_state = (current_zone, turn)

            if best_score[current_state] != (cost, penalty):
                continue

            if current_zone == end_zone:
                return self._rebuild_path(parent, current_state)

            if turn >= max_turns:
                continue

            # Option 1: wait
            wait_turn = turn + 1
            wait_state = (current_zone, wait_turn)

            if wait_turn <= max_turns and self._can_stay(wait_turn, current_zone):
                wait_score = (cost + 1, penalty + 1)

                if self._is_better(wait_score, best_score.get(wait_state)):
                    best_score[wait_state] = wait_score
                    parent[wait_state] = current_state
                    heapq.heappush(
                        queue,
                        (wait_score[0], wait_score[1], wait_turn, current_zone),
                    )

            # Option 2: move to neighbors
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

        return (turn, zone_a, zone_b)
