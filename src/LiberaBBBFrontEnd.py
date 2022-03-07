#!/usr/bin/env python
# -*- coding:utf-8 -*-


# ############################################################################
#  license :
# ============================================================================
#
#  File :        LiberaBBBFrontEnd.py
#
#  Project :     LiberaBBBFrontEnd
#
# This file is part of LiberaBBBFrontEnd tango device server.
#
# LiberaBBBFrontEnd tango device server is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# LiberaBBBFrontEnd tango device server is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LiberaBBBFrontEnd tango device server.  If not, see
# <http://www.gnu.org/licenses/>.
#
# ############################################################################

import sys
import socket
try:
    import tango  # python tango >= 8
    try:
        from tango import LatestDeviceImpl as DeviceImpl  # python tango>=9.2.1
    except:
        from tango import Device_5Impl as DeviceImpl  # python tango<9.2.1
except:
    import PyTango as tango  # python tango < 8
    from PyTango import Device_4Impl as DeviceImpl


__all__ = ['LiberaBBBFrontEnd', 'LiberaBBBFrontEndClass', 'main']
__version = '1.0.1'  # managed with bumpversion (do not update manually)


# libera BBFE attributes
attributes = {
    # name: [
    #   type, read cmd, write cmd, description, min, max, units]
    'TimeToSleep': [
        tango.DevShort,
        'TIM:SLE',
        '',
        'Time before LCD enters into sleep mode',
        1,
        60,
        'min'],
    'BrightnessInSleep': [
        tango.DevShort,
        'BRI:SLE',
        '',
        'Brightness of the LCD in sleep mode',
        0,
        100,
        '%'],
    'BrightnessInAwakened': [
        tango.DevShort,
        'BRI:AWA',
        '',
        'Brightness of the LCD in normal mode',
        10,
        100,
        '%'],
    'FanSpeedSetpoint': [
        tango.DevShort,
        'FAN:SSP',
        '',
        'Fan speed setpoint',
        1000,
        7500,
        'rpm'],
    'FanSpeed': [
        tango.DevShort,
        'FAN:MSP',
        None,
        'Fan speed',
        None,
        None,
        'rpm'],
    'TemperatureLimit': [
        tango.DevShort,
        'TEM:LIM',
        '',
        'Temperature limit where Libera shuts down',
        20,
        60,
        'C'],
    'Temperature': [
        tango.DevDouble,
        'TEM:INS',
        None,
        'Temperature inside the libera',
        None,
        None,
        'C'],
    'TemperatureAlarm': [
        tango.DevString,
        'TEM:ALA',
        None,
        'Temperature alarm status',
        None,
        None,
        None],
    'Uptime': [
        tango.DevString,
        'TIM:UP',
        None,
        'Temperature alarm status',
        None,
        None,
        None],
    'Volt33': [
        tango.DevDouble,
        'VOL:3V3',
        None,
        'Actual value of the 3.3V supply voltage',
        None,
        None,
        'volts'],
    'Volt5': [
        tango.DevDouble,
        'VOL:5V',
        None,
        'Actual value of the 5V supply voltage',
        None,
        None,
        'volts'],
    'Volt_5': [
        tango.DevDouble,
        'VOL:-5V',
        None,
        'Actual value of the -5V supply voltage',
        None,
        None,
        'volts'],
    'Volt8': [
        tango.DevDouble,
        'VOL:8V',
        None,
        'Actual value of the 8V supply voltage',
        None,
        None,
        'volts'],
    'Volt12': [
        tango.DevDouble,
        'VOL:12V',
        None,
        'Actual value of the 12V supply voltage',
        None,
        None,
        'volts'],
    'LevelX': [
        tango.DevShort,
        'LEV:X',
        'X input level',
        '',
        -60,
        -20,
        'dBm'],
    'LevelY': [
        tango.DevShort,
        'LEV:Y',
        'Y input level',
        '',
        -60,
        -20,
        'dBm'],
    'LevelI': [
        tango.DevShort,
        'LEV:I',
        'I input level',
        '',
        -50,
        -10,
        'dBm'],
    'PhaseShift': [
        tango.DevShort,
        'PHA',
        'Phase shift of the LO signal',
        '',
        -180,
        180,
        'degrees'],
    'PhaseOffsetX': [
        tango.DevShort,
        'PHA:OFF:X',
        'Phase offset of the LO signal for X signal',
        '',
        -180,
        180,
        'degrees'],
    'PhaseOffsetY': [
        tango.DevShort,
        'PHA:OFF:Y',
        'Phase offset of the LO signal for Y signal',
        '',
        -180,
        180,
        'degrees'],
    'PhaseOffsetIT': [
        tango.DevShort,
        'PHA:OFF:IT',
        'Phase offset of the LO signal for IT signal',
        '',
        -180,
        180,
        'degrees'],
    'PhaseOffsetIL': [
        tango.DevShort,
        'PHA:OFF:IL',
        'Phase offset of the LO signal for IL signal',
        '',
        -180,
        180,
        'degrees'],
    'PhaseClock1': [
        tango.DevShort,
        'PHA:CLO:1',
        'MC phase shift clk1 output',
        '',
        -180,
        180,
        'degrees'],
    'PhaseClock2': [
        tango.DevShort,
        'PHA:CLO:2',
        'MC phase shift clk2 output',
        '',
        -180,
        180,
        'degrees'],
    'PhaseClock3': [
        tango.DevShort,
        'PHA:CLO:3',
        'MC phase shift clk3 output',
        '',
        -180,
        180,
        'degrees'],
    'PhaseClock4': [
        tango.DevShort,
        'PHA:CLO:4',
        'MC phase shift clk4 output',
        '',
        -180,
        180,
        'degrees'],
}


