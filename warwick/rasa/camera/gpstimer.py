#
# This file is part of rasa-camd
#
# rasa-camd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rasa-camd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rasa-camd.  If not, see <http://www.gnu.org/licenses/>.

"""Controller for GPS timer board"""

import datetime
import struct
import threading
import time
import serial
from warwick.observatory.common import log

# pylint: disable=invalid-name
# pylint: disable=broad-except
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-instance-attributes
# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

FMT_GREEN = u'\033[92m'
FMT_RED = u'\033[91m'
FMT_YELLOW = u'\033[93m'
FMT_BOLD = u'\033[1m'
FMT_CLEAR = u'\033[0m'

def gps_to_utc(week, ms, ns):
    """Convert a GPS week number and millisecond count
       (UTC time base) to a UTC python datetime
    """
    return datetime.datetime(1980, 1, 6) + datetime.timedelta(days=7 * week, milliseconds=ms,
                                                              microseconds=ns/1000)

class GPSFixType:
    NoFix, DeadReckoning, Pos2D, Pos3D, GPSPlusDeadReckoning, TimeOnly = range(6)
    Labels = ['NO FIX', 'DEAD RECKONING', '2D FIX', '3D FIX', 'GPS + DEAD RECKONING',
              'TIME ONLY FIX']

class GPSLocalCheckStatus:
    Unknown, Good, Warn, Error = range(4)
    _labels = [
        ('UNKNOWN', ''),
        ('GOOD', FMT_GREEN),
        ('WARNING', FMT_YELLOW),
        ('BAD', FMT_RED)
    ]

    @classmethod
    def label(cls, status_code, colored=False):
        """Returns a human readable string describing an error code"""
        if status_code >= 0 and status_code < len(cls._labels):
            status = cls._labels[status_code]
            if colored:
                return FMT_BOLD + status[1] + status[0] + FMT_CLEAR
            return status[0]

        return 'unknown status {}'.format(status_code)

