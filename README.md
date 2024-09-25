# Contenu du dossier

Voici une liste des fichiers présents dans le dossier et leur description.
(À chaque mission correspond un fichier)

## DDDGOATlib.py
Bibliothèque principale contenant toutes les fonctions nécessaires pour les missions, telles que les fonctions de conversion, de récupération de données, et de contrôle du bateau.

## calibrate_mag.py
Script utilisé pour la calibration du magnétomètre et obtenir la matrice de calibration A et b (enregistrés sur le DDBOAT).

## suivi_...py
Codes réalisant les différents suivis (cap, traj, chemin...)

## plot_lissajou.py / plot_lissajou_live.py / gif_creator.py
Pour faire des jolies animations. 

## debug.py
Comme son nom l'indique, pour tester et débuger les fonctions.

Assurez-vous de consulter chaque fichier pour plus de détails sur son utilisation et ses fonctionnalités.



# Réussites

Voici les missions que nous avons réalisé avec succès :
- mission 1 : aller-retour Nord-Ouest (fichier suivi_cap.py)
- mission 2 : aller-retour vers la bouée (fichier suivi_gps.py)
- mission 3 : suivi de trajectoire : la courbe de lizarazu (fichier suivi_trajectoire.py)
- mission 4 : suivi de chemin sur 2 minutes (fichier suivi_chemin.py)



# Échecs

Il y a eu en effet quelques échecs durant cette semaine. Ceux-ci s'expliquent principalement par :

- des consignes pas toujours comprises
- les autres idiots imbéciles en 2A qui savent pas récupérer des coordonnées GPS et répandent des fake news sur le groupe
    (on aurait dû utiliser le GPS de notre DDGOAT pour toutes les mesures)
- des difficultés à travailler en groupe parce qu'on peut pas tous faire la même fonction en même temps
    et quand ça bug seul l'auteur de la fonction peut la corriger. Et devoir se partager un bateau à 3 quand on veut tester des codes différents.
- le vin au Guerléshreu (c'est faux on a rien gagné nous)
- le rab au Guerléshreu (merci Noé)
- DARTAP. On sait que c'est dur à mettre en place mais c'est sacrément pénible


Donc voici les échecs (tout relatifs) :
- mission 5 : suivi du chemin avec les 3 bouées (fichier suivi_chemin_2.py)
- mission finale : rendez-vous à la bouée (fichier rdv.py)
    En fait la fonction suivi_gps() qui marchait bien depuis le début avait été modifié et ne fonctionnait plus correctement le jour de la mission

