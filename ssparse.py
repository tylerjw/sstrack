import pynmea2
from optparse import OptionParser
from pprint import pprint
from geo.sphere import _haversine_distance as distance
from geo.sphere import bearing
import matplotlib.pyplot as plt
from math import cos,sin,radians


def main():
  usage = "usage: %prog [options] logFile outputFile"
  parser = OptionParser(usage)
  parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
  parser.add_option("-q", "--quiet", action="store_false", dest="verbose")

  (options, args) = parser.parse_args()
  if (len(args) != 2):
    parser.error("incorrect number of arguments")
  if (options.verbose):
    print("reading %s..." % args[0])

  gps_msgs = []

  with open(args[0]) as nmea:
    streamreader = pynmea2.NMEAStreamReader(errors='yield')

    for msg in streamreader.next(nmea.read()):
      msg_type = type(msg)
      if msg_type is pynmea2.types.talker.RMC:
        # print("RMC message: ", msg)
        gps_msgs.append(msg)
      elif msg_type is pynmea2.types.talker.GGA:
        # print("GGA message: ", msg)
        pass
      elif msg_type is pynmea2.types.talker:
        # print("Other valid NMEA message")
        pass
      else:
        print("Invalid NMEA string: ", msg)

  # all distances are in km, convert to m
  distance_bearing = []
  speeds = [gps_msgs[0].spd_over_grnd]
  points = [(0,0)]
  a = gps_msgs[0]
  for b in gps_msgs[1:]:
    x = (a.latitude, a.longitude)
    y = (b.latitude, b.longitude)
    p = (distance(x,y),bearing(x,y))

    if (b.spd_over_grnd < 2 or p[0] < 1):
      continue

    speeds.append(b.spd_over_grnd)
    distance_bearing.append(p)
    start = points[-1]
    end = (start[0]+p[0]*cos(radians(p[1])), start[1]-p[0]*sin(radians(p[1])))
    points.append(end)
    a = b

  distances,bearings = zip(*distance_bearing)
  bearing_delta = [b-a for a,b in zip(bearings[:-1], bearings[1:])]
  distance_y = [0]
  for dist in distances[:-1]:
    last = distance_y[-1]
    distance_y.append(dist+last)
  distance_y = distance_y[1:]

  plt.figure(1)
  plt.subplot(311)
  x,y = zip(*points)
  plt.plot(x,y,'bo-')

  plt.subplot(312)
  plt.plot(distance_y, bearing_delta, 'x-')

  plt.subplot(313)
  plt.plot(speeds,'r',distances,'k')
  plt.show()






if __name__ == '__main__':
    main()

