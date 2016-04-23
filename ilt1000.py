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


class CommandError(Error):
  pass


# TODO commands:
# captureflash (SPEC ERROR: doc description missing)
# getflash

# setcurrentloop

# usecalfactor
# erasecalfactor
# getcalfactor
# setcalfactor
# usecalfactortemp

# getecal
# getecaldate
# setecal

# setfeedbackres

# gettriggerin
# settriggerout

# getvagc3
# getvped
# getvped
# getvx1
# getvx17
# set0vbias
# set5vbias

# setwireless

# configbackup
# configrestore

# setmodelname

# setwflisten


class ILT1000(object):

  DARK_NONE = 0
  DARK_FACTORY = 1
  DARK_USER = 2

  DARK_NAMES = {
    0: 'None',
    1: 'Factory',
    2: 'User',
  }

  FEEDBACK_RES_AUTO = 0
  FEEDBACK_RES_LOW = 1
  FEEDBACK_RES_MEDIUM = 2
  FEEDBACK_RES_HIGH = 3

  FEEDBACK_RES_NAMES = {
    0: 'Auto',
    1: 'Low',
    2: 'Medium',
    3: 'High',
  }

  AVERAGING_AUTO = 0
  AVERAGING_LOW = 1  # 5 ㎐
  AVERAGING_MEDIUM = 2  # 2 ㎐
  AVERAGING_HIGH = 3  # 0.5 ㎐

  LOG_OPTICAL_DENSITY = 1 << 0
  LOG_TRANSMISSION_PERCENT = 1 << 1
  LOG_SENSOR_CURRENT = 1 << 2
  LOG_SENSOR_VOLTAGE = 1 << 3
  LOG_CONTROLLER_TEMP = 1 << 4
  LOG_IRRADIANCE = 1 << 5
  LOG_REALTIME = 1 << 7

  # ILT1000 presents two FTDI serial devices, which become ttyUSB0 and ttyUSB1
  # if nothing else is attached. ttyUSB0 seems to be completely non-responsive.
  # We default to ttyUSB1

  def __init__(self, device='/dev/ttyUSB1', set_time=True):
    self._dev = serial.Serial(device, baudrate=115200)
    self._Clear()
    self._SendCommandOrDie('echooff')
    if set_time:
      self.SetDateTime()

  def _Clear(self):
    self._dev.timeout = 0.1
    self._dev.write(b'\r')
    self._dev.read(2 ** 16)
    self._dev.timeout = None

  def _GetLine(self):
    return self._dev.readline().rstrip().decode('ascii')

  def _SendCommand(self, command):
    encoded = command.encode('ascii') + b'\r'
    self._dev.write(encoded[:1])
    time.sleep(0.05)
    self._dev.write(encoded[1:])
    ret = self._GetLine()
    if ret == '-999':
      raise UnsupportedCommand(command)
    if ret == '-500':
      raise RequiredValueNotSet(command)
    if ret == '-501':
      raise OutOfRange(command)
    if ret == '-502':
      raise Saturated(command)
    return ret

  def _SendCommandOrDie(self, command):
    ret = self._SendCommand(command)
    if int(ret) != 0:
      raise CommandError

  def GetModelName(self):
    return self._SendCommand('getmodelname')

  def GetGeneration(self):
    return int(self._SendCommand('getgeneration'))

  def GetFirmwareVersion(self):
    return self._SendCommand('getfwversion')

  def GetAPIVersion(self):
    return int(self._SendCommand('getapiversion'))

  def GetSerialNumber(self):
    return self._SendCommand('getserialnumber')

  def GetAuxSerialNumber(self):
    return self._SendCommand('getauxserialno')

  def SetAuxSerialNumber(self, serial):
    self._SendCommandOrDie('setauxserialno %s' % serial)

  def GetControllerTempF(self):
    return int(self._SendCommand('gettemp'))

  def GetAmbientTempF(self):
    return int(self._SendCommand('getambienttemp'))

  def GetDateTime(self):
    ret = self._SendCommand('getdatetime')
    return datetime.datetime.fromtimestamp(int(ret.split()[2]))

  def SetDateTime(self, now=None):
    now = now or datetime.datetime.utcnow()
    timestr = now.strftime('%m/%d/%Y %H:%M:%S')
    self._SendCommandOrDie('setdatetime ' + timestr)

  def GetSensorCurrent(self):
    return float(self._SendCommand('getcurrent'))

  def GetSensorVoltage(self):
    return float(self._SendCommand('getvoltage'))

  def GetVoltageStage(self):
    return int(self._SendCommand('getvoltagestage'))

  def GetTransmissionPercent(self):
    return float(self._SendCommand('gettrans'))

  def Get100PercentCurrent(self):
    return float(self._SendCommand('get100perc'))

  def Set100PercentCurrent(self):
    return float(self._SendCommand('set100perc'))

  def GetOpticalDensity(self):
    return float(self._SendCommand('getod'))

  def GetIrradiance(self):
    return float(self._SendCommand('getirradiance'))

  def SetIrradianceThresholdLow(self, value):
    self._SendCommandOrDie('setirrthresholdlow %.2e' % value)

  def GetIrradianceThresholdLow(self):
    return float(self._SendCommand('getirrthresholdlow'))

  def GetDarkMode(self):
    return int(self._SendCommand('getdarkmode'))

  _DARK_MODE_COMMANDS = {
    DARK_NONE: 'usenodark',
    DARK_FACTORY: 'usefactorydark',
    DARK_USER: 'useuserdark',
  }

  def SetDarkMode(self, mode=DARK_FACTORY):
    self._SendCommandOrDie(self._DARK_MODE_COMMANDS[mode])

  def _DarkCommand(self, command):
    ret = self._SendCommand(command)
    values = ret.split(' ')
    return [
        [float(values[4 * r + i + 1]) / 1000000 for i in range(3)]
        for r in range(3)]

  def SetFactoryDarkVoltages(self):
    return self._DarkCommand('setfactorydark')

  def GetFactoryDarkVoltages(self):
    return self._DarkCommand('getfactorydark')

  def SetUserDarkVoltages(self):
    return self._DarkCommand('setuserdark')

  def GetUserDarkVoltages(self):
    return self._DarkCommand('getuserdark')

  def GetClockFrequencyHz(self):
    ret = self._SendCommand('getclockfreq')
    return float(ret) / 100

  def GetFeedbackResistanceOhm(self):
    ret = self._SendCommand('getfeedbackres')
    return float(ret) * 100

  def GetFeedbackResistor(self):
    return int(self._SendCommand('getfeedbackresnumber'))

  def GetFeedbackResistorSetting(self):
    return int(self._SendCommand('usefeedbackres'))

  def SetFeedbackResistor(self, resistor=FEEDBACK_RES_AUTO):
    self._SendCommandOrDie('usefeedbackres %d' % resistor)

  def SetFeedbackResistorTemp(self, resistor=FEEDBACK_RES_AUTO):
    self._SendCommandOrDie('usefeedbackrestemp %d' % resistor)

  _AVERAGING_COMMANDS = {
    AVERAGING_AUTO: 'setautaveraging',
    AVERAGING_LOW: 'setlowaveraging',
    AVERAGING_MEDIUM: 'setmedaveraging',
    AVERAGING_HIGH: 'sethiaveraging',
  }

  def SetAveraging(self, averaging=AVERAGING_AUTO):
    self._SendCommandOrDie(self._AVERAGING_COMMANDS[averaging])

  def StartLogging(self, mask, period_seconds):
    self._SendCommandOrDie('startlogdata %d %d %d' % (mask, period_seconds * 100, time.time()))

  def StopLogging(self):
    self._SendCommandOrDie('stoplogdata')

  def EraseLogData(self):
    self._SendCommandOrDie('eraselogdata')

  def GetLogData(self):
    samples = int(self._SendCommand('getlogdata'))
    mask = int(self._GetLine())
    period = float(self._GetLine()) / 100
    ret = {
      'period_seconds': period,
      'samples': [],
    }
    fields = [
      'recorded',
    ]
    if mask & self.LOG_OPTICAL_DENSITY:
      fields.append('optical_density')
    if mask & self.LOG_TRANSMISSION_PERCENT:
      fields.append('transmission_percent')
    if mask & self.LOG_SENSOR_CURRENT:
      fields.append('sensor_current')
    if mask & self.LOG_SENSOR_VOLTAGE:
      fields.append('sensor_voltage')
    if mask & self.LOG_CONTROLLER_TEMP:
      fields.append('controller_temp')
    if mask & self.LOG_IRRADIANCE:
      fields.append('irradiance')

    for _ in range(samples):
      row = self._GetLine()
      values = row.split(',')
      sample = [
        datetime.datetime.fromtimestamp(int(values[0])),
      ]
      index = 1
      if mask & self.LOG_OPTICAL_DENSITY:
        sample.append(float(values[index]))
        index += 1
      if mask & self.LOG_TRANSMISSION_PERCENT:
        sample.append(float(values[index]))
        index += 1
      if mask & self.LOG_SENSOR_CURRENT:
        sample.append(float(values[index]))
        index += 1
      if mask & self.LOG_SENSOR_VOLTAGE:
        sample.append(float(values[index]))
        index += 1
      if mask & self.LOG_CONTROLLER_TEMP:
        sample.append(float(values[index]))
        index += 1
      if mask & self.LOG_IRRADIANCE:
        sample.append(float(values[index]))
        index += 1
      ret['samples'].append(_Row(fields, sample))
    return ret

  def GetInfo(self):
    # SPEC ERROR: There doesn't seem to be a good way to, other than a timing
    # hack, to find the end of the getinfo response.
    raise UnsupportedCommand

  def GetFriendlyName(self):
    return self._SendCommand('getfriendlyname')

  def SetFriendlyName(self, name):
    self._SendCommandOrDie('setfriendlyname %s' % name)

  def SetAmbientCurrent(self):
    self._SendCommandOrDie('setambientlevel')

  def ClearAmbientCurrent(self):
    self._SendCommandOrDie('clearambientlevel')

  def GetAmbientCurrent(self):
    return float(self._SendCommand('getambientlevel'))

  def SetSampleSeconds(self, seconds=0):
    self._SendCommandOrDie('setsampletime %d' % (seconds * 1000))

  def SetSampleSecondsTemp(self, seconds=0):
    self._SendCommandOrDie('setsampletimetemp %d' % (seconds * 1000))

  def GetSampleSeconds(self):
    ret = self._SendCommand('getsampletime')
    return float(ret) / 1000

  def GetBiasVoltage(self):
    return float(self._SendCommand('getbias'))

  def StartPeak(self):
    self._SendCommandOrDie('startpeak')

  def GetPeak(self):
    return float(self._SendCommand('getpeak'))

  def StartIntegrate(self):
    self._SendCommandOrDie('startintegrate')

  def StopIntegrate(self):
    self._SendCommandOrDie('stopintegrate')

  def GetIntegrate(self):
    return float(self._SendCommand('getintegrate'))


class _Row(object):

  def __init__(self, fields, values):
    self._fields = fields
    self._values = values

  def __getitem__(self, key):
    return self._values[self._fields.index(key)]

  def __str__(self):
    return str(self.AsDict())

  def __repr__(self):
    return repr(self.AsDict())

  def AsDict(self):
    return dict(zip(self._fields, self._values))
