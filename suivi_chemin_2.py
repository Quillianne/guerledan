from DDGOATlib import declenchement, suivi_gps, suivi_chemin_bouee
import time


declenchement()
suivi_chemin_bouee()
time.sleep(10)
#suivi_gps((48.1992385, -3.0147241))
suivi_chemin_bouee(point_1=(48.1996457, -3.0152944), point_2=(48.1996872, -3.0153766))

