import tkinter as tk
import tkinter.ttk as ttk

JAB = 0
HOOK = 1
UPPERCUT = 2
OVERHAND = 3
CLMH = 4
ELBOW = 5
KNEES = 6

HIT_TYPE = [
    "JAB",
    "HOOK",
    "UPPERCUT",
    "OVERHAND",
    "CLMH",
    "ELBOW",
    "KNEES",
]

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.empty_body_path = "model_body.png"
        self.champs = {
            'hit_type': tk.IntVar(),
            'selected_rounds': tk.StringVar(),
        }
        self.selected_buttons = []
        self._create_gui()

        self.root.title("Fight Analyse")
        self.root.mainloop()

    def button_click(self, button_index):
        if button_index in self.selected_buttons:
            self.selected_buttons.remove(button_index)
        else:
            self.selected_buttons.append(button_index)

    def _create_gui(self):
        self.title_entry = tk.Entry(self.root)
        self.title_entry.pack()

        for i in range(1, 6):
            button_text = "Round {}".format(i)
            button = tk.Checkbutton(self.root, text=button_text, variable=tk.IntVar(), command=lambda i=i: self.button_click(i))
            button.pack(pady=5)

        for i, rb_label in enumerate(HIT_TYPE):
            rb = ttk.Radiobutton(self.root, text=rb_label, value=i, variable=self.champs['hit_type'])
            rb.pack()

        self.img = tk.PhotoImage(file=self.empty_body_path)
        label = tk.Label(self.root, image=self.img)
        label.pack()

        validate_button = tk.Button(self.root, text="Debug", command=self.debug)
        validate_button.pack()

    def debug(self):
        title_value = self.title_entry.get()
        print(f"Title: {title_value}")

        for v, k in self.champs.items():
            print(f"{v} : {k.get()}")

        print("Boutons sélectionnés:", self.selected_buttons)

App()
