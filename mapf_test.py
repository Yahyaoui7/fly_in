from mapf import prioritized_planning


graph = {
    "Start": {"A": 1, "C": 1},
    "A": {"B": 1},
    "C": {"B": 1},
    "B": {"Goal": 1},
    "Goal": {},
}

# Two agents with the same start/goal — prioritized planning will make the
# second agent wait or take a different schedule to avoid conflicts.
agents = [("Start", "Goal"), ("Start", "Goal")]

plans = prioritized_planning(graph, agents, max_time=20)
print("Plans:", plans)
