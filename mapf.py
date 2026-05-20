from collections import deque
from typing import Dict, List, Tuple, Set

Graph = Dict[str, Dict[str, int]]
Agent = Tuple[str, str]


def _space_time_bfs(
    graph: Graph,
    start: str,
    goal: str,
    reservations_node: Set[Tuple[str, int]],
    reservations_edge: Set[Tuple[Tuple[str, str], int]],
    max_time: int,
) -> List[str] | None:
    """Simple BFS in space-time that respects node and edge reservations.

    Returns a list of nodes (one per timestep) when a solution is found,
    or None if no plan within `max_time` exists.
    """
    queue = deque()
    queue.append((start, 0, [start]))
    visited = set()
    visited.add((start, 0))

    while queue:
        node, t, path = queue.popleft()

        if node == goal:
            return path

        if t + 1 > max_time:
            continue

        # try moving to each neighbor
        for neighbor in graph.get(node, {}).keys():
            # node occupied at t+1?
            if (neighbor, t + 1) in reservations_node:
                continue

            # edge reserved at time t (u->v)
            if ((node, neighbor), t) in reservations_edge:
                continue

            # avoid head-on swap: someone moving neighbor->node at time t
            if ((neighbor, node), t) in reservations_edge:
                continue

            state = (neighbor, t + 1)
            if state in visited:
                continue

            visited.add(state)
            queue.append((neighbor, t + 1, path + [neighbor]))

        # wait in place
        if (node, t + 1) not in reservations_node:
            state = (node, t + 1)
            if state not in visited:
                visited.add(state)
                queue.append((node, t + 1, path + [node]))

    return None


def prioritized_planning(
    graph: Graph,
    agents: List[Agent],
    max_time: int = 50,
) -> List[List[str]] | None:
    """Plan paths for multiple agents using Prioritized Planning.

    Each agent is planned sequentially; earlier agents reserve nodes/edges
    in time to prevent conflicts for later agents.

    Returns a list of paths (list of node names per timestep) or None if
    any agent cannot be planned within `max_time`.
    """
    reservations_node: Set[Tuple[str, int]] = set()
    reservations_edge: Set[Tuple[Tuple[str, str], int]] = set()

    result_paths: List[List[str]] = []

    for idx, (start, goal) in enumerate(agents):
        path = _space_time_bfs(
            graph, start, goal, reservations_node, reservations_edge, max_time
        )

        if path is None:
            return None

        result_paths.append(path)

        # add node and edge reservations for this path
        for t, node in enumerate(path):
            reservations_node.add((node, t))
            if t > 0:
                prev = path[t - 1]
                reservations_edge.add(((prev, node), t - 1))

        # reserve goal for all future timesteps to avoid others entering it
        arrival = len(path) - 1
        for t in range(arrival, max_time + 1):
            reservations_node.add((goal, t))

    return result_paths


if __name__ == "__main__":
    # small demo when run directly
    graph = {
        "Start": {"A": 1, "C": 1},
        "A": {"B": 1},
        "C": {"B": 1},
        "B": {"Goal": 1},
        "Goal": {},
    }

    agents = [("Start", "Goal"), ("Start", "Goal")]
    plans = prioritized_planning(graph, agents, max_time=20)
    print(plans)
