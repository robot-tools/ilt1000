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


class ILT1000(object):

  def __init__(self, device, set_time=True):
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

  def GetCurrentPicoAmps(self):
    ret = self._SendCommand('getcurrent')
    return float(ret)

  def GetVoltage(self):
    ret = self._SendCommand('getvoltage')
    return float(ret) / 1000000

  def GetTransmissionPercent(self):
    ret = self._SendCommand('gettrans')
    return float(ret) / 10

  def GetOpticalDensity(self):
    ret = self._SendCommand('getod')
    return float(ret) / 100
