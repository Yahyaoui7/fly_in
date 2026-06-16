*This project has been created as part of the 42 curriculum by nyahyaou.*

# Fly-in

## Description

Fly-in is a drone routing simulation project written in Python.

The goal of the project is to move multiple drones from a start hub to an end hub in the smallest possible number of simulation turns.

The map is represented as a graph:

* Zones are nodes.
* Connections are edges.
* Drones move from zone to zone.
* The simulation must respect zone capacity, connection capacity, movement costs, and collision rules.

The project is object-oriented, type-safe, and uses custom graph logic without graph libraries.

---

## Features

* Custom map parser
* Object-oriented design
* Multi-drone simulation
* Turn-by-turn movement output
* Zone capacity handling with `max_drones`
* Connection capacity handling with `max_link_capacity`
* Blocked zone avoidance
* Restricted zone movement cost
* Priority zone preference
* Waiting when movement is not possible
* Reservation system to avoid conflicts
* Pathfinding using `(zone, turn)` states
* Optional Pygame visual representation

---

## Project Structure

```text
.
├── main.py
├── parser.py
├── model.py
├── fake_simulator.py
├── visualiser.py
├── Makefile
├── requirements.txt
├── maps/
└── README.md
```

## File Roles

| File            | Role                                                                     |
| --------------- | ------------------------------------------------------------------------ |
| `main.py`       | Program entry point                                                      |
| `parser.py`     | Reads and validates map files                                            |
| `model.py`      | Stores data classes such as `Zone`, `Connection`, `Drone`, and `MapData` |
| `simulator.py`  | Handles pathfinding, reservations, and output generation                 |
| `visualiser.py` | Displays the map and drone movement visually                             |
| `maps/`         | Contains test map files                                                  |
| `Makefile`      | Contains useful project commands                                         |

---

## Instructions

### Install dependencies

```bash
make install
```

### Run the program

```bash
make run MAP=maps/easy/01_linear.txt
```

Or run directly:

```bash
python3 main.py maps/easy/01_linear.txt
```

### Run with visual mode

```bash
python3 main.py maps/easy/01_linear.txt --visual
```

### Run lint checks

```bash
make lint
```

### Clean temporary files

```bash
make clean
```

---

## Map Format

Example input:

```text
nb_drones: 3

start_hub: start 0 0 [color=green max_drones=3]
end_hub: goal 4 0 [color=yellow]

hub: A 1 0 [zone=normal max_drones=1]
hub: B 2 0 [zone=priority max_drones=1]
hub: C 3 0 [zone=restricted max_drones=1]
hub: X 2 2 [zone=blocked color=gray]

connection: start-A
connection: A-B [max_link_capacity=2]
connection: B-C
connection: C-goal
```

### Zone Types

| Zone Type    | Meaning                     | Movement Cost |
| ------------ | --------------------------- | ------------- |
| `normal`     | Standard zone               | 1 turn        |
| `priority`   | Preferred zone              | 1 turn        |
| `restricted` | Dangerous or sensitive zone | 2 turns       |
| `blocked`    | Cannot be entered           | Not allowed   |

### Metadata

Zones can have optional metadata:

```text
[color=green zone=priority max_drones=2]
```

Connections can have optional metadata:

```text
[max_link_capacity=2]
```

If no capacity is given:

```text
max_drones = 1
max_link_capacity = 1
```

The start and end zones have unlimited capacity.

---

## Example Output

For a valid simulation, the program prints drone movements turn by turn:

```text
D1-A D2-A
D1-B D2-B
D1-B-C D2-B-C
D1-C D2-C
D1-goal D2-goal
D3-A
D3-B
D3-B-C
D3-C
D3-goal
```

Each line is one simulation turn.

Example meaning:

```text
D1-A
```

means Drone 1 moved to zone `A`.

For restricted movement, the drone may be printed on a connection:

```text
D1-B-C
```

This means Drone 1 is still travelling on the connection from `B` to `C`.

Drones that do not move during a turn are not printed.

---

## Algorithm Explanation

The simulator uses a turn-based pathfinding approach.

Instead of searching only by zone, the algorithm searches by:

```text
(zone, turn)
```

This is important because a zone or connection may be full at one turn but free later.

Example state:

```text
("A", 3)
```

This means:

```text
The drone is in zone A at turn 3.
```

---

## Priority Queue

The pathfinder uses a priority queue with `heapq`.

A queue item has this format:

```python
(turn, action_score, priority_score, current_zone, path)
```

| Value            | Meaning                              |
| ---------------- | ------------------------------------ |
| `turn`           | Current simulation turn              |
| `action_score`   | Used to prefer moving before waiting |
| `priority_score` | Used to prefer priority zones        |
| `current_zone`   | Current zone name                    |
| `path`           | Path already taken                   |

