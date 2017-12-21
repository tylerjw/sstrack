from readlogfile import readlogfile
from plotmap import get_speed_ms, get_courses_deg, get_odo_km, get_speed_mph
from plotmap import plot_map

from optparse import OptionParser
import math
import matplotlib.pyplot as plt
from pprint import pprint
import os

mpr_cutoff = 1000

def corner_num(mpr):
  #approximation of http://www.ipacenotes.com/blog-21/knowledge/the-ipacenotes-steering-wheel/68
  #see: http://www.wolframalpha.com/input/?i=polynominal+fit+(14,1),+(20,2),+(29,3),+(41,4),+(65,5),+(110,6),+(216,7)
  try:
    numf = 2.2177*math.log(abs(mpr)) - 4.54317
  except ValueError as e:
    print('ValueError: ', e)
    print('mpr: ', mpr)
    numf = 0
  (rem, numi) = math.modf(numf)
  modifier = None
  if (rem < 0.25):
    modifier = '-'
  elif (rem > 0.75):
    modifier = '+'

  if (numi < 1):
    numi = 1
    modifier = '-'
  if (numi > 6):
    numi = 6
    modifier = '+'

  return (numf, numi, modifier)

def calc_num(note):
  data = {'numf': 1000, 'numi':7, 'modifier':'', 'apex_index': 0, 'mpr': mpr_cutoff}
  for i in range(len(note['corner_mpr'])):
    (numf, numi, modifier) = corner_num(note['corner_mpr'][i])
    if (numf < data['numf']):
      data = {
        'numf': numf,
        'numi': int(numi),
        'modifier': modifier,
        'apex_index': i,
        'mpr': note['corner_mpr'][i]
      }
  return data


def calc_text(note):
  nt = note['type']
  distance = (note['odo end'] - note['odo start']) * 1000
  num_samples = len(note['corner_mpr'])
  text = ''

  if (nt == 'start'):
    text = 'Start'
  elif (nt == 'end'):
    text = 'over Finish'
  elif (nt == 'straight'):
    dist = int(5 * round(float(distance)/5))
    if (dist < 20):
      text = 'into'
    else:
      text = str(dist)
  elif (nt == 'corner' and distance < 10 and note['num']['numi'] > 5):
    text = 'kink ' + note['direction']
  elif (nt == 'corner'):
    text += note['direction']+str(note['num']['numi'])
    if note['num']['modifier']:
      text += note['num']['modifier']

    if (note['num']['apex_index'] > 0.9*num_samples):
      text += 'late'
    elif (note['num']['apex_index'] > 0.8*num_samples):
      text += '>'
    elif (note['num']['apex_index'] < 0.2*num_samples):
      text += '<'

    if (distance < 20):
      text += ' short'
    elif (distance > 150):
      text += ' Xlg'
    elif (distance > 100):
      text += 'Vlg'
    elif (distance > 50):
      text += 'lg'
  return text

def make_notes(messages):
  speeds_ms = get_speed_ms(messages['RMC'])
  speeds_mph = get_speed_mph(messages['RMC'])
  courses_deg = get_courses_deg(messages['RMC'])
  odo_km = get_odo_km(messages['RMC'])
  angular_vel = [math.radians(m['z']) for m in messages['GYRO']]

  # meeters per radian
  # speed (m/s) / yaw_rate (rad/s) = (m/s)*(s/rad) = m/rad
  corner_mpr = [
        ((s / v) if (v != 0 and s != 0) else mpr_cutoff)
        for s,v in zip(speeds_ms,angular_vel)
  ]

  corner_mpr = [p if (p < mpr_cutoff and p > -mpr_cutoff) else mpr_cutoff for p in corner_mpr]

  #plot corner radius data
  # plt.figure(1)
  # plt.plot(odo_km, corner_mpr, 'b')
  # plt.show()

  notes = [{'type':'start', 'text': 'Start', 'corner_mpr':[], 'odo start': 0, 'odo end': 0}]
  num_samples = len(messages['RMC'])
  for i in range(num_samples):
    current_note = notes[-1]
    no_change = True
    if (corner_mpr[i] > mpr_cutoff or corner_mpr[i] < -mpr_cutoff):
      #straight section
      if (current_note['type'] != 'straight'):
        newNote = {
          'type':'straight',
          'odo start': odo_km[i],
          'odo end': odo_km[i],
          'odo units': 'km',
          'index start': i,
          'index end': i,
          'corner_mpr': [corner_mpr[i]],
          'RMC': [messages['RMC'][i]],
          'GYRO': [messages['GYRO'][i]],
          'EULER': [messages['EULER'][i]],
        }
        notes.append(newNote)
        no_change = False
    else:
      #corner
      direction = 'R' if corner_mpr[i] < 0 else 'L'

      if (current_note['type'] != 'corner' or
          current_note['direction'] != direction):
        newNote = {
          'type':'corner',
          'odo start': odo_km[i],
          'odo end': odo_km[i],
          'odo units': 'km',
          'index start': i,
          'index end': i,
          'corner_mpr': [corner_mpr[i]],
          'RMC': [messages['RMC'][i]],
          'GYRO': [messages['GYRO'][i]],
          'EULER': [messages['EULER'][i]],
          'direction': direction
        }
        notes.append(newNote)
        no_change = False

    if no_change:
      current_note['odo end'] = odo_km[i]
      current_note['index end'] = i
      current_note['corner_mpr'].append(corner_mpr[i])
      current_note['RMC'].append(messages['RMC'][i])
      current_note['GYRO'].append(messages['GYRO'][i])
      current_note['EULER'].append(messages['EULER'][i])

  notes.append({'type':'end', 'text': 'over Finish', 'corner_mpr':[], 'odo start': 0, 'odo end': 0})

  for note in notes[1:-1]:
    note['num'] = calc_num(note)
    note['text'] = calc_text(note)

  return notes


def plot_notes(title, notes, show_plot=True):
  if not os.path.exists(title):
    os.makedirs(title)
  os.chdir(title)

  for i,note in enumerate(notes[1:-1]):
    title = "%03d_%s" % (i, note['text'])
    print(title)
    distance = note['odo end'] - note['odo start']
    if distance == 0:
      print((note['odo start'], note['odo end'], distance))
      continue

    plot_map(title, note['RMC'], note['odo start'], show_plot, note)


def main():
  usage = "usage: %prog [options] inputFile"
  parser = OptionParser(usage)

  (options, args) = parser.parse_args()
  if (len(args) != 1):
    parser.error("incorrect number of arguments")

  title = args[0].split('.')[0]
  messages = readlogfile(args[0])
  notes = make_notes(messages)
  plot_notes(title, notes, False)

if __name__ == '__main__':
    main()
