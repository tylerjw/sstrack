import pynmea2
from optparse import OptionParser
from pprint import pprint
from geo.sphere import _haversine_distance as distance
from geo.sphere import bearing
import matplotlib.pyplot as plt
from math import cos,sin,radians

def unwrap_angles(angles):
  adjustment = 0
  threshold = 180
  for i in range(1,len(angles)):
    angles[i] += adjustment
    if (angles[i] - angles[i-1] > threshold):
      adjustment -= 360
      angles[i] += adjustment
    elif (angles[i] - angles[i-1] < -1*threshold):
      adjustment += 360
      angles[i] += adjustment

  return angles

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
  distances = []
  bearings = []
  courses = []
  speeds = []
  points = [(0,0)]
  a = gps_msgs[0]

  for b in gps_msgs[1:]:
    if (b.spd_over_grnd < 1):
      continue

    x = (a.latitude,a.longitude)
    y = (b.latitude,b.longitude)

    r = distance(x,y)
    q = bearing(x,y)

    speeds.append(b.spd_over_grnd)
    courses.append(b.true_course)
    distances.append(r)
    bearings.append(q)
    start = points[-1]
    end = (start[0]+r*cos(radians(q)),
           start[1]-r*sin(radians(q)))
    points.append(end)
    a = b

  courses = unwrap_angles(courses)
  offset = 4
  bearing_delta = [b-a for a,b in zip(bearings[:-offset], bearings[offset:])] + [0]*(offset-1)
  course_delta = [b-a for a,b in zip(courses[:-offset], courses[offset:])] + [0]*(offset-1)
  distance_y = [0]
  for dist in distances[:-1]:
    last = distance_y[-1]
    distance_y.append(dist+last)
  distance_y = distance_y[1:]

  plt.figure(1)
  plt.subplot(411)
  x,y = zip(*points)
  plt.plot(x,y,'bo-')

  plt.subplot(412)
  plt.plot(distance_y, bearing_delta, 'x-',
           distance_y, course_delta, 'rx-')

  plt.subplot(413)
  plt.plot(distances,'k',)

  plt.subplot(414)
  plt.plot(distance_y, course_delta, 'b')
  plt.show()






if __name__ == '__main__':
    main()

