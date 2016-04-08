#!/usr/bin/python3

import datetime
import serial


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
# getauxserialno
# getdarkmode
# getfactorydark
# getirradiance
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
# getclockfreq
# getfeedbackres
# setcalfactor
# setclockfreq
# setsamplecount


class ILT1000(object):

  # ILT1000 presents two FTDI serial devices, which become ttyUSB0 and ttyUSB1
  # if nothing else is attached. ttyUSB0 seems to be completely non-responsive.
  # We default to ttyUSB1

  def __init__(self, device='/dev/ttyUSB1', set_time=True):
    self._dev = serial.Serial(device, 115200)
    try:
      # clear junk in outgoing buffer
      self._SendCommand('echooff')
    except UnsupportedCommand:
      pass
    assert int(self._SendCommand('echooff')) == 0
    if set_time:
      self.SetDateTime()

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
