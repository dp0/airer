#!/usr/bin/env python3

import pytest

import sds011

READING_PACKET_INPUT_OUTPUTS = [
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0xd4, 0x04, 0x3a, 0x0a, 0xa1, 0x60, 0x1d, 0xab],
        (123.6, 261.8)
    ),
]

@pytest.fixture
def reading_packet_input_output():
    for input_output in READING_PACKET_INPUT_OUTPUTS:
        yield input_output

def test_parse_reading_packet(reading_packet_input_output):
    packet, pms = reading_packet_input_output
    parser = sds011.Parser()
    parsed_pms = parser.parse_pms(packet)
    assert pms == parsed_pms
