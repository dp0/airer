#!/usr/bin/env python3

import serial
import sys


class CorruptPacketException(Exception):
    pass


class Parser:
    def __init__(self):
        pass

    def _check_packet(self, packet):
        if packet[0] != 0xaa:
            raise CorruptPacketException()
        if packet[1] != 0xc0:
            raise CorruptPacketException()
        if packet[9] != 0xab:
            raise CorruptPacketException()
        if sum(packet[2:8]) % 0x100 != packet[8]:
            raise CorruptPacketException()

    def parse_pms(self, packet):
        self._check_packet(packet)
        def calculate_value(offset):
            return ((packet[offset+1] * 256) + packet[offset]) / 10
        pm_2_5 = calculate_value(2)
        pm_10 = calculate_value(4)

        return (pm_2_5,pm_10)



class MatterReader:
    def __init__(self, device_file, speed):
        self.device = serial.Serial(device_file, speed)
        try:
            self.device.open()
        except serial.serialutil.SerialException:
            pass



    def read(self):
        packet = self.device.read(10)


    def query_reporting_mode(self):
        tx_packet = [
            0xaa, # Head
            0xb4, # Command ID
            0x02, # Data byte 1
            0x00, # Data byte 2 -> 0: query
            0x00, 0x00, 0x00, 0x00, # Data bytes 3-6
            0x00, 0x00, 0x00, 0x00, # Data bytes 7-10
            0x00, 0x00, 0x00, # Data bytes 11-13
            0xff, 0xff, # Data bytes 14-15: 0xff: broadcast
            0x00, 0xab
        ]

        self.device.write(tx_packet)

        rx_packet = self.device.read(10)

        [print(hex(b)) for b in rx_packet]


def main():
    reader = MatterReader('/dev/ttyUSB0', 9600)
    reader.query_reporting_mode()
    print(reader.read())

if __name__ == '__main__':
    sys.exit(main())
