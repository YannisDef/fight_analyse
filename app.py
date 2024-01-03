# https://customtkinter.tomschimansky.com/documentation/widgets/textbox

import tkinter as tk

import pickle
import json
from sys import argv
from timeit import default_timer
import customtkinter

# !
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
# !

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

# TODO: feat
#// - compter le nombre de takedown
#// - recalculer les % quand on cache un coup
#// - systeme de commentaire par defaut
#!- Probleme chrono ground control
# - faire un graphique de représentation des hits
# - systeme de notation hexagonal du combattant
# - systeme de creation de pdf
# - systeme d'ouverture de fichier ...
# - afficher le pourcentage de droite et de gauche
# - afficher nombre de coup au corps, tete, jambes
# - entrer les stats des deux combattans (age, poids, garde, ...)

# TODO: Optimisation
#// - je pense qu'on peut optimiser le code car je recréer certaines variables a chaque tour de boucle
#// - faire des fonctions pour init différentes parties de l'app
# - il y a des problemes avec la variable self.champs

# TODO: Style
#// - trouver un moyen de différencier les coups gauches des coups droits
# - Faire des plus beaux boutons que les Show -> faire des yeux
# - regrouper les hits proches
# - Legende ? comprendre la différence entre rouge et bleu ? C pour kick c'est nul
# - Modifier le style complet de l'app (couleurs, style, ...) / theme.json
# - Faire un schema bien organisé du style de l'app
    # - Organiser mieux les boutons et modules... surement en utilisant full grid

class App:
    def __init__(self, config=None):
        # setup window
        self.root = customtkinter.CTk()
        self.root.title('Fight Analyse')
        self.root.iconphoto(False, tk.PhotoImage(file="assets/icon.png"))
        self.root.geometry("1920x1080")
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("theme.json")

        # My variables
        self.champs = { # peut etre mit avec memory normalement
            'hit_type': tk.IntVar(),
            # 'selected_rounds': tk.StringVar(),
        }
        self.memory = {
            'filename': None,
            'commentary': None,
            'hits': [[], [], [], [], []],
            'takedown': 0,
            'ground_control': None
        }

        # style frame
        self.header_frame = customtkinter.CTkFrame(self.root, fg_color="blue", height=100)
        self.body_frame = customtkinter.CTkFrame(self.root)
        self.left_body_frame = customtkinter.CTkFrame(self.body_frame, width=540)
        self.left_hit_choice_frame = customtkinter.CTkFrame(self.left_body_frame, width=540, fg_color="red")
        self.left_hit_stats_frame = customtkinter.CTkFrame(self.left_body_frame, width=540, fg_color="red")
        self.right_body_frame = customtkinter.CTkFrame(self.body_frame, fg_color="red", width=540)
        self.footer_frame = customtkinter.CTkFrame(self.root, fg_color="blue", height=100)

        # interaction block
        self.title_entry = customtkinter.CTkEntry(self.header_frame, width=400, placeholder_text='Title')
        self.canvas = tk.Canvas(self.left_body_frame, width=171, height=549)
        self.body_model = tk.PhotoImage(file='assets/model_body.png') # 171 * 549
        self.commentary_entry = customtkinter.CTkTextbox(
            self.right_body_frame,
            width=500, #TODO peut etre augmenter ca
            height=400,
        )
        if config is None:
            with open("assets/model_commentary_entry.txt", "r") as txt_file:
                self.commentary_entry.insert("0.0", txt_file.read())

        # button
        self.debug_button = customtkinter.CTkButton(self.footer_frame, text="Debug", command=self._debug)
        self.save_button = customtkinter.CTkButton(self.footer_frame, text="Save", command=self._save)

        # setup
        self._setup_chrono()
        self._setup_round()
        self._setup_hit()

        # load from memory
        if config is not None:
            self._load(config)

        self._create_gui()
        self.root.mainloop()

