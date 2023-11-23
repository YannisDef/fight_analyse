import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from matplotlib.patches import Rectangle
from matplotlib.colors import LogNorm
from matplotlib import cm
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image

# Données
data = [
    {'pos': (100, 74), 'type': 1, 'side': 'right'}, {'pos': (87, 214), 'type': 4, 'side': 'right'}, 
    {'pos': (112, 346), 'type': 4, 'side': 'right'}, {'pos': (115, 342), 'type': 4, 'side': 'right'}, 
    {'pos': (131, 349), 'type': 4, 'side': 'right'}, {'pos': (130, 345), 'type': 4, 'side': 'right'}, 
    {'pos': (129, 354), 'type': 4, 'side': 'right'}, {'pos': (84, 67), 'type': 0, 'side': 'right'}, 
    {'pos': (87, 236), 'type': 4, 'side': 'right'}, {'pos': (99, 78), 'type': 0, 'side': 'right'}, 
    {'pos': (127, 334), 'type': 4, 'side': 'right'}, {'pos': (88, 77), 'type': 0, 'side': 'right'}, 
    {'pos': (128, 361), 'type': 4, 'side': 'right'}, {'pos': (123, 369), 'type': 4, 'side': 'right'}, 
    {'pos': (88, 220), 'type': 4, 'side': 'right'}, {'pos': (89, 57), 'type': 0, 'side': 'right'}, 
    {'pos': (112, 358), 'type': 4, 'side': 'right'}, {'pos': (116, 324), 'type': 4, 'side': 'right'}, 
    {'pos': (82, 63), 'type': 0, 'side': 'right'}, {'pos': (69, 54), 'type': 4, 'side': 'left'}, 
    {'pos': (128, 342), 'type': 4, 'side': 'right'}, {'pos': (81, 224), 'type': 4, 'side': 'right'}, 
    {'pos': (118, 225), 'type': 4, 'side': 'right'}, {'pos': (82, 69), 'type': 0, 'side': 'left'}, 
    {'pos': (82, 69), 'type': 0, 'side': 'left'}, {'pos': (82, 69), 'type': 0, 'side': 'right'}, 
    {'pos': (128, 320), 'type': 4, 'side': 'right'}, {'pos': (88, 68), 'type': 0, 'side': 'left'}
]

# Créer une nouvelle figure
fig, ax = plt.subplots(figsize=(10, 13))

# Charger l'image
img = np.array(Image.open("model_body.png"))

# Afficher l'image
ax.imshow(img, extent=[0, 500, 0, 685])

# Préparer les données pour le graphique de contour
x = [point['pos'][0] for point in data]
y = [point['pos'][1] for point in data]
types = [point['type'] for point in data]

# Tracer les contours en fonction de la fréquence
contour = ax.tricontourf(x, y, types, cmap=cm.viridis, levels=20)

# Ajouter une barre de couleur
cbar = fig.colorbar(contour, ax=ax, ticks=MaxNLocator(nbins=5))
cbar.set_label('Fréquence de coup')

# Afficher le graphique
plt.show()