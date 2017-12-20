from optparse import OptionParser
from pprint import pprint
import math
import utm
import pyx
from readlogfile import readlogfile

def graph_linear(msgs):
  # timestamps = [float(m['timestamp']) for m in msgs]
  x = [m['x'] for m in msgs]
  y = [m['y'] for m in msgs]
  z = [m['z'] for m in msgs]
  x_axis = range(len(x))
  g = pyx.graph.graphxy(width=8,
                  key=pyx.graph.key.key(pos="br", dist=0.1))
  g.plot([pyx.graph.data.values(title="linear acceleration x m/s**2", x=x_axis, y=x),
         pyx.graph.data.values(title="linear acceleration y m/s**2", x=x_axis, y=y)],
          [pyx.graph.style.line([pyx.style.linestyle.solid,
                                pyx.color.gradient.Rainbow])])
  g.writePDFfile("linearAccel")

def graph_gyro(msgs):
  # timestamps = [float(m['timestamp']) for m in msgs]
  x = [m['x'] for m in msgs]
  y = [m['y'] for m in msgs]
  z = [m['z'] for m in msgs]
  x_axis = range(len(x))
  g = pyx.graph.graphxy(width=8,
                  key=pyx.graph.key.key(pos="br", dist=0.1))
  g.plot([pyx.graph.data.values(title="gyro x deg/sec", x=x_axis, y=x),
         pyx.graph.data.values(title="gyro y deg/sec", x=x_axis, y=y),
         pyx.graph.data.values(title="gyro z deg/sec", x=x_axis, y=z)],
          [pyx.graph.style.line([pyx.style.linestyle.solid,
                                pyx.color.gradient.Rainbow])])
  g.writePDFfile("gyro")

def graph_accel(msgs):
  # timestamps = [float(m['timestamp']) for m in msgs]
  x = [m['x'] for m in msgs]
  y = [m['y'] for m in msgs]
  z = [m['z'] for m in msgs]
  x_axis = range(len(x))
  g = pyx.graph.graphxy(width=8,
                  key=pyx.graph.key.key(pos="br", dist=0.1))
  g.plot([pyx.graph.data.values(title="accelerometer x m/s**2", x=x_axis, y=x),
         pyx.graph.data.values(title="accelerometer y m/s**2", x=x_axis, y=y)],
          [pyx.graph.style.line([pyx.style.linestyle.solid,
                                pyx.color.gradient.Rainbow])])
  g.writePDFfile("accelerometer")

def graph_euler(msgs):
  # timestamps = [float(m['timestamp']) for m in msgs]
  x = [m['x'] for m in msgs]
  y = [m['y'] for m in msgs]
  z = [m['z'] for m in msgs]
  x_axis = range(len(x))
  g = pyx.graph.graphxy(width=8,
                  key=pyx.graph.key.key(pos="br", dist=0.1))
  g.plot([pyx.graph.data.values(title="euler x deg", x=x_axis, y=x),
         pyx.graph.data.values(title="euler y deg", x=x_axis, y=y),
         pyx.graph.data.values(title="euler z deg", x=x_axis, y=z)],
          [pyx.graph.style.line([pyx.style.linestyle.solid,
                                pyx.color.gradient.Rainbow])])
  g.writePDFfile("euler")

def main():
  usage = "usage: %prog [options] inputFile"
  parser = OptionParser(usage)

  (options, args) = parser.parse_args()
  if (len(args) != 1):
    parser.error("incorrect number of arguments")

  messages = readlogfile(args[0])

  graph_linear(messages['LINEAR'])
  graph_gyro(messages['GYRO'])
  graph_accel(messages['ACCEL'])
  graph_euler(messages['EULER'])


if __name__ == '__main__':
    main()

