from DDGOATlib import declenchement, suivi_gps
from datetime import datetime


# attente de la bonne heure (11h26)
while datetime.now() < datetime.strptime("13/09/24 11:26", "%d/%m/%y %H:%M"):
    pass
suivi_gps((48.1996457, -3.0152944), distance_seuil= 40)

# attente de la bonne heure (11h28)
while datetime.now() < datetime.strptime("13/09/24 10:28", "%d/%m/%y %H:%M"):
    pass
suivi_gps((48.1996457, -3.0152944), distance_seuil= 5)

