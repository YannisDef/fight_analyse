import tkinter as tk
import tkinter.ttk as ttk
import pickle
from sys import argv
import json

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
    "J",
    "H",
    "U",
    "O",
    "C",
    "E",
    "K",
]

# TODO:
# - CTRL+x / CTRL+y
# - regrouper les hits proches
# - trouver un moyen de différencier les coups gauches des coups droits

class App:
    def __init__(self, config = None):
        self.root = tk.Tk()
        self.root.geometry("700x1000")
        self.empty_body_path = 'assets/model_body.png'
        self.champs = {
            'hit_type': tk.IntVar(),
            'selected_rounds': tk.StringVar(),
        }
        # My variables
        self.rounds_selected = []
        self.memory = {
            'hits': [[], [], [], [], []],
            'commentary': None
        }
        self.name = config

        if config is not None:
            self._load(config)
        self._create_gui()

        self.root.title('Fight Analyse')
        self.root.mainloop()

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

    def _create_gui(self):
        # TITRE
        self.title_entry = tk.Entry(self.root, width=70)
        if self.name:
            self.title_entry.insert(tk.INSERT, self.name[:-4])
        self.title_entry.pack()
        #####

        # ROUNDS
        for i in range(5):
            button_text = "Round {}".format(i+1)
            button = tk.Checkbutton(self.root, text=button_text, variable=tk.IntVar(), command=lambda i=i: self._select_round_click(i))
            button.pack()
        #####

        # HIT BUTTONS
        for i, rb_label in enumerate(HIT_TYPE):
            rb = ttk.Radiobutton(self.root, text=rb_label, value=i, variable=self.champs['hit_type'])
            rb.pack()
        #####

        # PICTURE
        self.canvas = tk.Canvas(self.root, width=171, height=549)
        self.canvas.pack()

        self.img = tk.PhotoImage(file=self.empty_body_path)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        #####

        self.commentary_entry = tk.Text(self.root)
        if self.memory['commentary']:
            self.commentary_entry.insert(tk.INSERT, self.memory['commentary'])
        self.commentary_entry.pack()

        # EVENTS
        self.canvas.bind("<Button-1>", self._add_letter_left)
        self.canvas.bind("<Button-3>", self._add_letter_right)
        #####

        # BUTTONS
        debug_button = tk.Button(self.root, text="Debug", command=self._debug)
        debug_button.pack()

        save_button = tk.Button(self.root, text="Save", command=self._save)
        save_button.pack()
        #####

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

    def _add_hit(self, pos, type, side, color, save_hit = False):
        for round_selected in self.rounds_selected:
            self.canvas.create_text(pos['x'], pos['y'], text=type, fill=color)
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
        self.memory['commentary'] = self.commentary_entry.get()
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
        # print('self.commantary:', self.memory['commentary'])
        # self.commantary = self.memory['commentary']

    def _debug(self):
        print(f"Title: {self.title_entry.get()}")

        for v, k in self.champs.items():
            print(f"{v} : {k.get()}")

        print("Rounds sélectionnés:", self.rounds_selected)
        print('self.hits:', json.dumps(self.memory, indent = 1))

def main(argv):
    App(argv[0] if len(argv) == 1 else None)

if __name__ == '__main__':
    main(argv[1:])
