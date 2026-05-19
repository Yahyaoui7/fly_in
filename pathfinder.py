from model import Zone
from model import MapData
from model import Connection
import heapq


def get_zone_cost(zone: Zone) -> int:
    if zone.zone_type == "blocked":
        return float("inf")  # or Dijkstra can skip this zone entirely
    elif zone.zone_type == "restricted":
        return 2
    elif zone.zone_type in ("normal", "priority"):
        return 1


def dijkstra(map_data: MapData):
    start = map_data.start
    end = map_data.end
    adjacency = map_data.adjacency
    zones = map_data.zones

    distances = {zone: float("inf") for zone in zones}
    previous = {zone: None for zone in zones}

    distances[start] = 0

    heap = [(0, start)]
    visited = set()

    while heap:
        current_cost, node = heapq.heappop(heap)

        if node in visited:
            continue

        visited.add(node)

        if node == end:
            break

        for neighbor in adjacency[node]:

            if zones[neighbor].zone_type == "blocked":
                continue

            new_cost = current_cost + get_zone_cost(zones[neighbor])

            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                previous[neighbor] = node

                heapq.heappush(heap, (new_cost, neighbor))

    path = []
    current = end

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    return path
