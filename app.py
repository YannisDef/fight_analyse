# https://customtkinter.tomschimansky.com/documentation/widgets/textbox

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd

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
#!- Probleme chrono ground control
# - faire un graphique de représentation des hits
# - systeme de notation hexagonal du combattant
# - systeme de creation de pdf
# - systeme d'ouverture de fichier ...
# - entrer les stats des deux combattans (age, poids, ...)

# TODO: Optimisation
# - je pense qu'on peut optimiser le code car je recréer certaines variables a chaque tour de boucle
# - il y a des problemes avec la variable self.champs

# TODO: Style
#// - trouver un moyen de différencier les coups gauches des coups droits
# - Faire des plus beaux boutons que les Show -> faire des yeux
# - regrouper les hits proches
# - Legende ? comprendre la différence entre rouge et bleu ? C pour kick c'est nul
# - Modifier le style complet de l'app (couleurs, style, ...) / theme.json
# - Organiser mieux les boutons et modules...

class App:
    def __init__(self, config=None):
        self.root = customtkinter.CTk()
        self.root.geometry("1920x1080")
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("theme.json")
        self.root.title('Fight Analyse')

        photo = tk.PhotoImage(file="assets/icon.png")
        self.root.iconphoto(False, photo)

        self.empty_body_path = 'assets/model_body.png' # 171 * 549
        self.champs = {
            'hit_type': tk.IntVar(),
            'selected_rounds': tk.StringVar(),
        }
        # My variables
        self.left_frame = customtkinter.CTkFrame(self.root)

        self.canvas = tk.Canvas(self.left_frame, width=171, height=549)
        self.img = tk.PhotoImage(file=self.empty_body_path)
        
        self.rounds_selected = [0]
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

#! -----------------------------------------------------------------------------

        # x_positions = [item["pos"]["x"] for item in self.memory['hits'][0]]
        # y_positions = [item["pos"]["y"] for item in self.memory['hits'][0]]


        # # Changer la taille du graphique en pixels
        # dpi = 100  # points par pouce (DPI)
        # width, height = 171, 549  # dimensions en pixels
        # figsize = width / dpi, height / dpi

        # # Créer une grille pour représenter la densité des points
        # grid, xedges, yedges = np.histogram2d(x_positions, y_positions, bins=(width, height), range=[[0, width], [0, height]])
        # extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

        # # Créer le graphique avec une échelle de couleur basée sur la densité
        # fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        # im = ax.imshow(grid.T, extent=extent, origin='lower', cmap='Reds', alpha=0.7)
        # ax.set_xlabel('Position X')
        # ax.set_ylabel('Position Y')
        # ax.set_title('Graphique des Positions')

        # # Ajouter une barre de couleur (colorbar)
        # cbar = fig.colorbar(im, ax=ax, label='Densité')

        # # Inverser l'axe Y
        # ax.invert_yaxis()

        # # Créer la fenêtre Tkinter pour afficher le graphique
        # root = tk.Tk()
        # root.title('Graphique des Positions')

        # # Incorporer le graphique dans la fenêtre Tkinter
        # canvas = FigureCanvasTkAgg(fig, master=root)
        # canvas_widget = canvas.get_tk_widget()
        # canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # # Ajouter un bouton de fermeture de fenêtre
        # close_button = tk.Button(root, text='Fermer', command=root.destroy)
        # close_button.pack(side=tk.BOTTOM)

#! -----------------------------------------------------------------------------

        # ROUNDS
        for i in range(5):
            button_text = "Round {}".format(i+1)
            round_checkbox = customtkinter.CTkCheckBox(
                self.left_frame, text=button_text,
                variable=tk.IntVar(),
                command=lambda i=i: self._select_round_click(i)
            )
            if i == 0:
                round_checkbox.select()
            round_checkbox.pack()
        #####

        # PICTURE
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        #####

       # HIT BUTTONS
        button_frame = customtkinter.CTkFrame(self.root)
        for i, rb_label in enumerate(HIT_TYPE):
            show_hit_switch = customtkinter.CTkSwitch(button_frame, text='',
                command=lambda i=i: self._hide_hit(i), width=35, height=25)
            show_hit_switch.grid(row=i, column=0, sticky='w')
            show_hit_switch.select()  # turn on by default the switch

            rb = customtkinter.CTkRadioButton(button_frame, text=rb_label,
                                value=i, variable=self.champs['hit_type'])
            rb.grid(row=i, column=1, sticky='w')

        # Conteneur pour les boutons de takedown
        takedown_frame = customtkinter.CTkFrame(self.root)

        nb_takedown = customtkinter.CTkLabel(takedown_frame,
            textvariable=self.takedown, font=("Helvetica", 16),)
        del_takedown_button = customtkinter.CTkButton(takedown_frame,
            text="-", command=lambda i=-1: self._update_takedown(i),
            width=35, height=25)
        add_takedown_button = customtkinter.CTkButton(takedown_frame,
            text="+", command=lambda i=1: self._update_takedown(i),
            width=35, height=25)

        # Pack les boutons de takedown dans le conteneur takedown_frame
        del_takedown_button.pack(side=tk.BOTTOM)
        nb_takedown.pack(side=tk.BOTTOM)
        add_takedown_button.pack(side=tk.BOTTOM)

        # Pack le conteneur des boutons de takedown sous le conteneur des boutons HIT
        button_frame.pack(side=tk.LEFT)
        takedown_frame.pack(side=tk.LEFT)

        # Chrono
        self.time_label = customtkinter.CTkLabel(
            self.left_frame, textvariable=self.time_var, font=("Helvetica", 24))
        self.time_label.pack()

        # Button to start/stop the timer
        self.start_stop_button = customtkinter.CTkButton(
            self.left_frame, text="Start/Stop", command=self._start_stop_timer)
        self.reset_button = customtkinter.CTkButton(
            self.left_frame, text="Reset", command=self._reset_timer)
        self.start_stop_button.pack(padx=20, pady=10)
        self.reset_button.pack(padx=20, pady=10)
        #####
        self.left_frame.pack(side=tk.LEFT)

        self.right_frame = customtkinter.CTkFrame(self.root)
        # COMMENTARY
        self.commentary_entry = customtkinter.CTkTextbox(self.right_frame,
                                                         width=1000,
                                                         height=400)
        if self.memory['commentary']:
            self.commentary_entry.insert(tk.INSERT, self.memory['commentary'])
        self.commentary_entry.pack()
        #####
        self.right_frame.pack(side=tk.RIGHT)

        # NUMBER OF HITS
        self._draw_hit_data()
        #####

        # EVENTS
        self.canvas.bind("<Button-1>", self._add_letter_left)
        self.canvas.bind("<Button-3>", self._add_letter_right)

        self.root.bind_all("<Control-y>", self._redo)
        self.root.bind_all("<Control-z>", self._undo)
        #####

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
        self.hit_percent_label.pack(side=tk.LEFT)

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
        with open('saves/' + str(self.title_entry.get()) + '.plk', 'wb') as file:
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
