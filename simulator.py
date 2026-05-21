from model import Drone, MapData, Connection, Zone


class Simulator:
    def __init__(self, data_map, path):
        self.data_map: MapData = data_map
        self.drones = [Drone(i + 1, path) for i in range(data_map.nb_drones)]
        self.reservation = ReservationTable()

    def can_move(self, turn, from_zone: Zone, to_zone: Zone, drone_id):
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
        if not self.reservation.is_zone_available(
            turn, to_zone, to_zone.max_drones
        ):
            return False
        return True

    def _edge_key(self, zone_a, zone_b):
        zone_one = min(zone_a, zone_b)
        zone_two = max(zone_a, zone_b)
        return zone_one, zone_two


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
