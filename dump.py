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


LABEL_WIDTH = 30


def PrintLine(label, value, unit=''):
  print(('%s:' % label).rjust(LABEL_WIDTH), value, unit)


ilt = ilt1000.ILT1000(device=FLAGS.device)


ilt.SetAveraging(ilt.AVERAGING_AUTO)


LINES = [
  ('Model', ilt.GetModelName, ''),
  ('Generation', ilt.GetGeneration, ''),
  ('Firmware version', ilt.GetFirmwareVersion, ''),
  ('API version', ilt.GetAPIVersion, ''),
  ('Serial number', ilt.GetSerialNumber, ''),
  ('Aux serial number', ilt.GetAuxSerialNumber, ''),
  ('Friendly name', ilt.GetFriendlyName, ''),
  ('Controller temperature', ilt.GetControllerTempF, '°F'),
  ('Ambient temperature', ilt.GetAmbientTempF, '°F'),
  ('Date/time', ilt.GetDateTime, ''),
  ('Sensor current', ilt.GetSensorCurrent, 'A'),
  ('Sensor voltage', ilt.GetSensorVoltage, 'V'),
  ('Transmission', ilt.GetTransmissionPercent, '%'),
  ('Optical density', ilt.GetOpticalDensity, '%'),
  ('100% percent setting', ilt.Get100PercentCurrent, 'A'),
  ('Dark mode', lambda: ilt.DARK_NAMES[ilt.GetDarkMode()], ''),
  ('Irradiance', ilt.GetIrradiance, ''),
  ('Irradiance threshold (low)', ilt.GetIrradianceThresholdLow, ''),
  ('Clock frequency', ilt.GetClockFrequencyHz, '㎐'),
  ('Feedback resistance', ilt.GetFeedbackResistanceOhm, 'Ω'),
  ('Feedback resistor', lambda: ilt.FEEDBACK_RES_NAMES[ilt.GetFeedbackResistor()], ''),
  ('Feedback resistor setting', lambda: ilt.FEEDBACK_RES_NAMES[ilt.GetFeedbackResistorSetting()], ''),
  ('Factory dark', ilt.GetFactoryDarkVoltages, 'V'),
  ('User dark', ilt.GetUserDarkVoltages, 'V'),
  ('Ambient', ilt.GetAmbientCurrent, 'A'),
  ('Sample time', ilt.GetSampleSeconds, 's'),
  ('Detector bias', ilt.GetBiasVoltage, 'V'),
]


for label, callback, unit in LINES:
  try:
    PrintLine(label, callback(), unit)
  except ilt1000.Error as e:
    PrintLine(label, repr(e), '')
