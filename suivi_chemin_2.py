from DDGOATlib import declenchement, suivi_gps, suivi_chemin_bouee
import time


declenchement()
suivi_chemin_bouee()
time.sleep(10)
suivi_gps((48.1992385, -3.0147241))