class LiberaBBBFrontEnd(DeviceImpl):
    """Device for controlling Libera BunchByBunch front end"""

    SIZE = 4096  # default buffer size for receiving data

    def __init__(self, cl, name):
        DeviceImpl.__init__(self, cl, name)
        self.debug_stream('In __init__()')
        self.setup_state_machine()
        LiberaBBBFrontEnd.init_device(self)

    def init_device(self):
        self.debug_stream('In init_device()')
        self.get_device_properties(self.get_device_class())
        try:
            # connect to instrument
            self.debug_stream(
                'Connecting to %s using port %d' % (self.Host, self.Port))
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3)
            self.sock.connect((self.Host, self.Port))
            # try to start and clean scpi console
            data = self.sock.recv(self.SIZE)
            data = data.decode('ascii')
            self.debug_stream('init_device conn: %s' % repr(data))
            self.sock.send(b'scpi>\r\n')
            data = self.sock.recv(4096)
            data = data.decode('ascii')
            self.debug_stream('init_device scpi: %s' % repr(data))
            # read IDN to check communication
            self.sock.send(b'*IDN?\r\n')
            data = self.sock.recv(self.SIZE)
            data = data.decode('ascii')
            self.debug_stream('init_device *IDN: %s' % repr(data))
            if (data.find('BBFE') != -1):
                msg = 'System seems OK'
                state_ = tango.DevState.ON
            else:
                msg = 'Invalid answer from instrument'
                state_ = tango.DevState.FAULT
            self._set_state(state_, msg, force_init=True)
        except Exception as e:
            msg = 'Unable to communicate with instrument'
            self.error_stream('%s: %s' % (msg, str(e)))
            self._set_state(tango.DevState.FAULT, msg, force_init=True)

    def delete_device(self):
        self.debug_stream('In delete_device()')
        self.sock.close()

    def always_executed_hook(self):
        self.debug_stream('In always_excuted_hook()')

    def read_attr(self, attr):
        name = attr.get_name()
        cmd = bytes(attributes[name][1], 'ascii')
        # command should be something like 'BRI:AWA?\r\n'
        cmd += b'?\r\n'
        self.debug_stream('read_%s sending command: %s' % (name, repr(cmd)))
        try:
            self.sock.send(cmd)
            # answer should be something like:
            #   "BRI:AWA 100\r\nOK\r\nscpi>"
            #   or (note units):
            #   "FAN:MSP 4170 rpm\r\nOK\r\nscpi>"
            #   or even (note ' character):
            #   "PHA:CLO:1 +020'\r\nOK\r\nscpi>"
            answer = self.sock.recv(self.SIZE)
            answer = answer.decode('ascii')
            self.debug_stream('read_%s answer: %s' % (name, repr(answer)))
        except Exception as e:
            msg = 'Comm error while requesting data from instrument'
            self.error_stream('%s: %s' % (msg, str(e)))
            self._set_state(tango.DevState.FAULT, msg)
            tango.Except.throw_exception(
                'read_attr', msg, '%s.read_attr()' % self.__class__.__name__)
        try:
            value, ok, waste = answer.split('\r\n')
            answer = value.split()
            value = answer[1].strip("\'")  # ' character returned sometimes
            if attributes[name][0] is tango.DevShort:
                value = int(value)
            elif attributes[name][0] is tango.DevDouble:
                value = float(value)
            else:
                pass
        except Exception as e:
            msg = 'Error processing answer from instrument'
            self.error_stream('%s: %s' % (msg, str(e)))
            tango.Except.throw_exception(
                'read_attr', msg, '%s.read_attr()' % self.__class__.__name__)
        attr.set_value(value)

    def write_attr(self, attr):
        name = attr.get_name()
        value = attr.get_write_value()
        cmd = '%s %s\r\n' % (attributes[name][1], str(value))
        cmd = bytes(cmd, 'ascii')
        self.debug_stream('write_%s sending command: %s' % (name, repr(cmd)))
        try:
            self.sock.send(bytes(cmd))
            answer = self.sock.recv(self.SIZE)
            answer = answer.decode('ascii')
            self.debug_stream('write_%s answer: %s' % (name, repr(answer)))
        except Exception as e:
            msg = 'Comm error while sending data to instrument'
            self.error_stream('%s: %s' % (msg, str(e)))
            self._set_state(tango.DevState.FAULT, msg)
            tango.Except.throw_exception(
                'write_attr', msg, '%s.write_attr()' % self.__class__.__name__)
        # check that command was correctly processed
        if (answer.find('OK') == -1):
            msg = 'Seems like attribute was not correctly written. Check!'
            self.error_stream(msg)
            tango.Except.throw_exception(
                'write_attr', msg, '%s.write_attr()' % self.__class__.__name__)

    def Reset(self):
        cmd = b'*RST\r\n'
        self.debug_stream('Reset sending command: %s' % repr(cmd))
        try:
            self.sock.send(cmd)
            answer = self.sock.recv(self.SIZE)
            answer = answer.decode('ascii')
            self.debug_stream('Reset answer: %s' % repr(answer))
        except Exception as e:
            msg = 'Comm error while sending command to instrument'
            self.error_stream('%s: %s' % (msg, str(e)))
            self._set_state(tango.DevState.FAULT, msg)
            tango.Except.throw_exception(
                'Reset', msg, '%s.Reset()' % self.__class__.__name__)
        # check that command was correctly processed
        if (answer.find('OK') == -1):
            msg = 'Seems like the command was not correctly processed. Check!'
            self.error_stream(msg)
            tango.Except.throw_exception(
                'Reset', msg, '%s.Reset()' % self.__class__.__name__)

    # -------------------------------------------------------------------------
    #    Utility functions
    # -------------------------------------------------------------------------
    def _set_state(self, new_state, new_status=None, force_init=False):
        state_now = self.get_state()
        # don't allow to change FAULT state unless initialing
        nok = [tango.DevState.FAULT]
        if state_now in nok and not force_init:
            return
        if (state_now == new_state) and (not force_init):
            return
        self.set_state(new_state)
        if new_status is not None:
            self.set_status(new_status)

    def setup_state_machine(self):
        '''
        By default allow all the attributes in all the states except writing
        when FAULT
        By default allow all the commands in all the states
        '''
        for attr in LiberaBBBFrontEndClass.attr_list:
            method = 'is_' + attr + '_allowed'
            if not hasattr(self, method):
                setattr(self, method, self.is_allowed_default)

        for cmd in LiberaBBBFrontEndClass.cmd_list:
            method = 'is_' + cmd + '_allowed'
            if not hasattr(self, method):
                setattr(self, method, self.is_allowed_default)

    def is_allowed_default(self, req_type=None):
        if req_type is None:
            check = True  # this is a command
        elif req_type is not None and req_type == tango.AttReqType.WRITE_REQ:
            check = True  # write attribute
        else:
            check = False  # read attribute

        if check and self.get_state() in [tango.DevState.FAULT]:
            return False
        else:
            return True

    # ------------------------------------------------------------------------
    # Dynamic attributes initialization and read/write methods
    # ------------------------------------------------------------------------
    def initialize_dynamic_attributes(self):
        try:
            self.debug_stream('Initializing dynamic attributes')
            for attr_name, props in list(attributes.items()):
                type_, read_, write_, desc_, min_, max_, units_ = props
                if write_ is not None:
                    rw = tango.AttrWriteType.READ_WRITE
                    write_ = self.write_attr
                else:
                    rw = tango.AttrWriteType.READ
                if not hasattr(self, attr_name):
                    attr = tango.Attr(attr_name, type_, rw)
                    attr_prop = tango.UserDefaultAttrProp()
                    if min_ is not None:
                        attr_prop.set_min_value(str(min_))
                    if max_ is not None:
                        attr_prop.set_max_value(str(max_))
                    if units_ is not None:
                        attr_prop.set_unit(units_)
                    attr_prop.set_label(attr_name)
                    attr_prop.set_description(desc_)
                    attr.set_default_properties(attr_prop)
                    self.add_attribute(
                        attr, self.read_attr, write_, self.is_allowed_default)
        except Exception as e:
            msg = 'Error while processing dynamic attributes. Please check!'
            self.error_stream('%s: %s' % (msg, str(e)))
            self._set_state(tango.DevState.FAULT, msg)


