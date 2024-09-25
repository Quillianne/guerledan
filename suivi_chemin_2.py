from DDGOATlib import declenchement, suivi_gps, suivi_chemin_bouee
import time


declenchement()

#de M vers bouée A
suivi_chemin_bouee()
time.sleep(10)

#de A vers bouée B
suivi_chemin_bouee(point_1=(48.1996457, -3.0152944),point_2=(48.2008333, -3.0163889))
time.sleep(10)

#de B vers bouée A
suivi_chemin_bouee(point_1=(48.2008333, -3.0163889), point_2=(48.1996457, -3.0152944))
time.sleep(10)

#retour à M avec suivi_gps (plus précis que suivi_chemin_bouee)
suivi_gps((48.1992385, -3.0147241))
#suivi_chemin_bouee(point_1=(48.1996457, -3.0152944), point_2=(48.1996872, -3.0153766))

