# visual_grid_game.py

import random
import tkinter as tk
from agent import SearchAgent



class VisualGridHuntGame:

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        custom_walls=None
    ):
        self.width = width
        self.height = height

        
        self.agent_pos = [0, 0]
        self.facing = 'Right'

    

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

    

        self.food_positions = set()

        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)

            food_pos = (fx, fy)

            if (
                food_pos != (0, 0)
                and food_pos not in self.walls
            ):
                self.food_positions.add(food_pos)

    

        self.toxic_traps = set()

        while len(self.toxic_traps) < 3:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)

            trap_pos = (tx, ty)

            if (
                trap_pos != (0, 0)
                and trap_pos not in self.walls
                and trap_pos not in self.food_positions
            ):
                self.toxic_traps.add(trap_pos)

    

        self.opponents = []

        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)

            opponent_pos = [ox, oy]

            if (
                tuple(opponent_pos) != (0, 0)
                and tuple(opponent_pos) not in self.walls
                and tuple(opponent_pos) not in self.food_positions
            ):
                self.opponents.append(opponent_pos)

    

        self.score = 0
        self.steps = 0
        self.collision = False



    def get_percept(self) -> dict:

        x, y = self.agent_pos

        
        if self.facing == 'Up':
            ahead = (x, y + 1)

        elif self.facing == 'Down':
            ahead = (x, y - 1)

        elif self.facing == 'Left':
            ahead = (x - 1, y)

        else:  # Right
            ahead = (x + 1, y)

        wall_ahead = (
            ahead[0] < 0
            or ahead[0] >= self.width
            or ahead[1] < 0
            or ahead[1] >= self.height
            or ahead in self.walls
        )

        return {
            'wall_ahead': wall_ahead,
            'food_here': tuple(self.agent_pos) in self.food_positions,
            'toxin_here': tuple(self.agent_pos) in self.toxic_traps,
            'grid_size': (self.width, self.height),
            'walls': list(self.walls),
            'all_food': list(self.food_positions)
        }


    

    def execute_action(self, action: str):

        self.steps += 1


        if action == 'Suck':

            current_pos = tuple(self.agent_pos)

            if current_pos in self.food_positions:
                self.food_positions.remove(current_pos)
                self.score += 20

            return


        if action == 'TurnLeft':

            turn_left = {
                'Up': 'Left',
                'Left': 'Down',
                'Down': 'Right',
                'Right': 'Up'
            }

            self.facing = turn_left[self.facing]

            return


        if action == 'TurnRight':

            turn_right = {
                'Up': 'Right',
                'Right': 'Down',
                'Down': 'Left',
                'Left': 'Up'
            }

            self.facing = turn_right[self.facing]

            return

    
        if action == 'Forward':

            new_pos = list(self.agent_pos)

            if self.facing == 'Up':
                new_pos[1] += 1

            elif self.facing == 'Down':
                new_pos[1] -= 1

            elif self.facing == 'Left':
                new_pos[0] -= 1

            elif self.facing == 'Right':
                new_pos[0] += 1

            
            outside_grid = (
                new_pos[0] < 0
                or new_pos[0] >= self.width
                or new_pos[1] < 0
                or new_pos[1] >= self.height
            )

            if outside_grid:
                self.score -= 5

            elif tuple(new_pos) in self.walls:
                self.score -= 5

            else:
                self.agent_pos = new_pos

                # Toxic trap penalty
                if tuple(self.agent_pos) in self.toxic_traps:
                    self.score -= 15

    

        for op in self.opponents:

            move = random.choice(
                ['Up', 'Down', 'Left', 'Right', 'Stay']
            )

            old_pos = list(op)

            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1

            elif move == 'Down' and op[1] > 0:
                op[1] -= 1

            elif move == 'Left' and op[0] > 0:
                op[0] -= 1

            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            
            if tuple(op) in self.walls:
                op[0] = old_pos[0]
                op[1] = old_pos[1]

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True


    def is_done(self) -> bool:

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


class SimpleReflexAgent:
    

    def sense_and_act(self, percept: dict) -> str:

       
        if percept['food_here']:
            return 'Suck'

        elif percept['wall_ahead']:
            return 'TurnLeft'
        else:
            return 'Forward'


