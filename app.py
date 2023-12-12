import tkinter as tk
import tkinter.ttk as ttk
import pickle
from sys import argv

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

class App:
    def __init__(self, config = None):
        self.root = tk.Tk()
        self.empty_body_path = "assets/model_body.png"
        self.champs = {
            'hit_type': tk.IntVar(),
            'selected_rounds': tk.StringVar(),
        }
        # My variables
        self.selected_buttons = []
        self.memory = []
        self.hits_memory = []
        self.name = config

        self._create_gui()
        if config is not None:
            self._load(config)

        self.root.title("Fight Analyse")
        self.root.mainloop()

    def _button_click(self, button_index):
        if button_index in self.selected_buttons:
            self.selected_buttons.remove(button_index)
        else:
            self.selected_buttons.append(button_index)

    def _create_gui(self):
        self.title_entry = tk.Entry(self.root)
        if self.name:
            self.title_entry.insert(0, self.name[:-4])
        self.title_entry.pack()

        for i in range(1, 6):
            button_text = "Round {}".format(i)
            button = tk.Checkbutton(self.root, text=button_text, variable=tk.IntVar(), command=lambda i=i: self._button_click(i))
            button.pack(pady=5)

        for i, rb_label in enumerate(HIT_TYPE):
            rb = ttk.Radiobutton(self.root, text=rb_label, value=i, variable=self.champs['hit_type'])
            rb.pack()

        self.canvas = tk.Canvas(self.root, width=171, height=549)
        self.canvas.pack()

        self.img = tk.PhotoImage(file=self.empty_body_path)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)

        self.canvas.bind("<Button-1>", self._add_letter_left)
        self.canvas.bind("<Button-3>", self._add_letter_right)

        debug_button = tk.Button(self.root, text="Debug", command=self._debug)
        debug_button.pack()

        save_button = tk.Button(self.root, text="Save", command=self._save)
        save_button.pack()

    def _add_letter_left(self, event):
        self._add_hit(
            {'x': event.x, 'y': event.y},
            HIT_TYPE[self.champs['hit_type'].get()],
            LEFT,
            'red'
        )

    def _add_letter_right(self, event):
        self._add_hit(
            {'x': event.x, 'y': event.y},
            HIT_TYPE[self.champs['hit_type'].get()],
            RIGHT,
            'blue'
        )

    def _add_hit(self, pos, type, side, color):
        self.canvas.create_text(pos['x'], pos['y'], text=type, fill=color)
        self.hits_memory.append({
            'pos': pos,
            'color': color,
            'type': HIT_TYPE[self.champs['hit_type'].get()],
            'side': 'right' if side == RIGHT else 'left'
        })

    def _save(self):
        with open(str(self.title_entry.get()) + '.plk', 'wb') as file:
    	    pickle.dump(self.hits_memory, file)
        print('saving with name: ' + str(self.title_entry.get()) + '.plk')

    def _load(self, path_save):
        with open(path_save, 'rb') as file:
            self.hits_memory = pickle.load(file)
            self._initialize_canvas()

    def _initialize_canvas(self):
        # peut surement etre amélioré
        for i in range(len(self.hits_memory)):
            self._add_hit(
                self.hits_memory[i]['pos'], 
                self.hits_memory[i]['type'], 
                self.hits_memory[i]['side'], 
                self.hits_memory[i]['color']
            )

    def _debug(self):
        title_value = self.title_entry.get()
        print(f"Title: {title_value}")

        for v, k in self.champs.items():
            print(f"{v} : {k.get()}")

        print("Boutons sélectionnés:", self.selected_buttons)
        print('self.hits:', self.hits_memory)

def main(argv):
    App(argv[0] if len(argv) == 1 else None)

if __name__ == '__main__':
    main(argv[1:])