The queue always chooses the smallest item first.

This means the algorithm prefers:

1. Earlier turns
2. Moving before waiting
3. Priority zones before normal zones

---

## Movement Cost

Movement cost depends on the destination zone:

```text
normal     = 1 turn
priority   = 1 turn
restricted = 2 turns
blocked    = not allowed
```

Example:

```python
if zone_type == "restricted":
    arrival_turn = turn + 2
else:
    arrival_turn = turn + 1
```

---

## Waiting Strategy

A drone can wait in the same zone for one turn.

Waiting is useful when:

* The next zone is full
* The connection is full
* Moving now would break a capacity rule
* Waiting gives a valid path later

Waiting is treated as another possible state in the queue.

Example:

```text
("A", 2) -> ("A", 3)
```

This means the drone waits in zone `A` for one turn.

---

## Reservation System

After a path is found for a drone, the simulator reserves the zones and connections used by that path.

This prevents future drones from breaking capacity rules.

### Zone reservation

Example:

```text
turn 2, zone A -> Drone 1
```

This means Drone 1 occupies zone `A` at turn 2.

### Connection reservation

Example:

```text
turn 3, connection A-B -> Drone 2
```

This means Drone 2 is using connection `A-B` at turn 3.

For restricted movement, the connection is reserved for multiple turns.

Example path:

```python
[("A", 0), ("B", 2)]
```

The connection `A-B` is reserved at:

```text
turn 0
turn 1
```

The drone arrives at `B` on turn 2.

---

## Conflict Handling

Before a drone moves, the simulator checks:

1. The destination zone is not blocked.
2. The connection exists.
3. The connection has free capacity.
4. The destination zone has free capacity at the arrival turn.
5. The movement does not exceed the maximum turn limit.

If any check fails, the move is not allowed.

---

## Algorithm Steps

For each drone:

1. Start at the start zone on turn 0.
2. Add the start state to the priority queue.
3. Pop the best state from the queue.
4. If the current zone is the end zone, return the path.
5. Try waiting in the current zone.
6. Try moving to each connected neighbor.
7. Check if each move is valid.
8. Calculate the arrival turn.
9. Add valid future states to the queue.
10. Reserve the final path.
11. Continue until all drones have a path.

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

So the number of possible states is approximately:

```text
O(V * T)
```

For each state, the algorithm may check connected neighbors.

Approximate complexity:

```text
O((V * T + E * T) log(V * T))
```

The `log` part comes from the priority queue.

---

## Visual Representation

The project includes an optional Pygame visualizer.

The visualizer helps the user understand the simulation by showing:

* Zones as circles
* Connections as lines
* Drones as small moving circles
* Zone colors from metadata
* Blocked zones visually
* Restricted and priority zones
* Current simulation turn
* Drone positions over time
* Camera movement with arrow keys
* Step-by-step simulation using the space key

Zone size can also represent capacity:

```text
higher max_drones -> bigger zone circle
```

This makes the simulation easier to debug and easier to explain during peer review.

---

## Visual Controls

| Key          | Action                              |
| ------------ | ----------------------------------- |
| `SPACE`      | Move simulation forward by one turn |
| `Arrow keys` | Move the camera                     |
| `ESC`        | Close the visualizer                |

---

## Error Handling

The parser detects invalid input and raises clear errors.

Examples of handled errors:

* Missing `nb_drones`
* Missing `start_hub`
* Missing `end_hub`
* Duplicate zone names
* Duplicate connections
* Invalid zone type
* Invalid capacity value
* Invalid metadata syntax
* Connection to an unknown zone
* Blocked start or end zone
* No valid path from start to end
* Disconnected usable zones

---

## Performance Strategy

The simulator improves performance by:

* Using a priority queue
* Searching with `(zone, turn)` states
* Avoiding blocked zones early
* Preferring priority zones
* Checking capacity before moving
* Allowing strategic waiting
* Reserving paths after they are found
* Preventing future conflicts with the reservation table

---

## AI Usage

AI was used as a learning assistant during development.

It helped with:

* Understanding pathfinding logic
* Understanding Dijkstra-style search
* Understanding reservation tables
* Explaining zone capacity
* Explaining connection capacity
* Improving README structure
* Debugging type hint and mypy errors
* Improving code clarity

All AI-generated ideas were reviewed, tested, and adapted manually.

---

## Resources

## Resources

- Python documentation: https://docs.python.org/3/
- heapq documentation: https://docs.python.org/3/library/heapq.html
- dataclasses documentation: https://docs.python.org/3/library/dataclasses.html
- mypy documentation: https://mypy.readthedocs.io/
- flake8 documentation: https://flake8.pycqa.org/
- Dijkstra algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

AI was used to help understand pathfinding, reservation tables, type hints, mypy errors, and README structure.

---