################################################################################
#############################      GUI      ####################################
################################################################################

    def _create_gui(self):
        # HEADER
        self.header_frame.pack(fill=tk.X)
        self.title_entry.pack(side=tk.LEFT)
        ########
        
        # BODY
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        self.left_body_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._draw_hit_data()
        self.left_hit_choice_frame.pack(side=tk.LEFT)
        self.canvas.pack(side=tk.LEFT)

        for i in range(len(HIT_TYPE)):
            self.rb[i].grid(row=i, column=1, sticky='w')
        for i in range(len(HIT_TYPE), len(HIT_TYPE) + 5):
            self.round_checkbox[i - len(HIT_TYPE)].grid(row=i, column=0, sticky='w')

        self.label = customtkinter.CTkLabel(self.left_hit_stats_frame, text="Takedown")
        self.label.grid(                row=0, column=1, padx=5, pady=1, sticky="w")
        self.del_takedown_button.grid(  row=1, column=0, padx=5, pady=5, sticky="w")
        self.nb_takedown.grid(          row=1, column=1, padx=5, pady=5, sticky="w")
        self.add_takedown_button.grid(  row=1, column=2, padx=5, pady=5, sticky="w")

        self.hit_percent_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="w") # lui est peut etre dans la fonction juste au dessus

        self.time_label.grid(row=3, column=0, sticky="w")
        self.start_stop_button.grid(row=3, column=1, sticky="w")
        self.reset_button.grid(row=3, column=2, sticky="w")

        self.left_hit_stats_frame.pack(side=tk.LEFT)

        ########
        self.right_body_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.commentary_entry.pack(side=tk.BOTTOM)
        ########

        # FOOTER
        self.footer_frame.pack(fill=tk.X)
        self.debug_button.pack(side=tk.RIGHT)
        self.save_button.pack(side=tk.RIGHT)
        ########

        # # EVENTS
        self.canvas.bind("<Button-1>", self._add_letter_left)
        self.canvas.bind("<Button-3>", self._add_letter_right)
        self.root.bind_all("<Control-y>", self._redo)
        self.root.bind_all("<Control-z>", self._undo)

################################################################################
#############################      CHRONO      #################################
################################################################################

    def _setup_chrono(self):
        self.start_time = None
        self.is_running = False
        self.time_var = tk.StringVar()
        self.time_var.set("00:00:00")

        self.time_label = customtkinter.CTkLabel(
            self.left_hit_stats_frame, textvariable=self.time_var, font=("Helvetica", 24))
        self.start_stop_button = customtkinter.CTkButton(
            self.left_hit_stats_frame, text="Start/Stop", command=self._start_stop_timer)
        self.reset_button = customtkinter.CTkButton(
            self.left_hit_stats_frame, text="Reset", command=self._reset_timer)

    def _start_stop_timer(self):
        if self.is_running:
            self.is_running = False
            self.save = self.start_time
        else:
            if self.start_time is None:
                self.start_time = default_timer()
            self.is_running = True
            self._update_time()

    def _update_time(self):
        if self.is_running:
            elapsed_time = default_timer() - self.start_time
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            str_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

            self.time_var.set(str_time)
            self.root.after(1000, self._update_time)

    def _reset_timer(self):
        self.start_time = None
        self.is_running = False
        self.time_var.set("00:00:00")

