def draw_text(screen, font, txt, color, pos):
	txtsurf = font.render(txt, True, color)
	screen.blit(txtsurf, (pos[0] - 5, pos[1] - 20))