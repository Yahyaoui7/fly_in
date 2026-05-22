*This project has been created as part of the 42 curriculum by <your_login>.*

# Fly-in

## Description

Fly-in is a drone routing simulation project written in Python.

The goal of this project is to move multiple drones from a start hub to an end hub in the smallest possible number of simulation turns.

The map is represented as a graph:

- Zones are nodes.
- Connections are edges.
- Drones move from zone to zone.
- The simulation must respect capacity, movement cost, and collision rules.

---

## Features

- Object-oriented Python project
- Custom map parser
- Multi-drone simulation
- Turn-by-turn movement system
- Zone capacity handling
- Connection capacity handling
- Blocked zone avoidance
- Restricted zone movement cost
- Priority zone preference
- Waiting support
- Reservation system to prevent conflicts
- Pathfinding using `(zone, turn)` states
- Terminal output for drone movements
- Optional visual representation

---

## Project Structure

```text
.
├── main.py
├── parser.py
├── model.py
├── simulator.py
├── visualizer.py
├── maps/
├── Makefile
└── README.md
```

### File Roles

| File | Role |
|---|---|
| `main.py` | Program entry point |
| `parser.py` | Reads and validates map files |
| `model.py` | Contains main classes like `Zone`, `Connection`, `Drone`, and `MapData` |
| `simulator.py` | Handles pathfinding and simulation |
| `visualizer.py` | Shows the simulation visually or in terminal |
| `maps/` | Contains test map files |
| `Makefile` | Contains useful project commands |

---

## Map Format

Example map:

```text
nb_drones: 5

start_hub: start 0 0 [color=green max_drones=5]
end_hub: goal 10 10 [color=yellow]

hub: A 2 0 [zone=normal max_drones=1]
hub: B 4 0 [zone=priority max_drones=1]
hub: C 6 0 [zone=restricted max_drones=1]
hub: X 5 5 [zone=blocked color=gray]

connection: start-A
connection: A-B [max_link_capacity=2]
connection: B-C
connection: C-goal
```

---

## Zone Types

| Zone Type | Meaning | Movement Cost |
|---|---|---|
| `normal` | Standard zone | 1 turn |
| `priority` | Preferred zone | 1 turn |
| `restricted` | Dangerous/sensitive zone | 2 turns |
| `blocked` | Cannot be entered | Not allowed |

---

## Connection Capacity

Each connection can have a maximum capacity.

Example:

```text
connection: A-B [max_link_capacity=2]
```

This means only 2 drones can use the connection `A-B` during the same turn.

If no capacity is given, the default is:

```text
max_link_capacity = 1
```

---

## How to Run

Install dependencies:

```bash
make install
```

Run the program:

```bash
make run MAP=maps/easy/01_linear.txt
```

Or run directly:

```bash
python3 main.py maps/easy/01_linear.txt
```

Run lint:

```bash
make lint
```

Clean temporary files:

```bash
make clean
```

---

## Simulation Output

The simulation prints drone movements turn by turn.

Example:

```text
D1-A D2-B
D1-B D2-goal
D1-goal
```

Meaning:

```text
Turn 1: Drone 1 moves to A, Drone 2 moves to B
Turn 2: Drone 1 moves to B, Drone 2 reaches goal
Turn 3: Drone 1 reaches goal
```

Drones that do not move during a turn are not printed.

---

## Big Picture

The simulation works like this:

```text
MapData
   ↓
Simulator
   ↓
Find path for each drone
   ↓
Check if movement is valid
   ↓
Reserve zones and connections
   ↓
Print drone movements
```

The main idea is to avoid conflicts between drones.

A drone can move only if:

1. The destination zone is not blocked.
2. The connection exists.
3. The connection has free capacity.
4. The destination zone has free capacity at the arrival turn.
5. The move does not pass the maximum turn limit.

---

## Simulator

The `Simulator` class controls the simulation.

It stores:

```python
self.data_map
self.drones
self.reservation
```

Meaning:

```text
data_map     = map information
drones       = all drones
reservation  = used zones and connections
```

The simulator is responsible for:

- Checking if a drone can move
- Finding a path for a drone
- Booking zones
- Booking connections
- Avoiding collisions
- Managing turns

---

## Reservation Table

The `ReservationTable` remembers which zones and connections are already used.

### Zone Booking

```python
zone_bookings[(turn, zone)] = [drone_ids]
```

Example:

```python
zone_bookings[(2, "A")] = [1]
```

Meaning:

```text
At turn 2, Drone 1 is in zone A.
```

### Edge Booking

```python
edge_bookings[(turn, zone_a, zone_b)] = [drone_ids]
```

Example:

```python
edge_bookings[(3, "A", "B")] = [2]
```

Meaning:

```text
At turn 3, Drone 2 is using connection A-B.
```

---

## Edge Normalization

Connections are bidirectional.

This means:

```text
A-B
```

is the same as:

```text
B-A
```

To avoid duplicate keys, the simulator normalizes the connection:

```python
zone_a = min(from_zone, to_zone)
zone_b = max(from_zone, to_zone)
```

Example:

```python
_edge_key("B", "A")
```

returns:

```python
("A", "B")
```

So both directions use the same reservation key.

---

## Pathfinding Strategy

The pathfinder searches using states.

A state is:

