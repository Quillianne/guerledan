from DDGOATlib import suivi_gps, declenchement, suivi_trajectoire, lissajou, lissajou_point
import time

declenchement()
suivi_gps((48.1996457, -3.0152944))
time.sleep(20)
suivi_trajectoire(lissajou, lissajou_point)
time.sleep(10)
suivi_gps((48.1992385, -3.0147241))
