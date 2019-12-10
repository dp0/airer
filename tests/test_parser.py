#!/usr/bin/env python3

import pytest

import sds011

READING_PACKET_INPUT_OUTPUTS = [
    # Example given as per datasheet docs
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0xd4, 0x04, 0x3a, 0x0a, 0xa1, 0x60, 0x1d, 0xab],
        (123.6, 261.8, 0xa160)
    ),
    # Zero PM2.5, Zero PM10
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0x00, 0x00, 0x00, 0x00, 0xa1, 0x60, 0x01, 0xab],
        (0.0, 0.0, 0xa160)
    ),
    # Zero PM2.5, Small PM10
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0x00, 0x00, 0x01, 0x00, 0xa1, 0x60, 0x02, 0xab],
        (0.0, 0.1, 0xa160)
    ),
    # Small PM2.5, Zero PM10
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0x02, 0x00, 0x00, 0x00, 0xa1, 0x60, 0x03, 0xab],
        (0.2, 0.0, 0xa160)
    ),
    # Small PM2.5, Small PM10
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0x03, 0x00, 0x04, 0x00, 0xa1, 0x60, 0x08, 0xab],
        (0.3, 0.4, 0xa160)
    ),
    # Theoretical Max PM2.5, Small PM10
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0xff, 0xff, 0x0a, 0x00, 0xa1, 0x60, 0x09, 0xab],
        (6553.5, 1.0, 0xa160)
    ),
    # Small PM2.5, Theoretical Max PM10
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0x0a, 0x00, 0xff, 0xff, 0xa1, 0x60, 0x09, 0xab],
        (1.0, 6553.5, 0xa160)
    ),
    # Large PM2.5, Large PM10
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0x12, 0x34, 0x56, 0x78, 0xa1, 0x60, 0x15, 0xab],
        (1333.0, 3080.6, 0xa160)
    ),
    # Large PM2.5, Large PM10 - Differing ID
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0x12, 0x34, 0x56, 0x78, 0xbe, 0xef, 0xc1, 0xab],
        (1333.0, 3080.6, 0xbeef)
    ),
    # Invalid Checksum
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0x12, 0x34, 0x56, 0x78, 0xbe, 0xef, 0xc0, 0xab],
        sds011.CorruptPacketException
    ),
    # Bad Header, Good Checksum
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xab, 0xc0, 0xd4, 0x04, 0x3a, 0x0a, 0xa1, 0x60, 0x1e, 0xab],
        sds011.CorruptPacketException
    ),
    # Bad Command, Good Checksum
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc1, 0xd4, 0x04, 0x3a, 0x0a, 0xa1, 0x60, 0x1e, 0xab],
        sds011.CorruptPacketException
    ),
    # Bad Tail, Good Checksum
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xaa, 0xc0, 0xd4, 0x04, 0x3a, 0x0a, 0xa1, 0x60, 0x1e, 0xac],
        sds011.CorruptPacketException
    ),
    # Trash
    (   # 0     1     2     3     4     5     6     7     8     9
        [0xbe, 0xef, 0xde, 0xad, 0xfa, 0xce, 0xc0, 0xc0, 0x13, 0x37],
        sds011.CorruptPacketException
    ),
]

@pytest.fixture(params=READING_PACKET_INPUT_OUTPUTS)
def reading_packet_input_output(request):
    return request.param

def test_parse_reading_packet(reading_packet_input_output):
    packet, exp = reading_packet_input_output
    def run_test():
        parser = sds011.Parser()
        parsed_pms = parser.parse_pms(packet)
        assert exp == parsed_pms

    if exp == sds011.CorruptPacketException:
        with pytest.raises(exp):
            run_test()
    else:
        run_test()

def test_parse_set_report_query_mode():
    parser = sds011.Parser()

    # Packet as per datasheet docs
    packet = [0xaa, 0xc5, 0x02, 0x01, 0x01, 0x00, 0xa1, 0x60, 0x05, 0xab]

    mode, address = parser.parse_report_mode(packet)
    assert 'query' == mode
    assert 0xa160 == address

def test_parse_get_report_active_mode():
    parser = sds011.Parser()

    # Packet as per datasheet docs
    packet = [0xaa, 0xc5, 0x02, 0x00, 0x00, 0x00, 0xa1, 0x60, 0x03, 0xab]

    mode, address = parser.parse_report_mode(packet)
    assert 'active' == mode
    assert 0xa160 == address

def test_parse_get_report_active_mode():
    parser = sds011.Parser()

    # Packet as per datasheet docs
    packet = [0xaa, 0xc5, 0x02, 0x00, 0x01, 0x00, 0xa1, 0x60, 0x04, 0xab]

    mode, address = parser.parse_report_mode(packet)
    assert 'query' == mode
    assert 0xa160 == address

def test_parse_get_report_mode_bad_checksum():
    parser = sds011.Parser()

    packet = [0xaa, 0xc5, 0x02, 0x00, 0x01, 0x00, 0xa1, 0x60, 0x05, 0xab]

    with pytest.raises(sds011.CorruptPacketException):
        mode, address = parser.parse_report_mode(packet)

def test_parse_get_report_mode_bad_mode():
    parser = sds011.Parser()

    packet = [0xaa, 0xc5, 0x02, 0x00, 0x02, 0x00, 0xa1, 0x60, 0x05, 0xab]

    with pytest.raises(sds011.CorruptPacketException):
        mode, address = parser.parse_report_mode(packet)
