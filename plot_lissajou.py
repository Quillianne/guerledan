import numpy as np
import matplotlib.pyplot as plt

# Charger les données sauvegardées
data_lissajou = np.load("data_lissajou_goated.npy", allow_pickle=True)

# Extraire les coordonnées du bateau et de la cible
x_bateau_list = [entry[0][0] for entry in data_lissajou]  # x du bateau
y_bateau_list = [entry[0][1] for entry in data_lissajou]  # y du bateau
x_cible_list = [entry[1][0] for entry in data_lissajou]   # x de la cible
y_cible_list = [entry[1][1] for entry in data_lissajou]   # y de la cible

# Tracer les coordonnées du bateau en bleu
plt.plot(y_bateau_list, x_bateau_list, 'bo-', label="Bateau (Bleu)")

# Tracer les coordonnées de la cible en rouge
plt.plot(y_cible_list, x_cible_list, 'ro-', label="Cible (Rouge)")

# Ajouter les labels et une légende
plt.xlabel('Y')
plt.ylabel('X')
plt.title('Trajectoire du bateau et de la cible')
plt.legend()

# Afficher le graphique
plt.grid(True)
plt.show()