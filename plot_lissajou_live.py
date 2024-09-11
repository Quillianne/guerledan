import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Charger les données sauvegardées
data_lissajou = np.load("data_lissajou.npy", allow_pickle=True)

# Extraire les coordonnées du bateau et de la cible
y_bateau_list = [entry[0][0] for entry in data_lissajou]  # x du bateau
x_bateau_list = [entry[0][1] for entry in data_lissajou]  # y du bateau
y_cible_list = [entry[1][0] for entry in data_lissajou]   # x de la cible
x_cible_list = [entry[1][1] for entry in data_lissajou]   # y de la cible

# Initialiser le graphique
fig, ax = plt.subplots()
boat_plot, = ax.plot([], [], 'bo-', label="Bateau (Bleu)")
target_plot, = ax.plot([], [], 'ro-', label="Cible (Rouge)")
ax.set_xlim(min(x_bateau_list + x_cible_list) - 1, max(x_bateau_list + x_cible_list) + 1)
ax.set_ylim(min(y_bateau_list + y_cible_list) - 1, max(y_bateau_list + y_cible_list) + 1)
ax.set_xlabel('Y')
ax.set_ylabel('X')
ax.set_title('Trajectoire du bateau et de la cible (live)')
ax.legend()
ax.grid(True)

# Fonction d'initialisation pour l'animation
def init():
    boat_plot.set_data([], [])
    target_plot.set_data([], [])
    return boat_plot, target_plot

# Fonction de mise à jour de l'animation (affiche point par point)
def update(frame):
    boat_plot.set_data(x_bateau_list[:frame], y_bateau_list[:frame])
    target_plot.set_data(x_cible_list[:frame], y_cible_list[:frame])
    return boat_plot, target_plot

# Animation : mise à jour du graphique à chaque frame
ani = FuncAnimation(fig, update, frames=len(x_bateau_list), init_func=init, interval=100, blit=True)

# Afficher le graphique en live
plt.show()
