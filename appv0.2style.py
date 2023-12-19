import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd

import pickle
import json
import os
from sys import argv
from timeit import default_timer
import customtkinter

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

class App:
    def __init__(self, config=None):
        self.root = customtkinter.CTk()
        self.root.geometry("1920x1080")
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")
        self.root.title('Fight Analyse')

        photo = tk.PhotoImage(file="assets/icon.png")
        self.root.iconphoto(False, photo)

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
            'takedown': 0,
            'ground_control': None
        }
        self.previous_hits = []  # list for CTRL+y / CTRL+z
        self.hit_to_hide = []
        self.takedown = tk.IntVar()

        self.start_time = None
        self.is_running = False
        self.time_var = tk.StringVar()
        self.time_var.set("00:00:00")

        if config is not None:
            self._load(config)

        self.hit_percent_label = tk.Label(
            self.root,
            text=self._get_nb_and_percent_of_hits(),
            justify=tk.LEFT
        )
        self._create_gui()

        self.root.mainloop()

    def _create_gui(self):
        # TITRE
        self.title_entry = customtkinter.CTkEntry(self.root, width=400, placeholder_text='Title')
        if self.memory['filename']:  # ! Ca peut peter car j'ai mis = None
            self.title_entry.insert(tk.INSERT, self.memory['filename'][:-4])
        self.title_entry.pack()
        #####

        # # BUTTONS
        debug_button = customtkinter.CTkButton(self.root, text="Debug", command=self._debug)
        debug_button.pack(side=tk.BOTTOM)

        save_button = customtkinter.CTkButton(self.root, text="Save", command=self._save)
        save_button.pack(side=tk.BOTTOM)
        # #####

        # left_frame = tk.Frame(self.root, bg='BLUE')
        left_frame = customtkinter.CTkFrame(self.root)
        # ROUNDS
        for i in range(5):
            button_text = "Round {}".format(i+1)
            button = customtkinter.CTkCheckBox(
                left_frame, text=button_text,
                variable=tk.IntVar(),
                command=lambda i=i: self._select_round_click(i)
            )
            button.pack()
        #####

        # PICTURE
        self.canvas = tk.Canvas(left_frame, width=171, height=549)
        self.canvas.pack()

        self.img = tk.PhotoImage(file=self.empty_body_path)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        #####

        # HIT BUTTONS
        button_frame = customtkinter.CTkFrame(self.root)
        for i, rb_label in enumerate(HIT_TYPE):
            toggle_btn = customtkinter.CTkButton(
                button_frame, text='Show', command=lambda i=i: self._hide_hit(i))
            toggle_btn.grid(row=i, column=0, sticky='w')

            rb = customtkinter.CTkRadioButton(button_frame, text=rb_label,
                                value=i, variable=self.champs['hit_type'])
            rb.grid(row=i, column=1, sticky='w')

        nb_takedown = customtkinter.CTkLabel(self.root,
            textvariable=self.takedown, font=("Helvetica", 16))
        del_takedown_button = customtkinter.CTkButton(self.root,
            text="-", command=lambda i=-1:self._update_takedown(i))
        add_takedown_button = customtkinter.CTkButton(self.root,
            text="+", command=lambda i=1:self._update_takedown(i))

        del_takedown_button.pack(side=tk.LEFT)
        nb_takedown.pack(side=tk.LEFT)
        add_takedown_button.pack(side=tk.LEFT)
        button_frame.pack(side=tk.LEFT)
        #####

        # Chrono
        self.time_label = customtkinter.CTkLabel(
            left_frame, textvariable=self.time_var, font=("Helvetica", 24))
        self.time_label.pack()

        # Button to start/stop the timer
        self.start_stop_button = customtkinter.CTkButton(
            left_frame, text="Start/Stop", command=self._start_stop_timer)
        self.start_stop_button.pack()
        self.reset = customtkinter.CTkButton(
            left_frame, text="Reset", command=self._reset_timer)
        self.reset.pack()
        #####
        left_frame.pack(side=tk.LEFT)

        self.right_frame = customtkinter.CTkFrame(self.root)
        # COMMENTARY
        self.commentary_entry = customtkinter.CTkTextbox(self.right_frame)
        if self.memory['commentary']:
            self.commentary_entry.insert(tk.INSERT, self.memory['commentary'])
        self.commentary_entry.pack()
        #####

        # NUMBER OF HITS
        # self._draw_hit_data()
        #####

        self.right_frame.pack(side=tk.RIGHT)

        # EVENTS
        # self.canvas.bind("<Button-1>", self._add_letter_left)
        # self.canvas.bind("<Button-3>", self._add_letter_right)

        # self.root.bind_all("<Control-y>", self._redo)
        # self.root.bind_all("<Control-z>", self._undo)
        #####

        # open_button = tcustomtkinter.CTkButton(
        #     self.root,
        #     text='Open a File',
        #     command=self._select_file
        # )

        # open_button.pack(expand=True)

    # def _select_file(self):
    #     filetypes = (
    #         ('text files', '*.plk')
    #     )

    #     filename = fd.askopenfilename(
    #         title='Open a file',
    #         initialdir=os.getcwd(),
    #         filetypes=filetypes)

    #     tk.messagebox.showinfo(
    #         title='Selected File',
    #         message=filename
    #     )

    def _hide_hit(self, hit):
        if hit in self.hit_to_hide:
            self.hit_to_hide.remove(hit)
        else:
            self.hit_to_hide.append(hit)
        self._draw_hits()

    def _update_takedown(self, value):
        self.memory['takedown'] += value
        self.takedown.set(self.memory['takedown'])

    def _draw_hit_data(self):
        self.hit_percent_label.config(text=(str(self._get_nb_and_percent_of_hits())))
        self.hit_percent_label.pack()

    def _get_nb_and_percent_of_hits(self, to_string=True):
        n_hit_list = [{'n': 0, 'type': hit_t, 'percent': 0} for hit_t in HIT_TYPE]

        # count how many hit
        for _round in self.rounds_selected:
            for i in range(len(self.memory['hits'][_round])):
                n_hit_list[HIT_TYPE.index(
                    self.memory['hits'][_round][i]['type'])]['n'] += 1

        # get percent of each hit
        n_hit = sum([case['n'] for case in n_hit_list])
        for i in range(len(n_hit_list)):
            try:
                n_hit_list[i]['percent'] = round((n_hit_list[i]['n'] * 100) / n_hit, 1)
            except ZeroDivisionError:
                n_hit_list[i]['percent'] = 0

        # sort list
        for i in range(len(n_hit_list)):
            for j in range(len(n_hit_list) - 1):
                if n_hit_list[i]['n'] > n_hit_list[j]['n']:
                    n_hit_list[i], n_hit_list[j] = n_hit_list[j], n_hit_list[i]

        # create cool string to show with list
        if to_string:
            string_to_show = ''
            for case in n_hit_list:
                string_to_show += str(case['percent']) + '% - ' + (str(case['n']) + ' ' + case['type'] + '\n')
            return string_to_show
        else:
            return n_hit_list

    def _start_stop_timer(self):
        if self.is_running:
            self.is_running = False
        else:
            if self.start_time is None:
                time_str = self.time_var.get().replace(":", "")
                self.start_time = default_timer() - float(time_str)
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
                self._draw_hits()
            self._draw_hit_data()

    def _undo(self, event=None):
        for round in self.rounds_selected:
            if len(self.memory['hits'][round]) >= 1:
                hit_deleted = self.memory['hits'][round].pop()
                self.previous_hits.append(hit_deleted)
                self._draw_hits()
        self._draw_hit_data()

    def _draw_hits(self):
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        for round in self.rounds_selected:
            for i in range(len(self.memory['hits'][round])):
                if not HIT_TYPE.index(self.memory['hits'][round][i]['type']) in self.hit_to_hide:
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
        self._draw_hits()
        self._draw_hit_data()

    def _add_letter_left(self, event):
        self._add_hit(
            {'x': event.x, 'y': event.y},
            HIT_TYPE[self.champs['hit_type'].get()],
            LEFT,
            'red',
            True
        )
        self._draw_hit_data()

    def _add_letter_right(self, event):
        self._add_hit(
            {'x': event.x, 'y': event.y},
            HIT_TYPE[self.champs['hit_type'].get()],
            RIGHT,
            'blue',
            True
        )
        self._draw_hit_data()

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
        self.takedown.set(self.memory['takedown'])

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
