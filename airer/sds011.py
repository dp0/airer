#!/usr/bin/env python3

import argparse
import serial
import sys


class CorruptPacketException(Exception):
    pass


class Crafter:
    def __init__(self):
        pass

    def _addr_to_addr_bytes(self, addr):
        return addr >> 8, addr & 0x00ff

    def reporting_mode(self, set_mode=None, device_id=0xffff):
        device_id_byte_1, device_id_byte_2 = self._addr_to_addr_bytes(device_id)
        if set_mode == 'query':
            get_set_byte = 0x01
            active_query_byte = 0x01
        elif set_mode == 'active':
            get_set_byte = 0x01
            active_query_byte = 0x00
        elif set_mode is None:
            get_set_byte = 0x00
            active_query_byte = 0x00
        else:
            raise ValueError(f'set_mode was "{set_mode}", which is not a supported mode')

        data_bytes = [
            0x02, get_set_byte, active_query_byte,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            device_id_byte_1, device_id_byte_2
        ]

        return [0xaa, 0xb4] + data_bytes + [self._compute_checksum(data_bytes), 0xab]

    def query_pms(self, device_id=0xffff):
        device_id_byte_1, device_id_byte_2 = self._addr_to_addr_bytes(device_id)

        data_bytes = [
            0x04, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            device_id_byte_1, device_id_byte_2
        ]

        return [0xaa, 0xb4] + data_bytes + [self._compute_checksum(data_bytes), 0xab]


    def _compute_checksum(self, data_bytes):
        return sum(data_bytes) % 0x100


class Parser:
    def __init__(self):
        pass

    def _check_packet(self, packet, head, command, tail):
        if packet[0] != head:
            raise CorruptPacketException()
        if packet[1] != command:
            raise CorruptPacketException()
        if packet[9] != tail:
            raise CorruptPacketException()
        if sum(packet[2:8]) % 0x100 != packet[8]:
            raise CorruptPacketException()

    def _addr_bytes_to_addr(self, addr_1, addr_2):
        return (addr_1 << 8) + addr_2

    def parse_pms(self, packet):
        address = self._addr_bytes_to_addr(packet[6], packet[7])
        self._check_packet(packet, 0xaa, 0xc0, 0xab)
        def calculate_value(offset):
            return ((packet[offset+1] * 256) + packet[offset]) / 10
        pm_2_5 = calculate_value(2)
        pm_10 = calculate_value(4)

        return (pm_2_5, pm_10, address)

    def parse_report_mode(self, packet):
        self._check_packet(packet, 0xaa, 0xc5, 0xab)
        address = self._addr_bytes_to_addr(packet[6], packet[7])
        report_mode_byte = packet[4]
        if report_mode_byte == 0x00:
            mode = 'active'
        elif report_mode_byte == 0x01:
            mode = 'query'
        else:
            raise CorruptPacketException()
        return (mode, address)


class SDS011:
    def __init__(self, device_file, speed, parser=Parser, crafter=Crafter):
        self.device = serial.Serial(device_file, speed)
        self.parser = parser()
        self.crafter = crafter()
        try:
            self.device.open()
        except serial.serialutil.SerialException:
            pass

    def active_read_pms(self):
        packet = self.device.read(10)
        return self.parser.parse_pms(packet)

    def get_reporting_mode(self):
        tx_packet = self.crafter.reporting_mode()
        self.device.write(tx_packet)
        rx_packet = self.device.read(10)
        return self.parser.parse_report_mode(rx_packet)

    def set_reporting_mode(self, reporting_mode):
        tx_packet = self.crafter.reporting_mode(set_mode=reporting_mode)
        self.device.write(tx_packet)
        rx_packet = self.device.read(10)
        return self.parser.parse_report_mode(rx_packet)

    def query_read_pms(self):
        tx_packet = self.crafter.query_pms()
        self.device.write(tx_packet)
        packet = self.device.read(10)
        return self.parser.parse_pms(packet)

def main():

    parser = argparse.ArgumentParser(description='sds011 management CLI')

    parser.add_argument('-d', '--device',
        help='Path to the sds011 serial device.',
        default='/dev/ttyUSB0',
        type=str
    )
    parser.add_argument('-s', '--speed',
        help='The baud rate for communication with the sds011 serial device.',
        default=9600,
        type=int
    )

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    def read(args, sds011):
        if args.query:
            pm_2_5, pm_10, addr = sds011.query_read_pms()
        else:
            pm_2_5, pm_10, addr = sds011.active_read_pms()

        print(f'Device ID: {addr}\nPM2.5 (µg/m³): {pm_2_5}\nPM10 (µg/m³): {pm_10}')

    parser_read = subparsers.add_parser('read',
        description='Take a reading from the sds011 to give values for the'
        ' PM2.5 and PM10 levels.'
    )
    parser_read.add_argument('--query', action='store_true',
        help='Query the sds011 for readings, rather than passively receiving'
        ' them. This is required if the sds011 is in the `query` reporting'
        ' mode.')
    parser_read.set_defaults(func=read)

    def mode(args, sds011):
        if args.new_mode:
            cur_mode, addr = sds011.set_reporting_mode(args.new_mode)
        else:
            cur_mode, addr = sds011.get_reporting_mode()

        print(f'Device ID: {addr}\nReporting Mode: {cur_mode}')

    parser_mode = subparsers.add_parser('mode',
        description='Retrieve (and set) the reporting mode of the sds011'
        ' serial device. If `new_mode` is specified, this will be persisted as'
        ' the reporting mode on the sds011, else the current reporting mode'
        ' will only be displayed.'
    )
    parser_mode.add_argument('new_mode', nargs='?', type=str,
        help='The new reporting mode to persist. For the `active`'
        ' reporting mode (the factory default), the sds011 will periodically'
        ' take readings and send these over the serial link. For the `query`'
        ' reporting mode, the sds011 needs to be queried to take a reading.'
    )
    parser_mode.set_defaults(func=mode)

    args = parser.parse_args()
    sds011 = SDS011(args.device, args.speed)
    args.func(args, sds011)


if __name__ == '__main__':
    sys.exit(main())