```python
(zone, turn)
```

Example:

```python
("A", 2)
```

Meaning:

```text
The drone is in zone A at turn 2.
```

This is important because a zone may be full at one turn but free later.

---

## Priority Queue

The pathfinder uses a priority queue.

Each queue item has this format:

```python
(cost, penalty, turn, zone)
```

| Value | Meaning |
|---|---|
| `cost` | Total movement cost |
| `penalty` | Used to prefer priority zones |
| `turn` | Current simulation turn |
| `zone` | Current zone name |

Example:

```python
(2, 1, 2, "A")
```

Meaning:

```text
Cost is 2
Penalty is 1
Current turn is 2
Current zone is A
```

---

## Cost System

Movement cost depends on the destination zone.

```text
normal zone     = 1 turn
priority zone   = 1 turn
restricted zone = 2 turns
blocked zone    = not allowed
```

Example:

```python
if to_zone.zone_type == "restricted":
    arrival_turn = turn + 2
else:
    arrival_turn = turn + 1
```

---

## Priority Penalty

Priority zones are preferred by giving them a lower penalty.

```python
priority_penalty = 0 if to_zone.zone_type == "priority" else 1
```

Example:

```text
priority zone = penalty 0
normal zone   = penalty 1
```

So if two paths have the same cost, the path using priority zones is chosen first.

---

## Waiting Strategy

A drone can wait in the same zone for one turn.

This is useful when:

- The next zone is full.
- The connection is full.
- Moving now would cause a conflict.
- Waiting creates a better path later.

Example:

```text
Turn 1: Drone waits at A
Turn 2: Drone moves from A to B
```

Waiting is treated like another possible move.

---

## Movement Validation

Before moving, the simulator checks the move with `can_move`.

The method checks:

```text
1. Is the destination blocked?
2. Does the connection exist?
3. Is the connection available?
4. Is the destination zone available at arrival time?
```

Example:

```python
def can_move(self, turn, from_zone, to_zone):
    if to_zone.zone_type == "blocked":
        return False

    if not edge_is_available:
        return False

    if not zone_is_available:
        return False

    return True
```

---

## Booking a Move

After a path is found, the simulator must reserve it.

Booking means saving:

- The zone used by the drone
- The connection used by the drone
- The turn when it happens

Example path:

```python
[("start", 0), ("A", 1), ("goal", 2)]
```

Bookings:

```text
Turn 1: book connection start-A
Turn 1: book zone A
Turn 2: book connection A-goal
Turn 2: book zone goal
```

This prevents another drone from breaking capacity rules.

---

## Algorithm Steps

For each drone:

```text
1. Start from the start zone.
2. Add the start state to the priority queue.
3. Take the best state from the queue.
4. If the current zone is the end zone, rebuild the path.
5. Try waiting.
6. Try moving to each neighbor.
7. Check if the move is valid.
8. Calculate arrival turn.
9. Calculate score.
10. Save the best state.
11. Continue until a path is found.
12. Reserve the final path.
```

---

## Path Rebuilding

The algorithm stores parents.

Example:

```python
parent[("A", 1)] = ("start", 0)
parent[("goal", 2)] = ("A", 1)
```

This allows the simulator to rebuild the final path:

```python
[("start", 0), ("A", 1), ("goal", 2)]
```

---

## Complexity

Let:

```text
V = number of zones
E = number of connections
T = maximum number of turns
```

The algorithm searches states like:

```text
(zone, turn)
```

So the number of possible states is:

```text
O(V * T)
```

For each state, it checks neighbors.

Approximate complexity:

```text
O((V * T + E * T) log(V * T))
```

The `log` part comes from the priority queue.

---

## Visual Representation

The visual output helps understand the simulation.

It can show:

- Drone positions
- Zone colors
- Blocked zones
- Restricted zones
- Priority zones
- Current turn
- Drone movement
- Delivered drones

This helps during debugging and peer review.

---

## Error Handling

The parser should detect invalid input, such as:

- Missing `nb_drones`
- Invalid zone type
- Duplicate zones
- Duplicate connections
- Connection to unknown zone
- Invalid capacity
- Missing start hub
- Missing end hub
- Bad metadata syntax

When an error happens, the program should print a clear message.

---

## Performance Strategy

The simulator improves performance by:

- Using a priority queue
- Searching with `(zone, turn)` states
- Avoiding blocked zones early
- Preferring priority zones
- Checking zone capacity
- Checking connection capacity
- Allowing strategic waiting
- Reserving paths to prevent future conflicts

---

## AI Usage

AI was used as a learning assistant during development.

It helped with:

- Understanding pathfinding logic
- Understanding reservation tables
- Explaining edge capacity
- Explaining zone capacity
- Improving code structure
- Improving README structure
- Debugging errors

All AI-generated ideas were reviewed, tested, and adapted manually.

---

## Resources

- Python documentation: https://docs.python.org/3/
- heapq documentation: https://docs.python.org/3/library/heapq.html
- collections documentation: https://docs.python.org/3/library/collections.html
- mypy documentation: https://mypy.readthedocs.io/
- flake8 documentation: https://flake8.pycqa.org/
- Graph theory: https://en.wikipedia.org/wiki/Graph_theory
- Dijkstra algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

---

## Author

Created by:

```text
<your_login>
```
