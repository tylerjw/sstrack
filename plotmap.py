import pynmea2
from optparse import OptionParser
from pprint import pprint
import math
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from readlogfile import readlogfile
import numpy as np
import os
import subprocess

def haversine(point1, point2):
  """
  Calculate the great circle distance between two points
  on the earth (specified in decimal degrees)
  Returns distance in m
  """
  # convert decimal degrees to radians
  lat1, lon1 = point1
  lat2, lon2 = point2
  lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
  # haversine formula
  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
  c = 2 * math.asin(math.sqrt(a))
  # Radius of earth in kilometers is 6371
  return 6371 * c

def myround(x, base=5):
    return int(base * round(float(x)/base))

def get_odo_km(rmc_msgs, odo_start=0):
  odo = [odo_start]
  for a,b in zip(rmc_msgs[:-1], rmc_msgs[1:]):
    dist = haversine((a.latitude, a.longitude),
                     (b.latitude, b.longitude))
    odo.append(odo[-1] + dist)
  return odo

def get_odo_m(rmc_msgs, odo_start):
  odo = get_odo_km(rmc_msgs, odo_start)
  odo = [x*1000 for x in odo]
  return odo

def get_speed_knots(rmc_msgs):
  speed = [p.spd_over_grnd for p in rmc_msgs]
  return speed

def get_speed_mph(rmc_msgs):
  speed = [p.spd_over_grnd*1.15078 for p in rmc_msgs]
  return speed

def get_speed_ms(rmc_msgs):
  speed = [p.spd_over_grnd*0.5144447 for p in rmc_msgs]
  return speed

def get_distances_m(rmc_msgs):
  distances = [0]
  for a,b in zip(rmc_msgs[:-1], rmc_msgs[1:]):
    dist = haversine((a.latitude, a.longitude),
                     (b.latitude, b.longitude))
    distances.append(dist * 1000)
  return distances

def get_courses_deg(rmc_msgs):
  courses = [p.true_course for p in rmc_msgs]
  return courses

def get_courses_rad(rmc_msgs):
  courses = get_courses_deg(rmc_msgs)
  courses = [math.radians(c) for c in courses]
  return courses


def plot_map(title, rmc_msgs, odo_start=0, show_plot=True, note=None):
  times = []
  lats = []
  lons = []
  for point in rmc_msgs:
    times.append(point.datetime)
    lats.append(point.latitude)
    lons.append(point.longitude)

  odo_km = get_odo_km(rmc_msgs, odo_start)

  start_lat = lats[0]
  stop_lat = lats[-1]
  lats2 = [start_lat, stop_lat]

  start_lon = lons[0]
  stop_lon = lons[-1]
  lons2 = [start_lon, stop_lon]

  start_time = times[0]
  stop_time = times[-1]
  duration = stop_time - start_time

  delta_lon = max(lons) - min(lons)
  center_lon = max(lons) - delta_lon/2
  delta_lat = max(lats) - min(lats)
  center_lat = max(lats) - delta_lat/2
  scale = haversine((center_lat, min(lons)), (center_lat, max(lons))) * 2 / 3
  scale_units = 'km'
  if (scale < 2):
    scale = myround(scale*1000, 5)
    scale_units = 'm'
  else:
    scale = myround(scale, 2)

  padding = 0.3 * max((delta_lon,delta_lat))

  print('scale: ', scale)
  if scale == 0:
    return

  ll_lon=(min(lons)-padding)
  ll_lat=(min(lats)-padding)
  ur_lon=(max(lons)+padding)
  ur_lat=(max(lats)+padding)

  map = Basemap(projection='merc', lat_0=stop_lat, lon_0=stop_lon,
                resolution='h', area_thresh=0.1,
                llcrnrlon=ll_lon, llcrnrlat=ll_lat,
                urcrnrlon=ur_lon, urcrnrlat=ur_lat)

  map.drawcoastlines()
  map.drawcountries()
  map.drawmapboundary(fill_color='aqua')
  map.fillcontinents(color='white', lake_color='aqua')

  map.drawmeridians(np.arange(0, 360, 0.5))
  map.drawparallels(np.arange(-90, 90, 0.5))

  x,y = map(lons, lats)
  x0, y0 = map(start_lon, start_lat)
  x1, y1 = map(stop_lon, stop_lat)

  map.plot(x, y, color='r', linewidth=1, label='route')
  map.plot(x0, y0, 'bo', markersize=2)
  map.plot(x1, y1, 'k+', markersize=2)

  if note and note['type'] == 'corner':
    apex_index = note['num']['apex_index']
    apex_lon = lons[apex_index]
    apex_lat = lats[apex_index]
    x2, y2 = map(apex_lon, apex_lat)
    map.plot(x2, y2, 'g*', markersize=2)
    apex_text = 'numf: %.2f\nmpr: %.4f' % (note['num']['numf'], note['num']['mpr'])
    plt.text(x2, y2, apex_text, fontsize=3)

  start_label = 'START\n%s\n%s\n%.2fkm' % (start_lat, start_lon, odo_km[0])
  stop_label  = 'END\n%s\n%s\n%.2fkm' % (stop_lat, stop_lon, odo_km[-1])

  plt.text(x0, y0, start_label, fontsize=3)
  plt.text(x1, y1, stop_label, fontsize=3)


  map.drawmapscale(center_lon, min(lats)-(padding*0.5),
                   lons[0], lats[0], scale, barstyle='fancy', units=scale_units)

  plt.title(title)
  plt.savefig('%s.png' % title, bbox_inches='tight', dpi=500)
  if show_plot:
    plt.show()
  plt.close('all')

def main():
  usage = "usage: %prog [options] inputFile"
  parser = OptionParser(usage)

  (options, args) = parser.parse_args()
  if (len(args) != 1):
    parser.error("incorrect number of arguments")

  messages = readlogfile(args[0])

  plot_map(args[0].split('.')[0], messages['RMC'], show_plot=False)


if __name__ == '__main__':
    main()