class LiberaBBBFrontEndClass(tango.DeviceClass):

    def dyn_attr(self, dev_list):
        """Invoked to create dynamic attributes for the given devices.
        Default implementation calls
        :meth:`Tmp.initialize_dynamic_attributes` for each device

        :param dev_list: list of devices
        :type dev_list: :class:`PyTango.DeviceImpl`"""
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except Exception as e:
                dev.warn_stream('Failed to initialize dynamic attributes')
                dev.debug_stream('Details: %s' % str(e))

    # Class Properties
    class_property_list = {
    }

    # Device Properties
    device_property_list = {
        'Host':
            [tango.DevString,
             'Hostname of bbbfe',
             ''],
        'Port':
            [tango.DevShort,
             'Port to communicate (default is telnet)',
             23],
    }

    # Command definitions
    cmd_list = {
        'Reset': [
            [tango.ArgType.DevVoid],
            [tango.ArgType.DevVoid]],
    }

    # Attribute definitions
    attr_list = {
    }


def main():
    try:
        py = tango.Util(sys.argv)
        if tango.Release.version_number <= 711:
            py.add_TgClass(
                LiberaBBBFrontEndClass, LiberaBBBFrontEnd, 'LiberaBBBFrontEnd')
        else:
            py.add_class(LiberaBBBFrontEndClass, LiberaBBBFrontEnd)
        U = tango.Util.instance()
        U.server_init()
        U.server_run()
    except tango.DevFailed as e:
        print(('-------> Received a DevFailed exception:', e))
    except Exception as e:
        print(('-------> An unforeseen exception occurred....', e))


if __name__ == '__main__':
    main()

