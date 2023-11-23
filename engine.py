import pygame

pygame.init()
X = 250
Y = 600

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

screen = pygame.display.set_mode((X, Y))
imp = pygame.image.load('model_body.png').convert()
pygame.display.set_caption('Striking Analyse')
pygame.display.set_icon(pygame.image.load('icon.png'))

pygame.display.flip()
isRunning = True

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

actual_hit_type = 0

# superposer des images et en afficher qu'une ou deux ...
# superposer les couches des différents coups (seulement kick, seulement direct, ...) et en afficher qu'une ou deux ...
# effacer des points
# trouver un systeme pour savoir si c'est gauche ou droite
# algo pour regrouper les coups qui sont proches
# graphique a la fin
# graphique hexagonal sur les différents coup
# chrono pour le temps de controle au sol

font = pygame.font.Font('OpenSans-Regular.ttf', 20)

class Button:
    def __init__(self, x, y, height, width, colour, border, curve, text, textColour, is_selected = False):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.colour = colour
        self.border = border
        self.curve = curve
        self.text = text
        self.textColour = textColour
        self.is_selected = is_selected

    def draw_rect(self, event):
        button = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.colour if self.is_selected else GRAY, button, self.border, self.curve)
        if self.text != "":
            self.draw_text()
        pygame.display.flip()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if button.collidepoint(event.pos):
                return True

        return False

    def draw_text(self):
        text_surf = font.render(self.text, True, self.textColour)
        text_rect = text_surf.get_rect(center=(self.x+self.width//2, self.y+self.height//2))
        screen.blit(text_surf, text_rect)

def draw_text(txt, color, pos):
	txtsurf = font.render(txt, True, color)
	screen.blit(txtsurf, (pos[0] - 5, pos[1] - 20))

def draw_hit(hit):
	# pygame.draw.circle(screen, RED, hit['pos'], 5)
	if hit['type'] == HOOK:
		draw_text('H', RED, hit['pos'])
	if hit['type'] == JAB:
		draw_text('J', BLUE, hit['pos'])
	if hit['type'] == UPPERCUT:
		draw_text('U', GREEN, hit['pos'])
	if hit['type'] == OVERHAND:
		draw_text('O', ORANGE, hit['pos'])
	if hit['type'] == CLMH:
		draw_text('K', YELLOW, hit['pos'])
	if hit['type'] == ELBOW:
		draw_text('E', CYAN, hit['pos'])
	if hit['type'] == KNEES:
		draw_text('G', PURPLE, hit['pos'])

def disable_all_buttons():
	jab_button.is_selected = False
	hook_button.is_selected = False
	uppercut_button.is_selected = False
	overhand_button.is_selected = False
	clmh_button.is_selected = False
	elbow_button.is_selected = False
	knees_button.is_selected = False

def disable_all_round_buttons():
	round1_button.is_selected = False
	round2_button.is_selected = False
	round3_button.is_selected = False
	round4_button.is_selected = False
	round5_button.is_selected = False

import pickle
import random
def save_variable(var, name = random.randint(0, 1000)):
	with open(str(name) + '.plk', 'wb') as file:
	    pickle.dump(var, file)

def load_variable(path_save):
	with open(path_save, 'rb') as file:
		myvar = pickle.load(file)
	return myvar

hit_list = [[], [], [], [], []]
ctrl_y_list = []
round_selected = 0

jab_button = Button(250, 171 / 2, 171 - X, 171 - X, BLUE, 0, 7, "Jab", WHITE, is_selected=True)
hook_button = Button(250, 171, 171 - X, 171 - X, RED, 0, 7, "Hook", WHITE, is_selected=False)
uppercut_button = Button(250, 171 + (171/2), 171 - X, 171 - X, GREEN, 0, 7, "Uppercut", WHITE, is_selected=False)
overhand_button = Button(250, 171 + 2*(171/2), 171 - X, 171 - X, ORANGE, 0, 7, "Overhand", WHITE, is_selected=False)
clmh_button = Button(250, 171 + 3*(171/2), 171 - X, 171 - X, MAGENTA, 0, 7, "Kick", WHITE, is_selected=False)
elbow_button = Button(250, 171 + 4*(171/2), 171 - X, 171 - X, CYAN, 0, 7, "Elbow", WHITE, is_selected=False)
knees_button = Button(250, 171 + 5*(171/2), 171 - X, 171 - X, PURPLE, 0, 7, "Knees", WHITE, is_selected=False)

round1_button = Button(0, Y - 50, 50, 50, WHITE, 0, 7, "R1", BLACK, is_selected=True)
round2_button = Button(50, Y - 50, 50, 50, WHITE, 0, 7, "R2", BLACK, is_selected=False)
round3_button = Button(100, Y - 50, 50, 50, WHITE, 0, 7, "R3", BLACK, is_selected=False)
round4_button = Button(150, Y - 50, 50, 50, WHITE, 0, 7, "R4", BLACK, is_selected=False)
round5_button = Button(200, Y - 50, 50, 50, WHITE, 0, 7, "R5", BLACK, is_selected=False)

from sys import argv

if len(argv) > 1:
	if argv[1] == '-l':
		hit_list = load_variable(argv[2])

while isRunning:
	screen.blit(imp, (0, 0))
	for hit in hit_list[round_selected]:
		draw_hit(hit)

	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			isRunning = False

		if event.type == pygame.KEYDOWN:
			# S - Save the image
			if event.key == pygame.K_s:
				rect = pygame.Rect(0, 0, 171, 549)
				sub = screen.subsurface(rect)
				pygame.image.save(sub, "fight" + str(len(hit_list[0])) + ".png")
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
			# print(pos[0], pos[1])
			# print(event.button)
			if pos[0] <= 171 and pos[1] <= 546:
				hit_list[round_selected].append({
					'pos': pos,
					'type': actual_hit_type,
					'side': 'right' if event.button == 3 else 'left'
				})
				# print(hit_list)

		# print('tik: ', hit_list[round_selected])

		# HIT SELECTION
		if hook_button.draw_rect(event):
			actual_hit_type = HOOK
			disable_all_buttons()
			hook_button.is_selected = True
		if jab_button.draw_rect(event):
			actual_hit_type = JAB
			disable_all_buttons()
			jab_button.is_selected = True
		if uppercut_button.draw_rect(event):
			actual_hit_type = UPPERCUT
			disable_all_buttons()
			uppercut_button.is_selected = True
		if overhand_button.draw_rect(event):
			actual_hit_type = OVERHAND
			disable_all_buttons()
			overhand_button.is_selected = True
		if clmh_button.draw_rect(event):
			actual_hit_type = CLMH
			disable_all_buttons()
			clmh_button.is_selected = True
		if elbow_button.draw_rect(event):
			actual_hit_type = ELBOW
			disable_all_buttons()
			elbow_button.is_selected = True
		if knees_button.draw_rect(event):
			actual_hit_type = KNEES
			disable_all_buttons()
			knees_button.is_selected = True

		# ROUND SELECTION
		if round1_button.draw_rect(event):
			disable_all_round_buttons()
			round1_button.is_selected = True
			round_selected = 0
		if round2_button.draw_rect(event):
			disable_all_round_buttons()
			round2_button.is_selected = True
			round_selected = 1
		if round3_button.draw_rect(event):
			disable_all_round_buttons()
			round3_button.is_selected = True
			round_selected = 2
		if round4_button.draw_rect(event):
			disable_all_round_buttons()
			round4_button.is_selected = True
			round_selected = 3
		if round5_button.draw_rect(event):
			disable_all_round_buttons()
			round5_button.is_selected = True
			round_selected = 4

	pygame.display.update()

pygame.quit()
