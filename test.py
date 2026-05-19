# Zones and connections
zones = {
    "Start": {"capacity": 3, "current": []},
    "A": {"capacity": 1, "current": []},
    "B": {"capacity": 1, "current": []},
    "C": {"capacity": 1, "current": []},
    "Goal": {"capacity": float("inf"), "current": []},
}

connections = {
    "Start": ["A", "C"],
    "A": ["B"],
    "C": ["B"],
    "B": ["Goal"],
}

# Drones
drones = [
    {"id": "D1", "position": "Start", "path": []},
    {"id": "D2", "position": "Start", "path": []},
    {"id": "D3", "position": "Start", "path": []},
]

# Simple shortest path (manually for small graph)


import heapq

# Graph with possible multiple paths
graph = {
    "Start": {"A": 1, "C": 1},
    "A": {"B": 1},
    "B": {"Goal": 1},
    "C": {"B": 1},
    "Goal": {},
}


# Simple function to find one shortest path
def dijkstra(graph, start, goal, blocked=set()):
    heap = [(0, start, [start])]
    visited = set()

    while heap:
        cost, node, path = heapq.heappop(heap)
        if node == goal:
            return path
        if node in visited:
            continue
        visited.add(node)
        for neighbor, w in graph[node].items():
            if neighbor not in visited and neighbor not in blocked:
                heapq.heappush(heap, (cost + w, neighbor, path + [neighbor]))
    return None


# Generate multiple paths for drones
shortest_paths = {}
blocked_nodes = set()
for i, drone in enumerate(["D1", "D2", "D3"]):
    path = dijkstra(graph, "Start", "Goal", blocked_nodes)
    if not path:
        # fallback if no unique path found
        path = dijkstra(graph, "Start", "Goal")
    shortest_paths[drone] = path
    # block intermediate nodes to force next drone to take different path
    blocked_nodes.update(path[1:-1])

print(shortest_paths)


# Booking system simulation
turn = 1
finished = False
while not finished:
    print(f"Turn {turn}: ", end="")
    moves = []
    finished = True
    for drone in drones:
        path = shortest_paths[drone["id"]]
        pos_index = path.index(drone["position"])
        if pos_index < len(path) - 1:
            next_zone = path[pos_index + 1]
            # Check capacity
            if len(zones[next_zone]["current"]) < zones[next_zone]["capacity"]:
                # Move drone
                (
                    zones[drone["position"]]["current"].remove(drone["id"])
                    if drone["id"] in zones[drone["position"]]["current"]
                    else None
                )
                zones[next_zone]["current"].append(drone["id"])
                drone["position"] = next_zone
                moves.append(f"{drone['id']}->{next_zone}")
            else:
                # Wait in current zone
                (
                    zones[drone["position"]]["current"].append(drone["id"])
                    if drone["id"] not in zones[drone["position"]]["current"]
                    else None
                )
        if drone["position"] != "Goal":
            finished = False
    print(" ".join(moves))
    turn += 1
