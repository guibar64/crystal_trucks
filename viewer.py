import arcade
import copy

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Crystals VS Trucks"


class Truck:
    def __init__(self, x, y):
        self.x = 0
        self.y = 0
        self.movements = {}

    def move(self, turn, x, y):
        # TODO déplacer que d'une case
        self.movements[turn] = (x, y)

    def position_at(self, clock):
        return self.x, self.y


class CrystalsVsTrucksGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.nb_trucks = 0
        self.grid_width = 0
        self.grid_height = 0
        self.initial_grid = []
        self.grid = None
        self.cell_width = 1
        self.cell_height = 1
        self.commands = []
        self.trucks = []
        self.clock = 0

        arcade.set_background_color(arcade.color.AMAZON)

        # If you have sprite lists, you should create them here,
        # and set them to None

    def read_config_file(self, filepath):
        in_grid = False
        with open(filepath, encoding="utf-8") as file:
            for line in file:
                if in_grid and not line.startswith("### End Grid ###"):
                    self.initial_grid.append([])
                    for char in line.strip():
                        if char == " ":
                            self.initial_grid[-1].append(0)
                        else:
                            self.initial_grid[-1].append(int(char))
                    for _ in range(len(self.initial_grid[-1]), self.width):
                        self.initial_grid[-1].append(0)
                    self.grid = copy.deepcopy(self.initial_grid)
                elif line.startswith("### End Grid ###"):
                    in_grid = False
                elif line.startswith("trucks: "):
                    self.nb_trucks = int(line.split()[-1])
                    self.trucks = [
                        Truck(0, truck_id) for truck_id in range(self.nb_trucks)
                    ]
                elif line.startswith("width: "):
                    self.grid_width = int(line.split()[-1])
                    self.cell_width = SCREEN_WIDTH // self.grid_width
                elif line.startswith("height: "):
                    self.grid_height = int(line.split()[-1])
                    self.cell_height = SCREEN_HEIGHT // self.grid_height
                elif line.startswith("### Grid ###"):
                    in_grid = True
                else:
                    parts = line.split()
                    if len(parts) < 2 or parts[1] not in ("DIG", "MOVE", "WAIT"):
                        print("ignore", line, end="")
                    else:
                        self.commands.append(parts)

    def position_to_px(self, x, y):
        return int((x + 0.5) * self.cell_width), int((y + 0.5) * self.cell_height)

    def compute_sprites(self):
        self.crystal_list = arcade.SpriteList()
        for cell_x in range(self.grid_width):
            for cell_y in range(self.grid_height):
                if self.grid[cell_y][cell_x] > 0:
                    crystal_sprite = arcade.Sprite(
                        "./element_blue_polygon_glossy.png", 0.5
                    )
                    x, y = self.position_to_px(cell_x, cell_y)
                    crystal_sprite.center_x = x - crystal_sprite.width // 2
                    crystal_sprite.center_y = y - crystal_sprite.height // 2 - 10
                    self.crystal_list.append(crystal_sprite)
                if self.grid[cell_y][cell_x] > 1:
                    crystal_sprite = arcade.Sprite(
                        "./element_red_polygon_glossy.png", 0.5
                    )
                    x, y = self.position_to_px(cell_x, cell_y)
                    crystal_sprite.center_x = x - crystal_sprite.width // 2 + 10
                    crystal_sprite.center_y = y - crystal_sprite.height // 2 - 10 + 10
                    self.crystal_list.append(crystal_sprite)

        self.truck_list = arcade.SpriteList()
        for truck in self.trucks:
            truck_sprite = arcade.Sprite("./towtruck.png", 1.5)
            x, y = self.position_to_px(*truck.position_at(self.clock))
            truck_sprite.center_x = x - truck_sprite.width // 2 + 10
            truck_sprite.center_y = y - truck_sprite.height // 2 - 10
            self.truck_list.append(truck_sprite)

    def setup(self):
        """Set up the game variables. Call to re-start the game."""
        self.compute_sprites()

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        self.crystal_list.draw()
        self.truck_list.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.clock += delta_time
        print("new frame at", self.clock)
        self.grid = copy.deepcopy(self.initial_grid)
        self.trucks = [Truck(0, truck_id) for truck_id in range(self.nb_trucks)]
        for command in sorted(self.commands):
            time, command, *args = command
            time = int(time)
            if time < self.clock:
                self.interpret(time, command, args)

        self.compute_sprites()

    def interpret(self, turn, command, args):
        if command == "MOVE":
            if len(args) != 3:
                print("invalid move command, must have 3 arguments", command, args)
                return
            truck_id, x, y = (int(a) for a in args)
            if not 0 <= truck_id < self.nb_trucks:
                print("invalid move command, invalid truck id", command, args)
                return
            if not 0 <= x < self.width:
                print("invalid move command, invalid x", command, args)
                return
            if not 0 <= y < self.height:
                print("invalid move command, invalid y", command, args)
                return
            self.trucks[truck_id].move(turn, x, y)
        elif command == "DIG":
            if len(args) != 3:
                print("invalid dig command, must have 3 arguments", command, args)
                return
            truck_id, x, y = (int(a) for a in args)
            if not 0 <= truck_id < self.nb_trucks:
                print("invalid dig command, invalid truck id", command, args)
                return
            if not 0 <= x < self.width:
                print("invalid dig command, invalid x", command, args)
                return
            if not 0 <= y < self.height:
                print("invalid dig command, invalid y", command, args)
                return
            truck = self.trucks[truck_id]
            if x != truck.x or y != truck.y:
                print("invalid dig command, cannot dig on non current position")
                print(f"    {truck_id=} {truck.x=} {truck.y=} dig at {x=} {y=}")
                return
            self.grid[y][x] = max(0, self.grid[y][x] - 1)
        else:
            print("invalid command", command, args)

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        pass

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    """Main function"""
    game = CrystalsVsTrucksGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.read_config_file("seed4.sample.txt")  # TODO use argparse
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
