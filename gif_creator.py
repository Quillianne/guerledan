import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Charger les données sauvegardées
data_lissajou = np.load("data_lissajou_goated.npy", allow_pickle=True)

# Extraire les coordonnées du bateau et de la cible
y_bateau_list = [entry[0][0] for entry in data_lissajou]  # x du bateau
x_bateau_list = [entry[0][1] for entry in data_lissajou]  # y du bateau
y_cible_list = [entry[1][0] for entry in data_lissajou]   # x de la cible
x_cible_list = [entry[1][1] for entry in data_lissajou]   # y de la cible

# Initialiser le graphique
fig, ax = plt.subplots()

# Tracer le bateau (actuel en bleu) et la cible (actuelle en rouge)
boat_plot, = ax.plot([], [], 'bo', label="Bateau (Bleu)", markersize=8, zorder=5)  # Point actuel en avant-plan (zorder 5)
target_plot, = ax.plot([], [], 'ro', label="Cible (Rouge)", markersize=8, zorder=5)  # Point actuel en avant-plan (zorder 5)

# Tracer les anciennes trajectoires du bateau (en noir, avec points plus petits) et de la cible (en gris, avec pointillés)
boat_old_plot, = ax.plot([], [], 'ko', label="Trajectoire Bateau (Noir)", markersize=4, zorder=3)  # Points plus petits pour le bateau (arrière-plan)
target_old_plot, = ax.plot([], [], 'go', label="Trajectoire Cible (Gris)", markersize=4, linestyle=':', zorder=3)  # Pointillés pour la cible (arrière-plan)

# Définir les limites du graphique
ax.set_xlim(min(x_bateau_list + x_cible_list) - 1, max(x_bateau_list + x_cible_list) + 1)
ax.set_ylim(min(y_bateau_list + y_cible_list) - 1, max(y_bateau_list + y_cible_list) + 1)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Trajectoire du bateau et de la cible (live)')
ax.legend()
ax.grid(True)

# Fonction d'initialisation pour l'animation
def init():
    boat_plot.set_data([], [])
    target_plot.set_data([], [])
    boat_old_plot.set_data([], [])
    target_old_plot.set_data([], [])
    return boat_plot, target_plot, boat_old_plot, target_old_plot

# Fonction de mise à jour de l'animation (affiche point par point)
def update(frame):
    # Met à jour les anciennes positions du bateau (en noir, petits points) et de la cible (en gris, pointillés)
    boat_old_plot.set_data(x_bateau_list[:frame], y_bateau_list[:frame])
    target_old_plot.set_data(x_cible_list[:frame], y_cible_list[:frame])

    # Met à jour les positions actuelles (le dernier point) du bateau (en bleu) et de la cible (en rouge)
    boat_plot.set_data(x_bateau_list[frame:frame+1], y_bateau_list[frame:frame+1])
    target_plot.set_data(x_cible_list[frame:frame+1], y_cible_list[frame:frame+1])

    return boat_plot, target_plot, boat_old_plot, target_old_plot

# Animation : mise à jour du graphique à chaque frame
ani = FuncAnimation(fig, update, frames=len(x_bateau_list), init_func=init, interval=100, blit=True)

# Sauvegarder l'animation en GIF
ani.save("trajectoire_bateau.gif", writer="pillow", fps=10)

# Afficher le graphique en live
plt.show()
