#!/usr/bin/python3

import datetime
import serial
import time


class Error(Exception):
  pass


class UnsupportedCommand(Error):
  pass


class RequiredValueNotSet(Error):
  pass


class OutOfRange(Error):
  pass


class Saturated(Error):
  pass


# TODO commands:
# eraselogdata
# getfactorydark
# getlogdata
# getuserdark
# set100perc
# setautaveraging
# setcurrentloop
# sethiaveraging
# setlowaveraging
# setmedaveraging
# setsimpleirrcal
# setuserdark
# startlogdata
# stoplogdata
# usecalfactor
# usefactorydark
# usefeedbackres
# usenodark
# useuserdark
# erasecalfactor
# getcalfactor
# getfeedbackres
# setcalfactor
# setsamplecount


class ILT1000(object):

  DARK_NONE = 0
  DARK_FACTORY = 1
  DARK_USER = 2

  DARK_NAMES = {
    0: 'None',
    1: 'Factory',
    2: 'User',
  }

  # ILT1000 presents two FTDI serial devices, which become ttyUSB0 and ttyUSB1
  # if nothing else is attached. ttyUSB0 seems to be completely non-responsive.
  # We default to ttyUSB1

  def __init__(self, device='/dev/ttyUSB1', set_time=True):
    self._dev = serial.Serial(device, baudrate=115200)
    self._Clear()
    assert int(self._SendCommand('echooff')) == 0
    if set_time:
      self.SetDateTime()

  def _Clear(self):
    self._dev.timeout = 0.1
    self._dev.write(b'\r\n')
    self._dev.read(128)
    self._dev.timeout = None

  def _SendCommand(self, command):
    self._dev.write(command.encode('ascii') + b'\r\n')
    ret = self._dev.readline().rstrip().decode('ascii')
    if ret == '-999':
      raise UnsupportedCommand(command)
    if ret == '-500':
      raise RequiredValueNotSet(command)
    if ret == '-501':
      raise OutOfRange(command)
    if ret == '-502':
      raise Saturated(command)
    return ret

  def GetModelName(self):
    return self._SendCommand('getmodelname')

  def GetGeneration(self):
    return int(self._SendCommand('getgeneration'))

  def GetFirmwareVersion(self):
    return self._SendCommand('getfwversion')

  def GetSerialNumber(self):
    return self._SendCommand('getserialnumber')

  def GetAuxSerialNumber(self):
    return self._SendCommand('getauxserialno')

  def SetAuxSerialNumber(self, serial):
    # SPEC ERROR
    # This is undocumented.
    assert int(self._SendCommand('setauxserialno %s' % serial)) == 0

  def GetControllerTempF(self):
    return int(self._SendCommand('gettemp'))

  def GetAmbientTempF(self):
    # SPEC ERROR
    # Protocol doc indicates that this is degrees F * 100, but actual values
    # look like just degrees F
    return int(self._SendCommand('getambienttemp'))

  def GetDateTime(self):
    ret = self._SendCommand('getdatetime')
    return datetime.datetime.fromtimestamp(int(ret.split()[2]))

  def SetDateTime(self, now=None):
    now = now or datetime.datetime.utcnow()
    timestr = now.strftime('%m/%d/%Y %H:%M:%S')
    ret = self._SendCommand('setdatetime ' + timestr)
    assert int(ret) == 0

  def GetSensorCurrent(self):
    # SPEC ERROR
    # Protocol doc indicates that this is in pA, but actual values are in
    # scientific notation and appear to be A. They are also suspiciously
    # similar to getvoltage return values.
    ret = self._SendCommand('getcurrent')
    return float(ret)

  def GetSensorVoltage(self):
    ret = self._SendCommand('getvoltage')
    return float(ret) / 1000000

  def GetTransmissionPercent(self):
    ret = self._SendCommand('gettrans')
    return float(ret) / 10

  def GetOpticalDensity(self):
    ret = self._SendCommand('getod')
    return float(ret) / 100

  def Get100PercentVoltage(self):
    # SPEC ERROR
    # Spec says microvolts, but actual values appear to be in volts.
    ret = self._SendCommand('get100perc')
    return float(ret)

  def GetDarkMode(self):
    return int(self._SendCommand('getdarkmode'))

  def GetIrradiance(self):
    ret = self._SendCommand('getirradiance')
    return float(ret) / 1000

  def GetClockFrequencyHz(self):
    ret = self._SendCommand('getclockfreq')
    return float(ret) / 100

  def SetClockFrequency(self):
    # SPEC ERROR
    # Command returns -999 on my ILT1000-V02. Implementation below is untested
    # and likely wrong.
    assert int(self._SendCommand('setclockfreq')) == 0
    self._dev.write(b'A')
    time.sleep(60.0)
    self._dev.write(b'B')
