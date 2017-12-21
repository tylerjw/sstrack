import pynmea2
from optparse import OptionParser
from pprint import pprint
import matplotlib.pyplot as plt
import math
import utm

def haversine(point1, point2):
  """
  Calculate the great circle distance between two points
  on the earth (specified in decimal degrees)
  Returns distance in meters
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
  r = 6371 * 1000 * c

  num = math.sin(dlon)*math.cos(lat2)
  denom = math.cos(lat1)*math.sin(lat2)-math.sin(lat1)*math.cos(lat2)*math.cos(dlon)
  q = math.atan2(num, denom)
  q = math.degrees(q)
  q = (q + 360) % 360

  return (r,q)

def calculate_delta(vector, offset=1):
  return [b-a for a,b in zip(vector[:-offset], vector[offset:])] + [0]*(offset-1)

def myround(x, base=5):
    return int(base * round(float(x)/base))

def corner_num(radius):
  #approximation of http://www.ipacenotes.com/blog-21/knowledge/the-ipacenotes-steering-wheel/68
  #see: http://www.wolframalpha.com/input/?i=polynominal+fit+(14,1),+(20,2),+(29,3),+(41,4),+(65,5),+(110,6),+(216,7)
  try:
    numf = 2.2177*math.log(abs(radius)) - 4.54317
  except ValueError as e:
    print('ValueError: ', e)
    print('radius: ', radius)
    numf = 0
  (rem, num) = math.modf(numf)
  modifier = None
  if (rem < 0.25):
    modifier = '-'
  elif (rem > 0.75):
    modifier = '+'

  if (num < 1):
    num = 1
    modifier = '-'
  if (num > 6):
    num = 6
    modifier = '+'

  return (numf, num, modifier)

def to_text(note):
  nt = note['type']
  text = ''
  if (nt == 'start'):
    text = 'Start'
  elif (nt == 'end'):
    text = 'over Finish'
  elif (nt == 'straight'):
    dist = int(5 * round(float(note['distance'])/5))
    if (dist < 20):
      text = 'into'
    else:
      text = str(dist)
  elif (nt == 'corner' and note['distance'] < 10 and note['num'] > 5):
    text = 'kink ' + note['direction']
  elif (nt == 'corner'):
    text += note['direction']+str(int(note['num']))
    if note['modifier']:
      text += note['modifier']

    if (note['apex_dist'] > 0.9*note['distance']):
      text += 'late'
    elif (note['apex_dist'] > 0.8*note['distance']):
      text += '>'
    elif (note['apex_dist'] < 0.2*note['distance']):
      text += '<'

    if (note['distance'] < 20):
      text += ' short'
    elif (note['distance'] > 150):
      text += ' Xlg'
    elif (note['distance'] > 100):
      text += 'Vlg'
    elif (note['distance'] > 50):
      text += 'lg'
  return text

def upwrap_angles(angles, threshold=180):
  offset = 0
  for i in range(1, len(angles)):
    angles[i] += offset
    if (angles[i] - angles[i-1] > threshold):
      offset -= 360
      angles[i] -= 360
    elif (angles[i-1] - angles[i] > threshold):
      offset += 360
      angles[i] += 360
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
  gyro_msgs = []
  euler_msgs = []
  linear_msgs = []
  accel_msgs = []

  outfile = open(args[1], 'w')
  with open(args[0]) as inputfile:
    for line in inputfile:
      try:
        msg = pynmea2.parse(line, 'yield')
        msg_type = type(msg)
        if msg_type is pynmea2.types.talker.RMC:
          # print("RMC message: ", msg)
          outfile.write(line)
          gps_msgs.append(msg)
        elif msg_type is pynmea2.types.talker.GGA:
          # print("GGA message: ", msg)
          pass
        elif msg_type is pynmea2.types.talker:
          print("Other valid NMEA message: ", msg)
          pass
        else:
          print("Other output from pynmea2: ", msg)
      except pynmea2.ParseError:
        msg = line.strip().split(',')
        if (msg[0] == '$GYRO'):
          msg = {'datestamp': msg[1],
                 'timestamp': msg[2],
                 'x': float(msg[3]),
                 'y': float(msg[4]),
                 'z': float(msg[5]) }
          gyro_msgs.append(msg)
        elif (msg[0] == '$EULER'):
          msg = {'datestamp': msg[1],
                 'timestamp': msg[2],
                 'x': float(msg[3]),
                 'y': float(msg[4]),
                 'z': float(msg[5]) }
          euler_msgs.append(msg)
        elif (msg[0] == '$LINEAR'):
          msg = {'datestamp': msg[1],
                 'timestamp': msg[2],
                 'x': float(msg[3]),
                 'y': float(msg[4]),
                 'z': float(msg[5]) }
          linear_msgs.append(msg)
        elif (msg[0] == '$ACCEL'):
          msg = {'datestamp': msg[1],
                 'timestamp': msg[2],
                 'x': float(msg[3]),
                 'y': float(msg[4]),
                 'z': float(msg[5]) }
          accel_msgs.append(msg)
        else:
          print('unknown message: ', msg)

  outfile.close()

  gps_msgs = gps_msgs[200:]
  gyro_msgs = gyro_msgs[200:]
  # euler_msgs = euler_msgs[100:]

  # all distances are in km, convert to m
  distances = []
  bearings = []
  courses = []
  course_delta_per_meter = []
  speeds = []
  utm_points = []
  gps_a = gps_msgs[0]
  latlong_points = [(gps_a.latitude, gps_a.longitude)]
  x = utm.from_latlon(gps_a.latitude, gps_a.longitude)
  utm_points = [(x[0],x[1])]
  corner_rad = []
  gyro_z = []

  notes = [{'type':'start'}]
  for gyro,gps_b in zip(gyro_msgs[1:], gps_msgs[1:]):
    if (gps_b.spd_over_grnd == 0):
      continue

    speed_ms = gps_b.spd_over_grnd * 0.514444;

    rad_per_s = math.radians(gyro['z'])
    gyro_z.append(rad_per_s)
    radius = 1000
    if (gyro['z'] != 0):
      radius = (speed_ms * speed_ms) / rad_per_s
      if (radius > 1000 or radius < -1000):
        radius = 1000
    corner_rad.append(radius)

    latlong_points.append((gps_b.latitude, gps_b.longitude))
    y = utm.from_latlon(gps_b.latitude, gps_b.longitude)
    utm_points.append((y[0],y[1]))

    deltax = y[0]-x[0]
    deltay = y[1]-x[1]
    r = math.sqrt(math.pow(deltax,2) + math.pow(deltay,2))
    q = math.degrees(math.atan2(deltay,deltax))

    speeds.append(speed_ms)
    distances.append(r)
    bearings.append(r)
    courses.append(gps_a.true_course)
    delta = gps_b.true_course - gps_a.true_course
    if (delta == 0 or r == 0):
      course_delta_per_meter.append(0)
    else:
      course_delta_per_meter.append(delta / r)

    gps_a = gps_b
    x = y

    current_note = notes[-1]
    if (radius > 300 or radius < -300):
      #straight section
      if (current_note['type'] != 'straight'):
        newNote = {
          'type':'straight',
          'distance': r,
          'distance units': 'meeter'
        }
        notes.append(newNote)
      else:
        current_note['distance'] += r
    else:
      #corner
      (numf, num, modifier) = corner_num(radius)
      direction = 'R' if rad_per_s < 0 else 'L'

      if (current_note['type'] != 'corner' or
          current_note['direction'] != direction):
        newNote = {
          'type':'corner',
          'distance': r,
          'distance units': 'meeter',
          'direction': direction,
          'numf': numf,
          'num': num,
          'modifier': modifier,
          'apex_dist': r
        }
        notes.append(newNote)
      else:
        current_note['distance'] += r
        if (numf < current_note['numf']):
          current_note['numf'] = numf
          current_note['num'] = num
          current_note['modifier'] = modifier
          current_note['apex_dist'] = r

  notes.append({'type':'end'})

  lat_points,long_points = zip(*latlong_points)
  east_points,north_points = zip(*utm_points)
  maxlat = max(lat_points)
  minlat = min(lat_points)
  maxlong = max(long_points)
  minlong = min(long_points)
  maxeast = max(east_points)
  mineast = min(east_points)

  text = "\n".join([to_text(n) for n in notes])
  text = text.replace("\ninto\n"," into ")
  text = text.replace("into over", "over")
  print(text)

  speeds.append(gps_a.spd_over_grnd)
  courses.append(gps_a.true_course)

  courses = upwrap_angles(courses)
  course_delta = calculate_delta(courses, 1)
  distance_y = [0]
  for dist in distances:
    last = distance_y[-1]
    distance_y.append(dist+last)
  distance_y = distance_y[1:]

  plt.figure(1)
  plt.subplot(511)
  x,y = zip(*points)
  plt.plot(x,y,'-gD', markevery=[0])

  plt.subplot(512)
  plt.axhline()
  plt.plot(distance_y, gyro_z, 'r')

  plt.subplot(513)
  plt.axhline()
  plt.plot(distance_y, corner_rad, 'b')

  plt.subplot(514)
  plt.plot(distance_y,speeds[1:],'r',distance_y,distances,'k')

  plt.subplot(515)
  plt.plot(distance_y,courses[1:])
  plt.show()


if __name__ == '__main__':
    main()

