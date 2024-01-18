# https://customtkinter.tomschimansky.com/documentation/widgets/textbox

import tkinter as tk

import pickle
import json
from sys import argv
import customtkinter
import tkcap

from PIL import Image, ImageTk

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
    "CLMH (Kick)",
    "Elbow",
    "Knee",
]

# TODO: feat
#// - compter le nombre de takedown
#// - recalculer les % quand on cache un coup
#// - systeme de commentaire par defaut
#// - afficher le pourcentage de droite et de gauche
#// - afficher nombre de coup au corps, tete, jambes
#!- probleme chrono ground control
# - faire un graphique de représentation des hits
# - deuxieme corps couleur naturelle et de + en + rouge
# - front kick ou middle ?
# - systeme de prise de note sur un coup
# - diviser encore le corps en deux pour que les zones rouges soient plus précises
# - systeme de notation hexagonal du combattant
# - systeme de creation de pdf
# - systeme d'ouverture de fichier ...
# - entrer les stats des deux combattans (age, poids, garde, ...)
# - separer les coups gauches des coups droits durant le trie d'affichage
# - savoir combien le combattant a lancé de hooks et combien ont touchés du coup

# - faire une video pour presenter les analyses

# TODO: Optimisation
#// - je pense qu'on peut optimiser le code car je recréer certaines variables a chaque tour de boucle
#// - faire des fonctions pour init différentes parties de l'app
# - il y a des problemes avec la variable self.champs

# TODO: Style
#// - trouver un moyen de différencier les coups gauches des coups droits
#// - le bloc note doit etre plus grand
# - faire des plus beaux boutons que les Show -> faire des yeux
# - regrouper les hits proches
# - legende ? comprendre la différence entre rouge et bleu ? C pour kick c'est nul
# - modifier le style complet de l'app (couleurs, style, ...) / theme.json
# - faire un schema bien organisé du style de l'app
    #// - Organiser mieux les boutons et modules... surement en utilisant full grid

class App:
    def __init__(self, config=None):
        # setup window
        self.root = customtkinter.CTk()
        self.root.title('Fight Analyse')
        self.root.iconphoto(False, tk.PhotoImage(file="assets/icon.png"))
        self.root.geometry("1500x700")
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
        self.header_frame = customtkinter.CTkFrame(self.root, fg_color="black", height=100)
        self.body_frame = customtkinter.CTkFrame(self.root)
        self.left_body_frame = customtkinter.CTkFrame(self.body_frame, fg_color="black", width=540)
        self.left_hit_choice_frame = customtkinter.CTkFrame(self.left_body_frame, width=540, fg_color="black")
        self.left_hit_stats_frame = customtkinter.CTkFrame(self.left_body_frame, width=540, fg_color="black")
        self.right_body_frame = customtkinter.CTkFrame(self.body_frame, fg_color="black", width=540)
        self.footer_frame = customtkinter.CTkFrame(self.root, fg_color="black", height=100)

        # interaction block
        self.title_entry = customtkinter.CTkEntry(self.header_frame, width=500, placeholder_text='Title')
        self.canvas = tk.Canvas(self.left_body_frame, bg='white', width=171, height=549)

        self.body_model = tk.PhotoImage(file='assets/model_body.png') # 171 * 549

        self.commentary_entry = customtkinter.CTkTextbox(
            self.right_body_frame,
            width=500, #TODO peut etre augmenter ca
            height=500,
        )
        if config is None:
            with open("assets/model_commentary_entry.txt", "r") as txt_file:
                self.commentary_entry.insert("0.0", txt_file.read())

        # button
        self.debug_button = customtkinter.CTkButton(self.footer_frame, text="Debug", command=self._debug)
        self.save_button = customtkinter.CTkButton(self.footer_frame, text="Save", command=self._save)
        self.show_repartition_v = False
        self.show_repartition_button = customtkinter.CTkButton(self.left_hit_choice_frame, text="Show", command=self.show_repartition)

        self.images = []  # to hold the newly created image

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
        
        # BODY
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        # LEFT
        self.left_body_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._draw_hit_data()
        self.left_hit_choice_frame.pack(side=tk.LEFT)
        self.canvas.pack(side=tk.LEFT)

        for i in range(len(HIT_TYPE)):
            self.rb[i].grid(row=i, column=1, sticky='w')
        for i in range(len(HIT_TYPE), len(HIT_TYPE) + 5):
            self.round_checkbox[i - len(HIT_TYPE)].grid(row=i, column=0, sticky='w')
        self.show_repartition_button.grid(row=len(HIT_TYPE) + 5 + 1, column=0, sticky='w')

        self.label = customtkinter.CTkLabel(self.left_hit_stats_frame, text="Takedown")
        self.label.grid(                row=0, column=1, padx=5, pady=1, sticky="w")
        self.del_takedown_button.grid(  row=1, column=0, padx=5, pady=5, sticky="w")
        self.nb_takedown.grid(          row=1, column=1, padx=5, pady=5, sticky="w")
        self.add_takedown_button.grid(  row=1, column=2, padx=5, pady=5, sticky="w")

        self.hit_percent_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="w") # lui est peut etre dans la fonction juste au dessus

        self.time.grid(row=3, column=0, padx=2)
        self.startstop_chrono_button.grid(row=4, column=0, padx=2)
        self.reset_chrono_button.grid(row=4, column=1, padx=2)

        self.left_hit_stats_frame.pack(side=tk.LEFT)

        # RIGHT
        self.right_body_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.commentary_entry.pack(side=tk.BOTTOM)

        # FOOTER
        self.footer_frame.pack(fill=tk.X)
        self.debug_button.pack(side=tk.RIGHT)
        self.save_button.pack(side=tk.RIGHT)

        # EVENTS
        self.canvas.bind("<Button-1>", self._add_letter_left)
        self.canvas.bind("<Button-3>", self._add_letter_right)
        self.root.bind_all("<Control-y>", self._redo)
        self.root.bind_all("<Control-z>", self._undo)

