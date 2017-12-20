import pynmea2
from optparse import OptionParser

def readlogfile(filename):
  messages = {
    'RMC':[],
    'GGA':[],
    'OTHER_NMEA':[],
    'INVALID_NMEA':[],
    'GYRO':[],
    'EULER':[],
    'LINEAR':[],
    'ACCEL':[],
    'OTHER':[]}

  with open(filename) as inputfile:
    for line in inputfile:
      try:
        msg = pynmea2.parse(line, 'yield')
        msg_type = type(msg)
        if msg_type is pynmea2.types.talker.RMC:
          # print("RMC message: ", msg)
          messages['RMC'].append(msg)
        elif msg_type is pynmea2.types.talker.GGA:
          # print("GGA message: ", msg)
          messages['GGA'].append(msg)
        elif msg_type is pynmea2.types.talker:
          messages['OTHER_NMEA'].append(msg)
        else:
          messages['INVALID_NMEA'].append(msg)
      except pynmea2.ParseError:
        msg = line.strip().split(',')
        if (msg[0] == '$GYRO'):
          msg = {'datestamp': msg[1],
                 'timestamp': msg[2],
                 'x': float(msg[3]),
                 'y': float(msg[4]),
                 'z': float(msg[5]) }
          messages['GYRO'].append(msg)
        elif (msg[0] == '$EULER'):
          msg = {'datestamp': msg[1],
                 'timestamp': msg[2],
                 'x': float(msg[3]),
                 'y': float(msg[4]),
                 'z': float(msg[5]) }
          messages['EULER'].append(msg)
        elif (msg[0] == '$LINEAR'):
          msg = {'datestamp': msg[1],
                 'timestamp': msg[2],
                 'x': float(msg[3]),
                 'y': float(msg[4]),
                 'z': float(msg[5]) }
          messages['LINEAR'].append(msg)
        elif (msg[0] == '$ACCEL'):
          msg = {'datestamp': msg[1],
                 'timestamp': msg[2],
                 'x': float(msg[3]),
                 'y': float(msg[4]),
                 'z': float(msg[5]) }
          messages['ACCEL'].append(msg)
        else:
          print('unknown message: ', msg)
          messages['OTHER'].append(msg)
  return messages

def main():
  usage = "usage: %prog [options] inputFile"
  parser = OptionParser(usage)

  (options, args) = parser.parse_args()
  if (len(args) != 1):
    parser.error("incorrect number of arguments")

  pprint(readlogfile(args[0]))


if __name__ == '__main__':
    main()
