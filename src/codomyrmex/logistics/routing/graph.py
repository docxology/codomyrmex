"""Graph-based routing algorithms (Dijkstra, A*)."""

import heapq
import math


class DijkstraRouting:
    """Dijkstra's shortest path algorithm for graph-based routing."""

    def __init__(self) -> None:
        self.graph: dict[str, dict[str, float]] = {}

    def add_edge(self, from_id: str, to_id: str, distance: float, bidirectional: bool = True) -> None:
        self.graph.setdefault(from_id, {})[to_id] = distance
        if bidirectional:
            self.graph.setdefault(to_id, {})[from_id] = distance

    def shortest_path(self, start_id: str, end_id: str) -> tuple[list[str], float]:
        if start_id not in self.graph:
            return [], float("inf")
        distances = {node: float("inf") for node in self.graph}
        distances[start_id] = 0
        previous: dict[str, str | None] = dict.fromkeys(self.graph)
        visited: set[str] = set()
        heap: list[tuple[float, str]] = [(0, start_id)]
        while heap:
            current_dist, current = heapq.heappop(heap)
            if current in visited:
                continue
            visited.add(current)
            if current == end_id:
                break
            for neighbor, weight in self.graph.get(current, {}).items():
                if neighbor in visited:
                    continue
                new_dist = current_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    heapq.heappush(heap, (new_dist, neighbor))
        path: list[str] = []
        current = end_id
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        if not path or path[0] != start_id:
            return [], float("inf")
        return path, distances[end_id]


class AStarRouting:
    """A* pathfinding algorithm."""

    def __init__(self) -> None:
        self.graph: dict[str, dict[str, float]] = {}
        self.positions: dict[str, tuple[float, float]] = {}

    def add_node(self, node_id: str, x: float, y: float) -> None:
        self.positions[node_id] = (x, y)
        self.graph.setdefault(node_id, {})

    def add_edge(self, from_id: str, to_id: str, cost: float | None = None) -> None:
        if cost is None:
            x1, y1 = self.positions.get(from_id, (0, 0))
            x2, y2 = self.positions.get(to_id, (0, 0))
            cost = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        self.graph.setdefault(from_id, {})[to_id] = cost

    def _heuristic(self, node_id: str, goal_id: str) -> float:
        if node_id not in self.positions or goal_id not in self.positions:
            return 0
        x1, y1 = self.positions[node_id]
        x2, y2 = self.positions[goal_id]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def find_path(self, start_id: str, goal_id: str) -> tuple[list[str], float]:
        if start_id not in self.graph:
            return [], float("inf")
        open_set: list[tuple[float, str]] = [(0, start_id)]
        came_from: dict[str, str] = {}
        g_score: dict[str, float] = {start_id: 0}
        open_set_hash = {start_id}
        while open_set:
            _, current = heapq.heappop(open_set)
            open_set_hash.discard(current)
            if current == goal_id:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path, g_score.get(goal_id, float("inf"))
            for neighbor, cost in self.graph.get(current, {}).items():
                tentative_g = g_score.get(current, float("inf")) + cost
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self._heuristic(neighbor, goal_id)
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f, neighbor))
                        open_set_hash.add(neighbor)
        return [], float("inf")