class GPSTimer:
    def __init__(self, port_path, port_baud, log_table, active_high=False):
        self._port_path = port_path
        self._port_baud = port_baud
        self._log_table = log_table
        self._active_high = active_high
        self._port = None
        self._port_error = False
        self._lock = threading.Lock()

        self._satellites = 0
        self._fix_type = 0
        self._last_start = None
        self._last_end = None
        self._last_utc = None

        # Check GPS time vs the local clock
        self._last_check_delta = None
        self._last_check_status = GPSLocalCheckStatus.Unknown

        runloop = threading.Thread(target=self.__run)
        runloop.daemon = True
        runloop.start()

    def __run(self):
        """Main run loop"""
        while True:
            # Initial setup
            try:
                self._port = serial.Serial(self._port_path, self._port_baud, timeout=0.1)
                print('Connected to GPS timer on ', self._port_path)
                prefix = 'Restored' if self._port_error else 'Established'
                log.info(self._log_table, prefix + ' serial connection to GPS timer')
                self._port_error = False
            except Exception as exception:
                print(exception)
                print('Will retry in 10 seconds...')
                if not self._port_error:
                    log.error(self._log_table, 'Failed to connect to GPS timer')

                self._port_error = True

                time.sleep(10.)
                continue
            try:
                # Flush any stale state
                self._port.reset_input_buffer()
                self._port.reset_output_buffer()
                self.__send_config()

                # Main run loop
                buf = b''
                while True:
                    # Read as much data as we can or block until the timeout expires
                    buf += self._port.read(max(1, self._port.in_waiting))

                    # Sync on start of UBX packet
                    start = 0
                    for start in range(len(buf)-2):
                        if buf[start] == 0xb5 and buf[start+1] == 0x62:
                            break

                    if start > 0:
                        print('timer: discarding {} junk bytes'.format(start))
                        buf = buf[start:]

                    # We need at least 4 bytes to determine packet type
                    if len(buf) < 4:
                        continue

                    (msg_cls, msg_id, msg_len) = struct.unpack_from('<BBh', buf, offset=2)
                    if len(buf) < 8 + msg_len:
                        continue

                    # Verify message checksum
                    chka = chkb = 0
                    for i in range(2, msg_len + 6):
                        chka += buf[i]
                        chkb += chka
                    chka = chka & 0xFF
                    chkb = chkb & 0xFF

                    if chka == buf[msg_len+6] and chkb == buf[msg_len+7]:
                        self.__parse_message(msg_cls, msg_id, buf)
                    else:
                        print('timer: discarding packet: checksum mismatch')

                    buf = buf[8+msg_len:]

            except Exception as exception:
                self._port.close()
                print(exception)
                print('Will retry in 10 seconds...')
                if not self._port_error:
                    log.error(self._log_table, 'Lost serial connection to GPS timer')
                self._port_error = True
                time.sleep(10.)

    def __send_config(self):
        # Disable default NMEA messages
        self.__send_configure_message(0xF0, 0x00, False) # GGA (GPS fix data)
        self.__send_configure_message(0xF0, 0x01, False) # GLL (latitude/longitude)
        self.__send_configure_message(0xF0, 0x02, False) # GSA (DOP and active satellites)
        self.__send_configure_message(0xF0, 0x03, False) # GSV (satellites in view)
        self.__send_configure_message(0xF0, 0x04, False) # RMC (recommended minimum data)
        self.__send_configure_message(0xF0, 0x05, False) # VTG (coarse over-ground speed)

        # Enable the UBX messages that we want
        self.__send_configure_message(0x0D, 0x03, True) # TIM-TM2 (time mark data)
        self.__send_configure_message(0x01, 0x07, True) # NAV-PVT (Navigation Pos/Vel/Time)

        # UBX-CFG-NAV5 (set stationary dynamic model, force 3D fixes only, force USNO UTC time base)
        self.__send_message(0x06, 0x24, [
            0xFF, 0xFF,# Parameters bitmask (default value)
            0x02, # Stationary dynamic model (changed from default = 0x00)
            0x03, # Allow 2D or 3D fixes (default value)
            0x09, 0x53, 0x00, 0x00, # Fixed altitude for 2D fix mode (changed from default = 0)
            0x10, 0x27, 0x00, 0x00, # Fixed altitude variance for 2D fix mode (default value)
            0x05, # Minimum elevation for satellite to be used (default value)
            0x00, # Reserved (default value)
            0xFA, 0x00, # Position DOP mask (default value)
            0xFA, 0x00, # Time DOP mask (default value)
            0x64, 0x00, # Position accuracy mask (default value)
            0x5E, 0x01, # Time accuracy mask (default value)
            0x00, # Static hold threshold (default value)
            0x3C, # DGNSS timeout (default value)
            0x00, # Number of satellites required before attempting fix (default value)
            0x00, # Signal threshold for satellites to attempt fix (default value)
            0x00, 0x00, # Reserved, (default value)
            0x00, 0x00, # Static hold distance threshold, (default value)
            0x03, # USNO UTC time standard (changed from default = 0x00)
            0x00, 0x00, 0x00, 0x00, 0x00 # Reserved
        ])

        # NOTE: The UBLOX manual comments in the Time pulse recommendations section (18.2)
        # that for best time pulse performance the SBAS subsystem should be disabled
        # and an accurate fixed position defined.
        # It also comments a 300m position accuracy is sufficient for time accuracies of
        # the order of microseconds, so this is probably overkill for our requirements.

        # UBX-CFG-RATE (set update rate to 10Hz)
        self.__send_message(0x06, 0x08, [0x64, 0x00, 0x01, 0x00, 0x01, 0])

    def __parse_message(self, msg_cls, msg_id, buf):
        if msg_cls == 0x0D and msg_id == 0x03: # TIM-TM2
            (_, flags, _, wnR, wnF, towMsR, towSubMsR, towMsF, towSubMsF, _) = \
                struct.unpack_from('BBHHHIIIII', buf, offset=6)
            newFallingEdge = flags & 0x04 == 0x04
            timeBaseUTC = flags & 0x10 == 0x10
            utc = flags & 0x20 == 0x20
            valid = flags & 0x40 == 0x40
            newRisingEdge = flags & 0x80 == 0x80

            if valid and timeBaseUTC and utc:
                with self._lock:
                    if self._active_high:
                        if newRisingEdge:
                            self._last_start = gps_to_utc(wnR, towMsR, towSubMsR)
                            self._last_end = None
                        if newFallingEdge:
                            self._last_end = gps_to_utc(wnF, towMsF, towSubMsF)
                    else:
                        if newFallingEdge:
                            self._last_start = gps_to_utc(wnF, towMsF, towSubMsF)
                            self._last_end = None
                        if newRisingEdge:
                            self._last_end = gps_to_utc(wnR, towMsR, towSubMsR)
        elif msg_cls == 0x01 and msg_id == 0x07: # NAV-PVT
            (year, month, day, hour, minute, second, valid, _, nanosecond, fixType,
             _, _, numSV) = struct.unpack_from('HBBBBBBIiBBBB', buf, offset=10)

            with self._lock:
                self._satellites = numSV
                self._fix_type = fixType

                # validDate and validTime and fullyResolved
                if (valid & 0x07) == 0x07:
                    self._last_utc = datetime.datetime(year, month, day, hour, minute, second) + \
                        datetime.timedelta(microseconds=nanosecond / 1000)

                    # This message is delayed by ~50-75 ms but may have an additional 100ms delay
                    # (message poll rate) for an unknown reason
                    # We will consider the NTP-GPS offset okay provided it is less than 250ms
                    if self._fix_type not in [GPSFixType.NoFix, GPSFixType.DeadReckoning]:
                        self._last_check_delta = \
                            (datetime.datetime.utcnow() - self._last_utc).total_seconds()
                        if abs(self._last_check_delta) < 0.250:
                            self._last_check_status = GPSLocalCheckStatus.Good
                        elif abs(self._last_check_delta) < 0.5:
                            self._last_check_status = GPSLocalCheckStatus.Warn
                        else:
                            self._last_check_status = GPSLocalCheckStatus.Error
                    else:
                        self._last_check_status = GPSLocalCheckStatus.Unknown
                else:
                    self._last_utc = None
                    self._last_check_status = GPSLocalCheckStatus.Unknown
        else:
            print('timer: Ignoring unknown packet type {:02x} {:02x}'.format(msg_cls, msg_id))

    def __send_configure_message(self, msg_cls, msg_id, enabled):
        usb = 0x01 if enabled else 0x00
        self.__send_message(0x06, 0x01, [msg_cls, msg_id, 0x00, 0x00, 0x00, usb, 0x00, 0x00])

    def __send_message(self, msg_cls, msg_id, payload):
        if len(payload) > 255:
            raise Exception("payload > 255 bytes not implemented")
        buf = [0xB5, 0x62]
        buf.append(msg_cls)
        buf.append(msg_id)
        cka = msg_cls + msg_id
        ckb = 2 * msg_cls + msg_id
        buf.append(len(payload))
        buf.append(0)
        cka += len(payload)
        ckb += 2 * cka
        for b in payload:
            buf.append(b)
            cka += b
            ckb += cka
        buf.append(cka & 0xFF)
        buf.append(ckb & 0xFF)
        self._port.write(buf)

    def report_status(self):
        """Returns a dictionary containing the current timer state"""
        with self._lock:
            last_utc = None
            if self._last_utc is not None:
                last_utc = self._last_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            return {
                'satellites': self._satellites,
                'fix_type': self._fix_type,
                'last_utc': last_utc,
                'last_check_delta': self._last_check_delta,
                'last_check_status': self._last_check_status
            }

    def last_trigger(self):
        """Returns a tuple containing the last trigger times"""
        with self._lock:
            return (self._last_start, self._last_end)

    def clear_last_trigger(self):
        """Clears the last recorded trigger"""
        with self._lock:
            self._last_start = self._last_end = None
