import pygame
from button import Button
from tools import draw_text
from sys import argv

X = 1700
Y = 800

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (75, 75, 75)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PINK = (255, 182, 193)
PURPLE = (128, 0, 128)

TEXTCOLOR = (0, 0, 0)

# faire un choix de couleur pour le coup - kick - poing - coudes - cross - jab - ...
# JAB
# CROCHET
# UPPERCUT
# OVERHAND
# HIT TYPES
JAB = 0
HOOK = 1
UPPERCUT = 2
OVERHAND = 3 # Pas fait pour l'instant

# kICKS
CLMH = 4 # Calf, low, middle and high (its depend where is placed)

# ELBOWS
# KNEES
ELBOW = 5
KNEES = 6

# superposer des images et en afficher qu'une ou deux ...
# superposer les couches des différents coups (seulement kick, seulement direct, ...) et en afficher qu'une ou deux ...
# effacer des points
# trouver un systeme pour savoir si c'est gauche ou droite
# algo pour regrouper les coups qui sont proches
# graphique a la fin
# graphique hexagonal sur les différents coup
# chrono pour le temps de controle au sol

def draw_hit(screen, font, hit):
	if hit['type'] == HOOK:
		draw_text(screen, font, 'H', hit['color'], hit['pos'])
	if hit['type'] == JAB:
		draw_text(screen, font, 'J', hit['color'], hit['pos'])
	if hit['type'] == UPPERCUT:
		draw_text(screen, font, 'U', hit['color'], hit['pos'])
	if hit['type'] == OVERHAND:
		draw_text(screen, font, 'O', hit['color'], hit['pos'])
	if hit['type'] == CLMH:
		draw_text(screen, font, 'K', hit['color'], hit['pos'])
	if hit['type'] == ELBOW:
		draw_text(screen, font, 'E', hit['color'], hit['pos'])
	if hit['type'] == KNEES:
		draw_text(screen, font, 'G', hit['color'], hit['pos'])

COLOR_HIT = [BLUE,RED,GREEN,ORANGE,PINK,CYAN,PURPLE]

def disable_all_buttons(button_hit_type_list):
	for i in range(len(button_hit_type_list)):
		button_hit_type_list[i]['button'].is_selected = False

def disable_all_round_buttons(button_round_list):
	for i in range(len(button_round_list)):
		button_round_list[i].is_selected = False

import pickle
import random
def save_variable(var, name = random.randint(0, 1000)):
	with open(str(name) + '.plk', 'wb') as file:
	    pickle.dump(var, file)
	print('saving with name: ' + str(name) + '.plk')

def load_variable(path_save):
	with open(path_save, 'rb') as file:
		myvar = pickle.load(file)
	return myvar

