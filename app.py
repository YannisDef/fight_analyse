import tkinter as tk
import tkinter.ttk as ttk
import pickle
from sys import argv
import json
from timeit import default_timer

JAB = 0
HOOK = 1
UPPERCUT = 2
OVERHAND = 3
CLMH = 4
ELBOW = 5
KNEES = 6

LEFT = 0
RIGHT = 1

HIT_TYPE = [
    "Jab",
    "Hook",
    "Uppercut",
    "Overhand",
    "CLMH",
    "Elbow",
    "Knee",
]

# TODO:
# - regrouper les hits proches
# - trouver un moyen de différencier les coups gauches des coups droits
# - je pense qu'on peut optimiser le code car je recréer a chaque tour de boucle

# autopep8 -i app.py

class App:
    def __init__(self, config=None):
        self.root = tk.Tk()
        self.root.geometry("900x1080")
        self.root.title('Fight Analyse')

        self.empty_body_path = 'assets/model_body.png'
        self.champs = {
            'hit_type': tk.IntVar(),
            'selected_rounds': tk.StringVar(),
        }
        # My variables
        self.rounds_selected = []
        self.memory = {
            'filename': None,
            'commentary': None,
            'hits': [[], [], [], [], []],
            'ground_control': None
        }
        self.previous_hits = [] # list for CTRL+y / CTRL+z
        # self.name = config

        self.start_time = None
        self.is_running = False
        self.time_var = tk.StringVar()
        self.time_var.set("00:00:00")

        if config is not None:
            self._load(config)        
        self._create_gui()

        self.root.mainloop()

    def _create_gui(self):
        # BUTTONS
        debug_button = tk.Button(self.root, text="Debug", command=self._debug)
        debug_button.pack(side=tk.BOTTOM)

        save_button = tk.Button(self.root, text="Save", command=self._save)
        save_button.pack(side=tk.BOTTOM)
        #####

        # TITRE
        self.title_entry = tk.Entry(self.root, width=70)
        if self.memory['filename']:  # ! Ca peut peter car j'ai mis = None
            self.title_entry.insert(tk.INSERT, self.memory['filename'][:-4])
        self.title_entry.pack()
        #####

        # leftFrame = tk.Frame(self.root, bg='BLUE')
        leftFrame = tk.Frame(self.root)
        # ROUNDS
        for i in range(5):
            button_text = "Round {}".format(i+1)
            button = tk.Checkbutton(
                leftFrame, text=button_text,
                variable=tk.IntVar(),
                command=lambda i=i: self._select_round_click(i)
            )
            button.pack()
        #####

        # PICTURE
        self.canvas = tk.Canvas(leftFrame, width=171, height=549)
        self.canvas.pack()

        self.img = tk.PhotoImage(file=self.empty_body_path)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        #####

        # HIT BUTTONS
        for i, rb_label in enumerate(HIT_TYPE):
            rb = ttk.Radiobutton(leftFrame, text=rb_label,
                                 value=i, variable=self.champs['hit_type'])
            rb.pack()
        #####

        # Chrono
        self.time_label = tk.Label(
            leftFrame, textvariable=self.time_var, font=("Helvetica", 24))
        self.time_label.pack(pady=20)

        # Button to start/stop the timer
        self.start_stop_button = tk.Button(
            leftFrame, text="Start/Stop", command=self._start_stop_timer)
        self.start_stop_button.pack()
        self.reset = tk.Button(
            leftFrame, text="Reset", command=self._reset_timer)
        self.reset.pack()
        #####
        leftFrame.pack(side=tk.LEFT)

        rightFrame = tk.Frame(self.root, bg='RED')
        self.commentary_entry = tk.Text(rightFrame)
        if self.memory['commentary']:
            self.commentary_entry.insert(tk.INSERT, self.memory['commentary'])
        self.commentary_entry.pack(side=tk.RIGHT)
        rightFrame.pack(side=tk.RIGHT)

        # EVENTS
        self.canvas.bind("<Button-1>", self._add_letter_left)
        self.canvas.bind("<Button-3>", self._add_letter_right)

        self.root.bind_all("<Control-y>", self._redo)
        self.root.bind_all("<Control-z>", self._undo)
        #####

    def _start_stop_timer(self):
        if self.is_running:
            self.is_running = False
        else:
            if self.start_time is None:
                self.start_time = \
                default_timer() - float(self.time_var.get().replace(":", ""))
            self.is_running = True
            self._update_time()

    def _update_time(self):
        if self.is_running:
            now = default_timer() - self.start_time
            minutes, seconds = divmod(now, 60)
            hours, minutes = divmod(minutes, 60)
            str_time = "%d:%02d:%02d" % (hours, minutes, seconds)

            self.time_var.set(str_time)
            self.root.after(1000, self._update_time)

    def _reset_timer(self):
        self.time_var.set("00:00:00")

    def _redo(self, event=None):
        if len(self.previous_hits) >= 1:
            hit_to_redo = self.previous_hits.pop()
            for round in self.rounds_selected:
                self.memory['hits'][round].append(hit_to_redo)

                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
                for round in self.rounds_selected:
                    for i in range(len(self.memory['hits'][round])):
                        self._add_hit(
                            self.memory['hits'][round][i]['pos'],
                            self.memory['hits'][round][i]['type'],
                            self.memory['hits'][round][i]['side'],
                            self.memory['hits'][round][i]['color']
                        )

    def _undo(self, event=None):
        for round in self.rounds_selected:
            if len(self.memory['hits'][round]) >= 1:
                hit_deleted = self.memory['hits'][round].pop()
                self.previous_hits.append(hit_deleted)

                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
                for round in self.rounds_selected:
                    for i in range(len(self.memory['hits'][round])):
                        self._add_hit(
                            self.memory['hits'][round][i]['pos'],
                            self.memory['hits'][round][i]['type'],
                            self.memory['hits'][round][i]['side'],
                            self.memory['hits'][round][i]['color']
                        )


    def _select_round_click(self, button_index):
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        if button_index in self.rounds_selected:
            self.rounds_selected.remove(button_index)
        else:
            self.rounds_selected.append(button_index)

        # Draw only hits of rounds selected
        for round in self.rounds_selected:
            for i in range(len(self.memory['hits'][round])):
                self._add_hit(
                    self.memory['hits'][round][i]['pos'],
                    self.memory['hits'][round][i]['type'],
                    self.memory['hits'][round][i]['side'],
                    self.memory['hits'][round][i]['color']
                )

    def _add_letter_left(self, event):
        self._add_hit(
            {'x': event.x, 'y': event.y},
            HIT_TYPE[self.champs['hit_type'].get()],
            LEFT,
            'red',
            True
        )

    def _add_letter_right(self, event):
        self._add_hit(
            {'x': event.x, 'y': event.y},
            HIT_TYPE[self.champs['hit_type'].get()],
            RIGHT,
            'blue',
            True
        )

    def _add_hit(self, pos, type, side, color, save_hit=False):
        for round_selected in self.rounds_selected:
            self.canvas.create_text(
                pos['x'], pos['y'], text=type[0], fill=color)
            if save_hit:
                self._save_hit(round_selected, pos, side, color)

    def _save_hit(self, round, pos, side, color):
        self.memory['hits'][round].append({
            'pos': pos,
            'color': color,
            'type': HIT_TYPE[self.champs['hit_type'].get()],
            'side': 'right' if side == RIGHT else 'left'
        })

    def _save(self):
        self.memory['filename'] = self.title_entry.get() + '.plk'
        self.memory['commentary'] = self.commentary_entry.get('1.0', tk.END)
        self.memory['ground_control'] = self.time_var.get()
        with open(str(self.title_entry.get()) + '.plk', 'wb') as file:
            pickle.dump(self.memory, file)
        print('saving with name: ' + str(self.title_entry.get()) + '.plk')

    def _load(self, path_save):
        with open(path_save, 'rb') as file:
            self.memory = pickle.load(file)
            # print('self.memory', self.memory)
            self._initialize_canvas()

    def _initialize_canvas(self):
        # peut surement etre amélioré
        for i in range(len(self.memory['hits'])):
            for j in range(len(self.memory['hits'][i])):
                self._add_hit(
                    self.memory['hits'][i][j]['pos'],
                    self.memory['hits'][i][j]['type'],
                    self.memory['hits'][i][j]['side'],
                    self.memory['hits'][i][j]['color']
                )
        self.time_var.set(self.memory['ground_control'])

    def _debug(self):
        print(f"Title: {self.title_entry.get()}")
        print(f"Commentary: {self.commentary_entry.get('1.0', tk.END)}")

        for v, k in self.champs.items():
            print(f"{v} : {k.get()}")

        print("Rounds sélectionnés:", self.rounds_selected)
        print('self.hits:', json.dumps(self.memory, indent=1))


def main(argv):
    App(argv[0] if len(argv) == 1 else None)


if __name__ == '__main__':
    main(argv[1:])
