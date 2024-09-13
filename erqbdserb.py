from datetime import datetime


#print(datetime.now() > datetime.strptime("13/09/24 10:30", "%d/%m/%y %H:%M"))
#print(datetime.strptime("13/09/24 10:30", "%d/%m/%y %H:%M"))

while datetime.now() < datetime.strptime("13/09/24 10:20", "%d/%m/%y %H:%M"):
    pass

print("il est 10h20")