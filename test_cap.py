from DDGOATlib import get_cap
import time
import numpy as np
while True:
    cap = get_cap()*180/np.pi
    print("cap actuel: {:.2f}°".format(cap))
    time.sleep(0.5)
