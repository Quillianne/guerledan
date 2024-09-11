from DDGOATlib import suivi_gps, declenchement, suivi_trajectoire, lissajou, lissajou_point
import time

declenchement()

suivi_trajectoire(lissajou, lissajou_point)
time.sleep(10)
suivi_gps((48.1992385, -3.0147241))
