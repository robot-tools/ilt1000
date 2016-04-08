#!/usr/bin/python3

import argparse
import ilt1000


parser = argparse.ArgumentParser(description='ilt1000 dump')
parser.add_argument(
    '--device',
    dest='device',
    action='store',
    default='/dev/ttyUSB1')
FLAGS = parser.parse_args()


LABEL_WIDTH = 25


def PrintLine(label, value, unit=''):
  print(('%s:' % label).rjust(LABEL_WIDTH), value, unit)


ilt = ilt1000.ILT1000(device=FLAGS.device)


LINES = [
  ('Model', ilt.GetModelName, ''),
  ('Generation', ilt.GetGeneration, ''),
  ('Firmware version', ilt.GetFirmwareVersion, ''),
  ('Serial number', ilt.GetSerialNumber, ''),
  ('Controller temperature', ilt.GetControllerTempF, '°F'),
  ('Ambient temperature', ilt.GetAmbientTempF, '°F'),
  ('Date/time', ilt.GetDateTime, ''),
  ('Sensor current', ilt.GetSensorCurrent, 'A'),
  ('Sensor voltage', ilt.GetSensorVoltage, 'V'),
  ('Transmission', ilt.GetTransmissionPercent, '%'),
  ('Optical density', ilt.GetOpticalDensity, '%'),
  ('100% percent setting', ilt.Get100PercentVoltage, 'V'),
]


for label, callback, unit in LINES:
  PrintLine(label, callback(), unit)
