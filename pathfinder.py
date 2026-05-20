from model import MapData
import heapq

Graph = dict[str, dict[str, int]]
Edge = tuple[str, str]


class PathFinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def _edge_key(self, a: str, b: str) -> Edge:
        return tuple(sorted((a, b)))  # same key for A-B and B-A

    def dijkstra(
        self,
        start: str,
        goal: str,
        zone_penalty: dict[str, int],
        link_penalty: dict[Edge, int],
    ) -> list[str] | None:
        heap: list[tuple[int, str, list[str]]] = [(0, start, [start])]
        best_cost: dict[str, int] = {start: 0}

        while heap:
            cost, node, path = heapq.heappop(heap)

            if node == goal:
                return path

            if cost > best_cost.get(node, float("inf")):
                continue

            for neighbor, weight in self.graph[node].items():
                edge = self._edge_key(node, neighbor)

                extra_cost = zone_penalty.get(neighbor, 0) + link_penalty.get(
                    edge, 0
                )

                new_cost = cost + weight + extra_cost

                if new_cost < best_cost.get(neighbor, float("inf")):
                    best_cost[neighbor] = new_cost
                    heapq.heappush(
                        heap,
                        (new_cost, neighbor, path + [neighbor]),
                    )

        return None

    def find_multiple_paths(
        self,
        start: str,
        goal: str,
        count: int,
    ) -> list[list[str]]:
        paths: list[list[str]] = []
        zone_penalty: dict[str, int] = {}
        link_penalty: dict[Edge, int] = {}

        for _ in range(count):
            path = self.dijkstra(
                start,
                goal,
                zone_penalty,
                link_penalty,
            )

            if path is None or path in paths:
                break

            paths.append(path)

            for zone in path[1:-1]:
                zone_penalty[zone] = zone_penalty.get(zone, 0) + 3

            for a, b in zip(path, path[1:]):
                edge = self._edge_key(a, b)
                link_penalty[edge] = link_penalty.get(edge, 0) + 2

        return paths


# {
#     "start": {"A": 1, "C": 1},
#     "A": {"start": 1, "B": 2},
#     "B": {"A": 1, "goal": 1},
#     "C": {"start": 1, "D": 1},
#     "D": {"C": 1, "goal": 1},
#     "goal": {"B": 2, "D": 1},
# }


def graph_create(data_map: MapData) -> dict[str, dict[str, int]]:
    graph: dict[str, dict[str, int]] = {}

    for name, neighbors in data_map.adjacency.items():
        graph[name] = {}

        for neighbor in neighbors:
            if data_map.zones[neighbor].zone_type == "restricted":
                graph[name][neighbor] = 2
            else:
                graph[name][neighbor] = 1

    return graph
<<<<<<< HEAD



def dijkstra(start, end):
    heap = [(0, start, [satrt])]

    while heap: 
        current_cost, node, path = heapq.heappop(heap)

        for neighbor, weight in graph[node].items():
            pass
=======
>>>>>>> d4b43e9 (nathing)