################################################################################
#############################      CHRONO      #################################
################################################################################

    def _setup_chrono(self):
        self.time = tk.Label(self.left_hit_stats_frame, width=20, font=("", "18"), background='black', fg='white')
        self.startstop_chrono_button = customtkinter.CTkButton(self.left_hit_stats_frame, text='⏯︎', command=self._start__stop_chronometer)
        self.reset_chrono_button = customtkinter.CTkButton(self.left_hit_stats_frame, text='⏹︎', command=self._reset_chronometer)

        self.seconds = 0
        self.is_running = False
        self.process = None

    def _format_time(self, seconds):
        return '{:02d}:{:02d}'.format(seconds // 60, seconds % 60)

    def _start__stop_chronometer(self):
        if self.is_running:
            self._stop_chronometer()
        else:
            self._start_chronometer()

    def _start_chronometer(self):
        self._stop_chronometer()
        self.is_running = True
        self.process = self.root.after(1000, self._start_chronometer)
        self.seconds += 1
        self.time['text'] = self._format_time(self.seconds)

    def _stop_chronometer(self):
        try:
            self.root.after_cancel(self.process)
        except:
            pass
        self.is_running = False

    def _reset_chronometer(self):
        self._stop_chronometer()
        self.seconds = 0
        self.time['text'] = self._format_time(self.seconds)

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
            textvariable=self.takedown, font=("Helvetica", 18),)
        self.del_takedown_button = customtkinter.CTkButton(self.left_hit_stats_frame,
            text="-", command=lambda i=-1: self._update_takedown(i),
            width=35, height=25)
        self.add_takedown_button = customtkinter.CTkButton(self.left_hit_stats_frame,
            text="+", command=lambda i=1: self._update_takedown(i),
            width=35, height=25)

        self.hit_percent_label = tk.Label(
            self.left_hit_stats_frame,
            text=self._get_nb_and_percent_of_hits(),
            justify=tk.LEFT,
            background='black',
            fg='white'
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

    def _create_rectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.root.winfo_rgb(fill) + (alpha,)
            image = Image.new('RGBA', (x2-x1, y2-y1), fill)
            self.images.append(ImageTk.PhotoImage(image))
            self.canvas.create_image(x1, y1, image=self.images[-1], anchor='nw')
        self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    def _draw_hit_data(self):
        self._create_rectangle(0, 0, 171, 546, fill='white')
        txt, n_hit_target = self._get_nb_and_percent_of_hits()
        self.hit_percent_label.config(text=txt)

        # n_hit_target to percent
        n_hit = n_hit_target['head'] + n_hit_target['body'] + n_hit_target['leg']
        if n_hit != 0 and self.show_repartition_v:
            self._create_rectangle(0, 0, 171, 107, fill='red', alpha=(n_hit_target['head'] * 100 / n_hit) / 100)
            self._create_rectangle(0, 107, 171, 306, fill='red', alpha=(n_hit_target['body'] * 100 / n_hit) / 100)
            self._create_rectangle(0, 306, 171 + 306, 171 + 400, fill='red', alpha=(n_hit_target['leg'] * 100 / n_hit) / 100)

        self._draw_hits() # ca fonctionne mais peut etre pas la meilleure chose

    def show_repartition(self):
        self.show_repartition_v = not self.show_repartition_v
        self._draw_hit_data()

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

    def _get_nb_and_percent_of_hits(self, to_string=True):
        n_hit_list = [{'n': 0, 'type': hit_t, 'percent': 0} for hit_t in HIT_TYPE]
        n_hit_side = {'left': 0, 'right': 0}
        n_hit_target = {'head': 0, 'body': 0, 'leg': 0}

        # count how many hit
        for _round in self.rounds_selected:
            for i in range(len(self.memory['hits'][_round])):
                if HIT_TYPE.index(self.memory['hits'][_round][i]['type']) in self.hit_to_hide:
                    continue
                n_hit_list[HIT_TYPE.index(self.memory['hits'][_round][i]['type'])]['n'] += 1
                n_hit_side[self.memory['hits'][_round][i]['side']] += 1

                if self.memory['hits'][_round][i]['pos']['y'] < 107:
                    n_hit_target['head'] += 1
                elif self.memory['hits'][_round][i]['pos']['y'] < 306:
                    n_hit_target['body'] += 1
                else:
                    n_hit_target['leg'] += 1

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

        try:
            percent_of_left_hit = round(n_hit_side['left'] * 100 / (n_hit_side['left'] + n_hit_side['right']), 1)
        except ZeroDivisionError:
            percent_of_left_hit = 0

        try:
            percent_of_head_hit = round(n_hit_target['head'] * 100 / (n_hit_target['head'] + n_hit_target['body'] + n_hit_target['leg']), 1)
            percent_of_body_hit = round(n_hit_target['body'] * 100 / (n_hit_target['head'] + n_hit_target['body'] + n_hit_target['leg']), 1)
            percent_of_legs_hit = round(n_hit_target['leg'] * 100 / (n_hit_target['head'] + n_hit_target['body'] + n_hit_target['leg']), 1)
        except ZeroDivisionError:
            percent_of_head_hit = 0
            percent_of_body_hit = 0
            percent_of_legs_hit = 0

        # create cool string to show with list
        if to_string:
            string_to_show = ''
            string_to_show += str(percent_of_head_hit) + '% (' + str(n_hit_target['head']) + ') head | ' + str(percent_of_body_hit) + '% (' + str(n_hit_target['body']) + ') body | ' + str(percent_of_legs_hit) + '% (' + str(n_hit_target['leg']) + ') leg\n\n'
            string_to_show += str(percent_of_left_hit) + '% (' + str(n_hit_side['left']) + ') lefts | ' + str(round(100 - percent_of_left_hit, 1) if n_hit_side['right'] > 0 else 0) + '% (' + str(n_hit_side['right']) + ') rights\n\n'
            for case in n_hit_list:
                string_to_show += str(case['percent']) + '% - ' + str(case['n']) + ' ' + str(case['type']) + '\n'
            string_to_show = string_to_show[:-1]
            return string_to_show, n_hit_target
        else:
            return n_hit_list

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
            'white',
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
        self.memory['ground_control'] = self.seconds
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
        self.takedown.set(self.memory['takedown'])

        self.seconds = self.memory.get('ground_control', 0)
        self.time['text'] = self._format_time(self.seconds)

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