class ModelBasedAgent:

    def __init__(self):

        
        self.relative_pos = (0, 0)

        self.facing = 'Right'

        self.visited_cells = set()

        
        self.known_walls = set()

        
        self.last_action = None
        self.last_percept = None



    def get_delta(self, direction):

        directions = {
            'Up': (0, 1),
            'Down': (0, -1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }

        return directions[direction]


   

    def get_neighbor(self, direction):

        dx, dy = self.get_delta(direction)

        x, y = self.relative_pos

        return (
            x + dx,
            y + dy
        )


    def get_left_direction(self):

        left_turn = {
            'Up': 'Left',
            'Left': 'Down',
            'Down': 'Right',
            'Right': 'Up'
        }

        return left_turn[self.facing]


    def get_right_direction(self):

        right_turn = {
            'Up': 'Right',
            'Right': 'Down',
            'Down': 'Left',
            'Left': 'Up'
        }

        return right_turn[self.facing]


    def update_from_last_action(self):

        if self.last_action is None:
            return

        
        if self.last_action == 'Forward':

            if (
                self.last_percept is not None
                and not self.last_percept['wall_ahead']
            ):

                self.relative_pos = self.get_neighbor(
                    self.facing
                )

        elif self.last_action == 'TurnLeft':

            self.facing = self.get_left_direction()

        elif self.last_action == 'TurnRight':

            self.facing = self.get_right_direction()


    def sense_and_act(self, percept: dict) -> str:


        self.update_from_last_action()

        self.visited_cells.add(
            self.relative_pos
        )

        forward_cell = self.get_neighbor(
            self.facing
        )


        if percept['wall_ahead']:
            self.known_walls.add(
                forward_cell
            )

    
        if percept['food_here']:

            action = 'Suck'

        elif percept['wall_ahead']:

            left_direction = self.get_left_direction()

            right_direction = self.get_right_direction()

            left_cell = self.get_neighbor(
                left_direction
            )

            right_cell = self.get_neighbor(
                right_direction
            )

            if (
                left_cell not in self.visited_cells
                and left_cell not in self.known_walls
            ):
                action = 'TurnLeft'

           
            elif (
                right_cell not in self.visited_cells
                and right_cell not in self.known_walls
            ):
                action = 'TurnRight'

            else:
                action = 'TurnLeft'

        elif forward_cell not in self.visited_cells:

            action = 'Forward'


        else:

            left_direction = self.get_left_direction()

            right_direction = self.get_right_direction()

            left_cell = self.get_neighbor(
                left_direction
            )

            right_cell = self.get_neighbor(
                right_direction
            )

            if (
                left_cell not in self.visited_cells
                and left_cell not in self.known_walls
            ):
                action = 'TurnLeft'

            elif (
                right_cell not in self.visited_cells
                and right_cell not in self.known_walls
            ):
                action = 'TurnRight'

            else:
                action = 'Forward'

        self.last_action = action
        self.last_percept = percept.copy()

        return action


class GridGameGUI:

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=0,
        walls=None,
        agent_type='model'
    ):

        self.root = root

        self.root.title(
            "IT3012 - Practical 04 A* Search Agent"
        )

    
        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        if agent_type == 'reflex':
            self.agent = SimpleReflexAgent()
            self.agent_name = "Simple Reflex Agent"

        elif agent_type == 'model':
            self.agent = ModelBasedAgent()
            self.agent_name = "Model-Based Agent"

        else:
            self.agent = SearchAgent()
            self.agent_name = f"Search Agent ({self.agent.active_algo})"


        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )

        canvas_width = (
            self.env.width * self.cell_size
        )

        canvas_height = (
            self.env.height * self.cell_size
        )

        self.canvas = tk.Canvas(
            root,
            width=canvas_width,
            height=canvas_height,
            bg="white"
        )

        self.canvas.pack()

        # Agent type label
        self.agent_label = tk.Label(
            root,
            text=self.agent_name,
            font=("Arial", 14, "bold")
        )

        self.agent_label.pack(
            pady=5
        )

        
        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial", 14)
        )

        self.label.pack(
            pady=5
        )

        
        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white"
        )

        self.btn.pack(
            pady=5
        )

        self.draw_grid()


    def draw_grid(self):

        self.canvas.delete("all")


        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = x * self.cell_size

                y1 = (
                    self.env.height - 1 - y
                ) * self.cell_size

                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if (x, y) in self.env.walls:
                    color = "#64748b"
                else:
                    color = "#f1f5f9"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#cbd5e1"
                )

                
                if (
                    self.cell_size >= 40
                    and (x, y) in self.env.walls
                ):

                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=("Arial", 8, "bold")
                    )

    
        for fx, fy in self.env.food_positions:

            offset = (
                self.cell_size * 0.25
            )

            x1 = (
                fx * self.cell_size
                + offset
            )

            y1 = (
                (self.env.height - 1 - fy)
                * self.cell_size
                + offset
            )

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706"
            )


        for tx, ty in self.env.toxic_traps:

            offset = (
                self.cell_size * 0.2
            )

            x1 = (
                tx * self.cell_size
                + offset
            )

            y1 = (
                (self.env.height - 1 - ty)
                * self.cell_size
                + offset
            )

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="purple",
                outline="#4b0082"
            )


        for ox, oy in self.env.opponents:

            offset = (
                self.cell_size * 0.2
            )

            x1 = (
                ox * self.cell_size
                + offset
            )

            y1 = (
                (self.env.height - 1 - oy)
                * self.cell_size
                + offset
            )

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000"
            )


        ax, ay = self.env.agent_pos

        offset = (
            self.cell_size * 0.15
        )

        x1 = (
            ax * self.cell_size
            + offset
        )

        y1 = (
            (self.env.height - 1 - ay)
            * self.cell_size
            + offset
        )

        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )



    def run_loop(self):

        self.btn.config(
            state="disabled"
        )

        def step():

            if not self.env.is_done():
                percept = (
                    self.env.get_percept()
                )

                action = (
                    self.agent.sense_and_act(
                        percept
                    )
                )

                self.env.execute_action(
                    action
                )

                
                self.draw_grid()

                self.label.config(
                    text=(
                        f"Score: {self.env.score}"
                        f" | Steps: {self.env.steps}"
                        f" | Action: {action}"
                        f" | Facing: {self.env.facing}"
                    )
                )

                self.root.after(
                    250,
                    step
                )

            else:

                if self.env.collision:

                    end_text = (
                        "Collision! Game Over! "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                else:

                    end_text = (
                        f"Finished! "
                        f"Final Score: "
                        f"{self.env.score}"
                        f" | Steps: "
                        f"{self.env.steps}"
                    )

                self.label.config(
                    text=end_text
                )

                self.btn.config(
                    state="normal"
                )

        step()


if __name__ == "__main__":

    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0,
        agent_type='search'
    )

    root.mainloop()