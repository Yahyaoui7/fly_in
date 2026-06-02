<<<<<<< HEAD
# ReservationTable = checks and saves reservations
# Simulator = runs turns and moves drones
from model import Drone, MapData


class ReservationTable:
    def __init__(self):
        self.zone_bookings: dict[tuple[int, str], list[int]] = {}
        self.edge_bookings: dict[tuple[int, str, str], list[int]] = {}


class Simulator:
    def __init__(self, data_map):
        self.data_map: MapData = data_map
        self.drones: list = [Drone(i + 1, []) for i in range(data_map.nb_drones)]

    def plan_all_drones(self):

        for drone in self.drones:
            pass
=======

from model import MapData, Zone, Connection

import heapq
# ReservationTable = checks and saves reservations
# Simulator = runs turns and moves drones

# self.zone_reservations = {
#     1: {
#         "roof1": [1],
#         "corridorA": [2, 3],
#     },
#     2: {
#         "roof2": [1],
#     },
# }


# self.edge_reservations = {
#     1: {
#         ("hub", "roof1"): [1],
#         ("hub", "corridorA"): [2],
#     },
#     2: {
#         ("roof1", "roof2"): [1],
#     },
# }

class ReservationTable:
    def __init__(self, data_map):
        self.data_map: MapData = data_map
        self.zone_reservations = {}
        self.edge_reservations = {}
        self.edge_capacities = {self._edge_key(conn.zone_a, conn.zone_b): conn.max_link_capacity for conn in data_map.connections}


    def _edge_key(self, from_zone, to_zone):
        return tuple(sorted((from_zone, to_zone)))
    
    def is_zone_available(self, zone: str, turn: int) -> bool:
        if zone == self.data_map.end or zone == self.data_map.start:
            return True  # Start and end zones have unlimited capacity
        capacity  = self.data_map.zones[zone].capacity
        reserved_drones = self.zone_reservations.get(turn, {}).get(zone, [])
        return len(reserved_drones) < capacity
    

    def is_edge_available(self, from_zone: str, to_zone: str, turn: int) -> bool:
        edge_key = self._edge_key(from_zone, to_zone)
        capacity = self.edge_capacities.get(edge_key, None)
        if capacity is None:
            return False  # No connection between these zones
        reserved_drones = self.edge_reservations.get(turn, {}).get(edge_key, [])
        return len(reserved_drones) < capacity  
    
    def reserve_zone(self, zone: str, turn: int, drone_id: int):
        if turn not in self.zone_reservations:
            self.zone_reservations[turn] = {}
        if zone not in self.zone_reservations[turn]:
            self.zone_reservations[turn][zone] = []
        self.zone_reservations[turn][zone].append(drone_id)

    def reserve_edge(self, from_zone: str, to_zone: str, turn: int, drone_id: int):
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
    def __init__(self, data_map: MapData, reservation_table: ReservationTable):
        self.data_map = data_map
        self.reservation_table = reservation_table

    def get_arrival_turn(self, turn: int, to_zone: str) -> int:
        if self.data_map.zones[to_zone].zone_type == "restricted":
            return turn + 2  # Assume it takes 2 turns to pass through a restricted zone
        else:
            return turn + 1  # Normal zones take 1 turn to pass through
        
        
    def can_move(self, from_zone: str, to_zone: str, turn: int) -> bool:
        if self.data_map.zones[to_zone].zone_type == "blocked":
            return False
        arrive_turn = self.get_arrival_turn(turn, to_zone)
        
        for edge_turn in range(turn, arrive_turn):
            if not self.reservation_table.is_edge_available(from_zone, to_zone,edge_turn):
                return False
            
        if not self.reservation_table.is_zone_available(to_zone, arrive_turn):
            return False

        return True
    
    def find_path_for_drone(
        self,
        drone_id: int,
        start_zone: str,
        end_zone: str,
        max_turns: int,
    ) -> list[tuple[str, int]]:
        queue = [(0, start_zone, [])]
        visited = set()

        while queue:
            turn, current_zone, path = heapq.heappop(queue)

            if turn > max_turns:
                continue

            if (current_zone, turn) in visited:
                continue

            visited.add((current_zone, turn))
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
                        (wait_turn, current_zone, new_path),
                    )

            # Option 2: move to a connected zone
            for neighbor in self.data_map.adjacency.get(current_zone, []):
                if self.can_move(current_zone, neighbor, turn):
                    arrival_turn = self.get_arrival_turn(turn, neighbor)

                    if arrival_turn <= max_turns:
                            heapq.heappush(
                                queue,
                                (arrival_turn, neighbor, new_path),
                            )

        return []
>>>>>>> c4182be (recreate fake simulator)
