import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Charger les données sauvegardées
data_lissajou = np.load("data_lissajou_goated.npy", allow_pickle=True)

# Extraire les coordonnées du bateau, de la cible, et les caps
x_bateau_list = [entry[0][0] for entry in data_lissajou]  # x du bateau
y_bateau_list = [entry[0][1] for entry in data_lissajou]  # y du bateau
x_cible_list = [entry[1][0] for entry in data_lissajou]   # x de la cible
y_cible_list = [entry[1][1] for entry in data_lissajou]   # y de la cible
cap_actuel_list = [entry[2] for entry in data_lissajou]   # cap actuel
cap_a_suivre_list = [entry[3] for entry in data_lissajou] # cap à suivre

# Initialiser le graphique
fig, ax = plt.subplots()

# Tracer le bateau (actuel en bleu) et la cible (actuelle en rouge)
boat_plot, = ax.plot([], [], 'bo', label="Bateau (Bleu)", markersize=8, zorder=5)  # Point actuel en avant-plan (zorder 5)
target_plot, = ax.plot([], [], 'ro', label="Cible (Rouge)", markersize=8, zorder=5)  # Point actuel en avant-plan (zorder 5)

# Tracer les anciennes trajectoires du bateau (en noir, avec points plus petits) et de la cible (en gris, avec pointillés)
boat_old_plot, = ax.plot([], [], 'ko', label="Ancienne Trajectoire Bateau (Noir)", markersize=4, zorder=3)  # Points plus petits pour le bateau (arrière-plan)
target_old_plot, = ax.plot([], [], 'go', label="Ancienne Trajectoire Cible (Gris)", markersize=4, linestyle=':', zorder=3)  # Pointillés pour la cible (arrière-plan)

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

# Fonction pour ajouter une flèche représentant un cap
def plot_arrow(ax, x, y, angle, color, label=None):
    """Ajoute une flèche partant de (x, y) avec un angle donné (en degrés)."""
    # Calcul des composantes de la direction de la flèche
    dx = np.cos(np.radians(angle))
    dy = np.sin(np.radians(angle))
    # Dessiner la flèche
    ax.arrow(x, y, dx, dy, head_width=0.1, head_length=0.2, fc=color, ec=color, label=label, zorder=4)

# Fonction de mise à jour de l'animation (affiche point par point)
def update(frame):
    # Effacer les anciennes flèches
    ax.patches = []

    # Met à jour les anciennes positions du bateau (en noir, petits points) et de la cible (en gris, pointillés)
    boat_old_plot.set_data(x_bateau_list[:frame], y_bateau_list[:frame])
    target_old_plot.set_data(x_cible_list[:frame], y_cible_list[:frame])

    # Met à jour les positions actuelles (le dernier point) du bateau (en bleu) et de la cible (en rouge)
    boat_plot.set_data(x_bateau_list[frame:frame+1], y_bateau_list[frame:frame+1])
    target_plot.set_data(x_cible_list[frame:frame+1], y_cible_list[frame:frame+1])

    # Tracer les flèches pour le cap actuel (rouge) et le cap à suivre (gris)
    plot_arrow(ax, x_bateau_list[frame], y_bateau_list[frame], cap_actuel_list[frame], color='red', label="Cap Actuel")
    plot_arrow(ax, x_bateau_list[frame], y_bateau_list[frame], cap_a_suivre_list[frame], color='gray', label="Cap à Suivre")

    return boat_plot, target_plot, boat_old_plot, target_old_plot

# Animation : mise à jour du graphique à chaque frame
ani = FuncAnimation(fig, update, frames=len(x_bateau_list), init_func=init, interval=100, blit=True)

# Sauvegarder l'animation en GIF
ani.save("trajectoire_bateau_cap.gif", writer="pillow", fps=10)

# Afficher le graphique en live
plt.show()