################################################################################
#############################      HIT      ####################################
################################################################################

    def _setup_hit(self):
        self.previous_hits = []  # list for CTRL+y / CTRL+z
        self.hit_to_hide = []
        self.rb = []
        for i, rb_label in enumerate(HIT_TYPE):
            show_hit_switch = customtkinter.CTkSwitch(self.left_hit_choice_frame, text='',
                command=lambda i=i: self._hide_hit(i), width=35, height=25)
            show_hit_switch.grid(row=i, column=0, sticky='w')
            # show_hit_switch.pack()
            show_hit_switch.select()  # turn on by default the switch

            tmp = customtkinter.CTkRadioButton(self.left_hit_choice_frame, text=rb_label,
                                value=i, variable=self.champs['hit_type'])
            self.rb.append(tmp)

        self.takedown = tk.IntVar()
        self.nb_takedown = customtkinter.CTkLabel(self.left_hit_stats_frame,
            textvariable=self.takedown, font=("Helvetica", 16),)
        self.del_takedown_button = customtkinter.CTkButton(self.left_hit_stats_frame,
            text="-", command=lambda i=-1: self._update_takedown(i),
            width=35, height=25)
        self.add_takedown_button = customtkinter.CTkButton(self.left_hit_stats_frame,
            text="+", command=lambda i=1: self._update_takedown(i),
            width=35, height=25)

        self.hit_percent_label = tk.Label(
            self.left_hit_stats_frame,
            text=self._get_nb_and_percent_of_hits(),
            justify=tk.LEFT
        )

    def _hide_hit(self, hit):
        if hit in self.hit_to_hide:
            self.hit_to_hide.remove(hit)
        else:
            self.hit_to_hide.append(hit)
        self._draw_hits()
        self._draw_hit_data()

    def _update_takedown(self, value):
        self.memory['takedown'] += value
        self.takedown.set(self.memory['takedown'])

    def _draw_hit_data(self):
        self._draw_hits() # ca fonctionne mais peut etre pas la meilleure chose
        self.hit_percent_label.config(text=self._get_nb_and_percent_of_hits())

    def _get_nb_and_percent_of_hits(self, to_string=True):
        n_hit_list = [{'n': 0, 'type': hit_t, 'percent': 0} for hit_t in HIT_TYPE]

        # count how many hit
        for _round in self.rounds_selected:
            for i in range(len(self.memory['hits'][_round])):
                if HIT_TYPE.index(self.memory['hits'][_round][i]['type']) in self.hit_to_hide:
                    continue
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
                string_to_show += str(case['percent']) + '% - ' + str(case['n']) + ' ' + str(case['type']) + '\n'
            return string_to_show
        else:
            return n_hit_list

    def _draw_hits(self):
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.body_model)
        for round in self.rounds_selected:
            for i in range(len(self.memory['hits'][round])):
                if not HIT_TYPE.index(self.memory['hits'][round][i]['type']) in self.hit_to_hide:
                    self._add_hit(
                        self.memory['hits'][round][i]['pos'],
                        self.memory['hits'][round][i]['type'],
                        self.memory['hits'][round][i]['side'],
                        self.memory['hits'][round][i]['color']
                    )

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

################################################################################
#############################      ROUND      ##################################
################################################################################

    def _setup_round(self):
        self.rounds_selected = [0]
        self.round_checkbox = []
        for i in range(5):
            button_text = "Round {}".format(i+1)
            round_checkbox = customtkinter.CTkCheckBox(
                self.left_hit_choice_frame, text=button_text,
                variable=tk.IntVar(),
                command=lambda i=i: self._select_round_click(i)
            )
            if i == 0:
                round_checkbox.select()
            self.round_checkbox.append(round_checkbox)

    def _select_round_click(self, button_index):
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.body_model)
        if button_index in self.rounds_selected:
            self.rounds_selected.remove(button_index)
        else:
            self.rounds_selected.append(button_index)

        # Draw only hits of rounds selected
        self._draw_hits()
        self._draw_hit_data()

################################################################################
#############################      MEMORY      #################################
################################################################################

    def _save(self):
        """ Write self.memory variable in plk file to save it
        """
        self.memory['filename'] = self.title_entry.get() + '.plk'
        self.memory['commentary'] = self.commentary_entry.get('1.0', tk.END)
        self.memory['ground_control'] = self.time_var.get()
        with open('saves/' + str(self.title_entry.get()) + '.plk', 'wb') as file:
            pickle.dump(self.memory, file)
        print('saving with name: ' + str(self.title_entry.get()) + '.plk')

    def _load(self, path_save: str):
        """ Load the data from plk file

        Args:
            path_save (string): path get with argv to load the project
        """
        with open(path_save, 'rb') as file:
            self.memory = pickle.load(file)
            # print('self.memory', self.memory)
            self._initialize_canvas()
        
        if self.memory['filename']:  # ! Ca peut peter car j'ai mis = None
            self.title_entry.insert(tk.INSERT, self.memory['filename'][:-4])

        if self.memory['commentary']:
            self.commentary_entry.insert(tk.INSERT, self.memory['commentary'])

    def _initialize_canvas(self):
        """ Used to setup project variables when you load a file
        """
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

################################################################################
#############################      DEBUG      ##################################
################################################################################

    def _debug(self):
        """ Function to debug easily when button is pressed
        """
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
