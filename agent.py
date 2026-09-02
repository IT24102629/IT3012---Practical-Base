from collections import deque
import heapq
import math


class SearchAgent:

    def __init__(self):

        self.plan = []
        self.active_algo = 'AStar'

        self.position = (0, 0)
        self.facing = 'Right'
        self.last_action = None


    def get_delta(self, direction):

        directions = {
            'Up': (0, 1),
            'Down': (0, -1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }

        return directions[direction]


    def get_left_direction(self, direction):

        left_turn = {
            'Up': 'Left',
            'Left': 'Down',
            'Down': 'Right',
            'Right': 'Up'
        }

        return left_turn[direction]


    def get_right_direction(self, direction):

        right_turn = {
            'Up': 'Right',
            'Right': 'Down',
            'Down': 'Left',
            'Left': 'Up'
        }

        return right_turn[direction]


    def update_from_last_action(self):

        if self.last_action is None:
            return

        if self.last_action == 'Forward':

            dx, dy = self.get_delta(self.facing)

            self.position = (
                self.position[0] + dx,
                self.position[1] + dy
            )

        elif self.last_action == 'TurnLeft':
            self.facing = self.get_left_direction(self.facing)

        elif self.last_action == 'TurnRight':
            self.facing = self.get_right_direction(self.facing)


    def get_neighbors(self, state, grid_size, walls):

        x, y = state
        width, height = grid_size

        neighbors = [
            ('Up', (x, y + 1)),
            ('Right', (x + 1, y)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y))
        ]

        valid_neighbors = []

        for action, new_state in neighbors:

            nx, ny = new_state

            if (
                0 <= nx < width
                and 0 <= ny < height
                and new_state not in walls
            ):
                valid_neighbors.append((action, new_state))

        return valid_neighbors


    def manhattan_distance(self, pos, goal):

        x1, y1 = pos
        x2, y2 = goal

        return abs(x1 - x2) + abs(y1 - y2)


    def euclidean_distance(self, pos, goal):

        x1, y1 = pos
        x2, y2 = goal

        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


    def bfs_search(self, start, goal, grid_size, walls):

        frontier = deque([(start, [])])
        reached = {start}

        while frontier:

            state, path = frontier.popleft()

            if state == goal:
                return path

            for action, new_state in self.get_neighbors(state, grid_size, walls):

                if new_state not in reached:
                    reached.add(new_state)
                    frontier.append((new_state, path + [action]))

        return []


    def dfs_search(self, start, goal, grid_size, walls):

        frontier = [(start, [])]
        reached = {start}

        while frontier:

            state, path = frontier.pop()

            if state == goal:
                return path

            for action, new_state in self.get_neighbors(state, grid_size, walls):

                if new_state not in reached:
                    reached.add(new_state)
                    frontier.append((new_state, path + [action]))

        return []


    def ucs_search(self, start, goal, grid_size, walls):

        frontier = [(0, start, [])]
        reached = set()

        while frontier:

            cost, state, path = heapq.heappop(frontier)

            if state in reached:
                continue

            reached.add(state)

            if state == goal:
                return path

            for action, new_state in self.get_neighbors(state, grid_size, walls):

                if new_state not in reached:
                    heapq.heappush(frontier, (cost + 1, new_state, path + [action]))

        return []


    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):

        frontier = []
        reached_states = set()

        if heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(start_pos, goal_pos)
        else:
            h_cost = self.manhattan_distance(start_pos, goal_pos)

        g_cost = 0
        f_cost = g_cost + h_cost

        heapq.heappush(frontier, (f_cost, g_cost, start_pos, []))

        while frontier:

            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            if current_pos in reached_states:
                continue

            if current_pos == goal_pos:
                return path_taken

            reached_states.add(current_pos)

            for action, new_state in self.get_neighbors(current_pos, grid_size, walls):

                if new_state not in reached_states:

                    new_g_cost = g_cost + 1

                    if heuristic_type == 'euclidean':
                        new_h_cost = self.euclidean_distance(new_state, goal_pos)
                    else:
                        new_h_cost = self.manhattan_distance(new_state, goal_pos)

                    new_f_cost = new_g_cost + new_h_cost

                    heapq.heappush(
                        frontier,
                        (new_f_cost, new_g_cost, new_state, path_taken + [action])
                    )

        return []


    def find_closest_food(self, all_food):

        if not all_food:
            return None

        x, y = self.position

        return min(
            all_food,
            key=lambda food: abs(food[0] - x) + abs(food[1] - y)
        )


    def directions_to_actions(self, directions):

        actions = []
        facing = self.facing

        for direction in directions:

            if facing == direction:
                actions.append('Forward')

            elif self.get_left_direction(facing) == direction:
                actions.append('TurnLeft')
                facing = self.get_left_direction(facing)
                actions.append('Forward')

            elif self.get_right_direction(facing) == direction:
                actions.append('TurnRight')
                facing = self.get_right_direction(facing)
                actions.append('Forward')

            else:
                actions.append('TurnLeft')
                facing = self.get_left_direction(facing)
                actions.append('TurnLeft')
                facing = self.get_left_direction(facing)
                actions.append('Forward')

        return actions


    def sense_and_act(self, percept: dict) -> str:

        self.update_from_last_action()
        self.last_action = None

        if percept['food_here']:
            self.plan = []
            action = 'Suck'

        else:

            if not self.plan:

                goal = self.find_closest_food(percept['all_food'])

                if goal is None:
                    action = 'TurnLeft'
                    self.last_action = action
                    return action

                start = self.position
                grid_size = percept['grid_size']
                walls = set(percept['walls'])

                if self.active_algo == 'BFS':
                    directions = self.bfs_search(start, goal, grid_size, walls)

                elif self.active_algo == 'DFS':
                    directions = self.dfs_search(start, goal, grid_size, walls)

                elif self.active_algo == 'UCS':
                    directions = self.ucs_search(start, goal, grid_size, walls)

                elif self.active_algo == 'AStar':
                    directions = self.astar_search(start, goal, walls, grid_size)

                else:
                    directions = self.bfs_search(start, goal, grid_size, walls)

                self.plan = self.directions_to_actions(directions)

            if self.plan:
                action = self.plan.pop(0)
            else:
                action = 'TurnLeft'

        self.last_action = action

        return action
if __name__ == "__main__":

     agent = SearchAgent()

     print("Manhattan Distance:", agent.manhattan_distance((0, 0), (3, 4)))
     print("Euclidean Distance:", agent.euclidean_distance((0, 0), (3, 4)))
    