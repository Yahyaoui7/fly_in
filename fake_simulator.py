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
