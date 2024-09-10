import numpy as np

point_gps = [4811.9511, "N", 300.8679, "W"]

def convert_to_decimal_degrees(ddmmss, direction):
    # Séparer les degrés et les minutes avec des opérations mathématiques
    degrees = int(ddmmss // 100)  # Diviser par 100 pour obtenir les degrés
    minutes = ddmmss % 100  # Le reste correspond aux minutes

    # Conversion des minutes en degrés
    decimal_degrees = degrees + minutes / 60

    # # Si la direction est Sud ou Ouest, on rend la valeur négative
    # if direction in ['S', 'W']:
    #     decimal_degrees = -decimal_degrees

    return decimal_degrees


def get_gps():
    gll_ok, gll_data = True, point_gps
    if gll_ok:
        # Conversion des données GPS en degrés décimaux
        latitude = convert_to_decimal_degrees(gll_data[0], gll_data[1])
        longitude = convert_to_decimal_degrees(gll_data[2], gll_data[3])
        return latitude, longitude

def deg_to_rad(deg):
    """Convertit les degrés en radians."""
    return deg * np.pi / 180

def conversion_spherique_cartesien(point, lat_m=48.1991667, long_m=3.0144444, rho=6371000):
    """
    Convertit les coordonnées GPS (latitude, longitude) en coordonnées cartésiennes locales
    par rapport à un point M défini par lat_m et long_m, en ne retournant que x et y.
    """
    # Convertir les latitudes et longitudes en radians
    lat_m_rad = deg_to_rad(lat_m)
    long_m_rad = deg_to_rad(long_m)
    lat_rad = deg_to_rad(point[0])
    long_rad = deg_to_rad(point[1])

    # Conversion des coordonnées du point M (centre) en cartésiennes 2D (x_m, y_m)
    x_m = rho * np.cos(lat_m_rad) * np.cos(long_m_rad)
    y_m = rho * np.cos(lat_m_rad) * np.sin(long_m_rad)

    # Conversion des coordonnées du point P en cartésiennes 2D (x_p, y_p)
    x_p = rho * np.cos(lat_rad) * np.cos(long_rad)
    y_p = rho * np.cos(lat_rad) * np.sin(long_rad)

    # Calcul des coordonnées relatives par rapport au point M
    x = x_p - x_m
    y = y_p - y_m

    return x, y

print(get_gps())
print(conversion_spherique_cartesien((48.1991667, 3.0144444)))
print(conversion_spherique_cartesien(get_gps()))