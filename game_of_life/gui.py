from tkinter import (
    Label,
    Frame,
    Canvas,
    N,
    E,
    S,
    W,
    Button,
    IntVar,
    Entry,
    Listbox,
    StringVar,
)
from logic import GameMatrix


class AppBase(Frame):
    def __init__(self, master=None, **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.grid(sticky=N + E + S + W)
        self.rowconfigure(0, weight=2)
        self.rowconfigure(6, weight=2)
        self.columnconfigure(0, weight=2)
        self.create()

    def create(self):
        raise NotImplementedError


class GameGrid(Canvas):
    def __init__(self, master=None, rows=2000, columns=2000):
        Canvas.__init__(self, master)
        self.bind("<Button-1>", self.click_cell)
        self.bind("<B1-Motion>", self.hold_down_cell)
        self.bind("<Button-3>", self.right_click)
        self.bind("<B3-Motion>", self.right_move)
        self.cell_width = 15
        self.cell_height = 15
        self.cell_draws = [[None for c in range(columns)] for r in range(rows)]
        self.cell_color = "red"
        self.matrix = GameMatrix(rows=rows, columns=columns)
        self._create_grid()
        self.shift_x = 0
        self.shift_y = 0

    def click_cell(self, event):
        top_border = (
            event.y
            - (event.y - self.shift_y) % self.cell_height
            - self.shift_y
        )
        left_border = (
            event.x - (event.x - self.shift_x) % self.cell_width - self.shift_x
        )
        if top_border < 0 or left_border < 0:
            return
        row = top_border // self.cell_height
        column = left_border // self.cell_width
        if self.matrix[row, column]:
            self.matrix[row, column] = False
            self._draw_dead_cell(row, column)
        else:
            self.matrix[row, column] = True
            self._draw_alive_cell(row, column)

    def hold_down_cell(self, event):
        top_border = (
            event.y
            - (event.y - self.shift_y) % self.cell_height
            - self.shift_y
        )
        left_border = (
            event.x - (event.x - self.shift_x) % self.cell_width - self.shift_x
        )
        if top_border < 0 or left_border < 0:
            return
        row = top_border // self.cell_height
        column = left_border // self.cell_width
        if not self.matrix[row, column]:
            self.matrix[row, column] = True
            self._draw_alive_cell(row, column)

    def right_click(self, event):
        self.right_x0 = event.x
        self.right_y0 = event.y

    def right_move(self, event):
        items = self.find_all()
        for item in items:
            self.move(item, event.x - self.right_x0, event.y - self.right_y0)
        self.shift_x += event.x - self.right_x0
        self.shift_y += event.y - self.right_y0
        self.right_x0 = event.x
        self.right_y0 = event.y

    def _create_grid(self):
        self.grid_width = self.matrix.columns * self.cell_width
        self.grid_height = self.matrix.rows * self.cell_height
        self.create_rectangle(
            0,
            0,
            self.grid_width,
            self.grid_height,
            fill="white",
            outline="lightgray",
        )
        for x in range(self.cell_width, self.grid_width, self.cell_width):
            self.create_line(x, 0, x, self.grid_height, fill="lightgray")
        for y in range(self.cell_height, self.grid_height, self.cell_height):
            self.create_line(0, y, self.grid_width, y, fill="lightgray")

    def make_step(self):
        self.matrix.make_step()
        for row, column in self.matrix.alive:
            self._draw_alive_cell(row, column)
        for row, column in self.matrix.died:
            self._draw_dead_cell(row, column)

    def clear(self):
        for row, column in self.matrix.alive:
            self.matrix[row, column] = False
            self._draw_dead_cell(row, column)

    def add_pattern(self, name):
        self.matrix.add_pattern("block", 10, 10)
        for row, column in self.matrix.alive:
            self._draw_alive_cell(row, column)

    def _draw_alive_cell(self, row, column):
        if self.cell_draws[row][column]:
            self.delete(self.cell_draws[row][column])
        cell_draw_id = self.create_rectangle(
            column * self.cell_width + 1 + self.shift_x,
            row * self.cell_height + 1 + self.shift_y,
            (column + 1) * self.cell_width - 1 + self.shift_x,
            (row + 1) * self.cell_height - 1 + self.shift_y,
            fill=self.cell_color,
        )
        self.cell_draws[row][column] = cell_draw_id

    def _draw_dead_cell(self, row, column):
        if self.cell_draws[row][column]:
            self.delete(self.cell_draws[row][column])
        cell_draw_id = self.create_rectangle(
            column * self.cell_width + 1 + self.shift_x,
            row * self.cell_height + 1 + self.shift_y,
            (column + 1) * self.cell_width - 1 + self.shift_x,
            (row + 1) * self.cell_height - 1 + self.shift_y,
            fill="white",
            outline="white",
        )
        self.cell_draws[row][column] = cell_draw_id


class App(AppBase):
    def create(self):
        self.game_grid = GameGrid(self)
        self.game_grid.grid(row=0, column=0, rowspan=8, sticky=N + E + S + W)
        self.start_call_id = None
        self._create_buttons()

    def _create_buttons(self):
        self.start_button = Button(self, text="Start", command=self.start)
        self.start_button.grid(row=1, column=1, sticky=E + W, padx=5, pady=7)
        self._create_step_time_frame()
        self.stop_button = Button(self, text="Stop", command=self.stop)
        self.stop_button.grid(row=3, column=1, sticky=E + W, padx=5, pady=7)
        self.step_button = Button(self, text="Step", command=self.one_step)
        self.step_button.grid(row=4, column=1, sticky=E + W, padx=5, pady=7)
        self.clear_button = Button(self, text="Clear", command=self.clear)
        self.clear_button.grid(row=5, column=1, sticky=E + W, padx=5, pady=7)
        self._create_pattern_frame()
        self._create_color_frame()

    def _create_step_time_frame(self):
        self.step_time_frame = Frame(self)
        self.step_time_frame.grid(row=2, column=1)
        self.step_time_label = Label(
            self.step_time_frame, text="Time of one step is"
        )
        self.step_time_label.grid(
            row=2, column=1, sticky=E + W, padx=5, pady=7
        )
        self.step_time_var = IntVar(value=500)
        self.step_time_entry = Entry(
            self.step_time_frame, textvariable=self.step_time_var, width=10
        )
        self.step_time_entry.grid(
            row=2, column=2, sticky=E + W, padx=5, pady=7
        )
        self.ms_label = Label(self.step_time_frame, text="ms")
        self.ms_label.grid(row=2, column=3, sticky=E + W, padx=5, pady=7)

    def _create_pattern_frame(self):
        self.patterns_list = ["block"]
        self.patterns_var = StringVar(value=self.patterns_list)
        self.pattern_frame = Frame(self, bg="cyan")
        self.pattern_frame.grid(row=6, column=1, sticky=N + E + S + W)
        self.add_pattern_button = Button(
            self.pattern_frame, text="Add Pattern", command=self.add_pattern
        )
        self.add_pattern_button.grid(
            row=0, sticky=E + W, padx=5, pady=7
        )
        self.pattern_chooser = Listbox(
            self.pattern_frame, listvariable=self.patterns_var
        )
        self.pattern_chooser.selection_set(0)
        self.pattern_chooser.grid(
            row=1, sticky=E + W, padx=5, pady=7
        )

    def _create_color_frame(self):
        self.color_frame = Frame(self, bg="purple")
        self.color_frame.grid_columnconfigure(0, weight=1)
        self.color_frame.grid_columnconfigure(1, weight=1)
        self.color_frame.grid(row=7, column=1, sticky=N + E + S + W)
        self.change_color_button1 = Button(
            self.color_frame, 
            command=lambda: self.change_color("red"),
            bg="red"
        )
        self.change_color_button1.grid(

            row=0, column=0, sticky=E + W, padx=5, pady=7
        )
        self.change_color_button2 = Button(
            self.color_frame, 
            command=lambda: self.change_color("blue"),
            bg="blue"
        )
        self.change_color_button2.grid(
            row=0, column=1, sticky=E + W, padx=5, pady=7
        )

    def change_color(self, color):
        self.game_grid.cell_color = color

    def one_step(self):
        self.game_grid.make_step()

    def start(self):
        if self.start_call_id:
            self.stop()
        self.step_time = self.step_time_var.get()
        self.game_cycle()

    def game_cycle(self):
        self.game_grid.make_step()
        self.start_call_id = self.after(self.step_time, self.game_cycle)

    def stop(self):
        if self.start_call_id:
            self.after_cancel(self.start_call_id)
            self.start_call_id = None

    def clear(self):
        self.game_grid.clear()

    def add_pattern(self):
        pattern_name = self.pattern_chooser.selection_get()
        self.game_grid.add_pattern(pattern_name)


def main():
    Tick = App()
    Tick.mainloop()


if __name__ == "__main__":
    main()