def engine(argv):
	hit_list = [[], [], [], [], []]
	ctrl_y_list = []
	round_selected = 0
	actual_hit_type = 0

	if len(argv) > 1:
		if argv[0] == '-l':
			hit_list = load_variable(argv[1])
			print('load_variable')

	BASE = 50
	jab_button = Button(70, BASE, 50, 100, BLUE, 0, 0, "Jab", WHITE, is_selected=True)
	hook_button = Button(70, BASE + 50, 50, 100, RED, 0, 0, "Hook", WHITE, is_selected=False)
	uppercut_button = Button(70, BASE + 2*(50), 50, 100, GREEN, 0, 0, "Uppercut", WHITE, is_selected=False)
	overhand_button = Button(70, BASE + 3*(50), 50, 100, ORANGE, 0, 0, "Overhand", WHITE, is_selected=False)
	clmh_button = Button(70, BASE + 4*(50), 50, 100, MAGENTA, 0, 0, "Kick", WHITE, is_selected=False)
	elbow_button = Button(70, BASE + 5*(50), 50, 100, CYAN, 0, 0, "Elbow", WHITE, is_selected=False)
	knees_button = Button(70, BASE + 6*(50), 50, 100, PURPLE, 0, 0, "Knees", WHITE, is_selected=False)
	button_hit_type_list = [{'button': jab_button, 'type': JAB},{'button': hook_button, 'type': HOOK},{'button': uppercut_button, 'type': UPPERCUT},{'button': overhand_button, 'type': OVERHAND},{'button': clmh_button, 'type': CLMH},{'button': elbow_button, 'type': ELBOW},{'button': knees_button, 'type': KNEES}]

	SIZE_X = 70
	POS_X = 10
	IMG_SIZE_Y = 549
	round1_button = Button(POS_X, BASE + IMG_SIZE_Y , 50, SIZE_X, WHITE, 0, 0, "R1", BLACK, is_selected=True)
	round2_button = Button(POS_X+SIZE_X, BASE + IMG_SIZE_Y , 50, SIZE_X, WHITE, 0, 0, "R2", BLACK, is_selected=False)
	round3_button = Button(POS_X+SIZE_X*2, BASE + IMG_SIZE_Y , 50, SIZE_X, WHITE, 0, 0, "R3", BLACK, is_selected=False)
	round4_button = Button(POS_X+SIZE_X*3, BASE + IMG_SIZE_Y , 50, SIZE_X, WHITE, 0, 0, "R4", BLACK, is_selected=False)
	round5_button = Button(POS_X+SIZE_X*4, BASE + IMG_SIZE_Y , 50, SIZE_X, WHITE, 0, 0, "R5", BLACK, is_selected=False)
	button_round_list = [round1_button, round2_button, round3_button, round4_button, round5_button]

	pygame.init()
	isRunning = True

	screen = pygame.display.set_mode((X, Y))
	imp = pygame.image.load('assets/model_body.png').convert()
	pygame.display.set_caption('Striking Analyse')
	pygame.display.set_icon(pygame.image.load('assets/icon.png'))
	font = pygame.font.Font('assets/OpenSans-Regular.ttf', 20)
	pygame.display.flip()

	while isRunning:
		screen.blit(imp, (170, BASE))
		for hit in hit_list[round_selected]:
			draw_hit(screen, font, hit)

		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				isRunning = False

			if event.type == pygame.KEYDOWN:
				# S - Save file
				if event.key == pygame.K_s:
					save_variable(hit_list)

				# CTRL + Z
				if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_LCTRL and len(hit_list[round_selected]) > 0:
					tmp = hit_list[round_selected].pop()
					ctrl_y_list.append(tmp)
				# CTRL + Y
				if event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_LCTRL and len(ctrl_y_list) > 0:
					new = ctrl_y_list.pop()
					hit_list[round_selected].append(new)

			# LEFT CLICK - Point a hit
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()
				# print('mouse-', pos[0], pos[1])
				# print(event.button)
				if pos[0] >= 170 and pos[0] <= 340 and pos[1] >= 50 and pos[1] <= 600:
					hit_list[round_selected].append({
						'pos': pos,
						'color': COLOR_HIT[actual_hit_type],
						'type': actual_hit_type,
						'side': 'right' if event.button == 3 else 'left'
					})
					# print(hit_list)

			# print('tik: ', hit_list[round_selected])

			draw_text(screen, font, 'Gane vs Lewis', WHITE, (10, 20))

			# HIT SELECTION
			for i in range(len(button_hit_type_list)):
				if button_hit_type_list[i]['button'].draw_rect(screen, font, event):
					disable_all_buttons(button_hit_type_list)
					button_hit_type_list[i]['button'].is_selected = True
					actual_hit_type = button_hit_type_list[i]['type']
			# ROUND SELECTION
			for i in range(len(button_round_list)):
				if button_round_list[i].draw_rect(screen, font, event):
					disable_all_round_buttons(button_round_list)
					button_round_list[i].is_selected = True
					round_selected = i

		pygame.display.update()

		# END LOOP

	pygame.quit()

def main(argv):
    engine(argv)

if __name__ == '__main__':
    main(argv[1:])
