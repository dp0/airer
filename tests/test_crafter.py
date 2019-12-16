#!/usr/bin/env python3

import pytest

from airer import sds011


def test_craft_set_report_query_mode():
    crafter = sds011.Crafter()

    expected_packet = [
        #0     1     2     3     4     5     6     7     8     9
        0xaa, 0xb4, 0x02, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
        #10    11    12    13    14    15    16    17    18
        0x00, 0x00, 0x00, 0x00, 0x00, 0xa1, 0x60, 0x05, 0xab
    ]

    crafted_packet = crafter.reporting_mode(
                       set_mode='query',
                       device_id=0xa160
                     )

    assert expected_packet == crafted_packet

def test_craft_set_report_active_mode():
    crafter = sds011.Crafter()

    expected_packet = [
        #0     1     2     3     4     5     6     7     8     9
        0xaa, 0xb4, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        #10    11    12    13    14    15    16    17    18
        0x00, 0x00, 0x00, 0x00, 0x00, 0xa1, 0x60, 0x04, 0xab
    ]

    crafted_packet = crafter.reporting_mode(
                       set_mode='active',
                       device_id=0xa160
                     )

    assert expected_packet == crafted_packet

def test_craft_get_report_active_mode():
    crafter = sds011.Crafter()

    expected_packet = [
        #0     1     2     3     4     5     6     7     8     9
        0xaa, 0xb4, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        #10    11    12    13    14    15    16    17    18
        0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0xab
    ]

    crafted_packet = crafter.reporting_mode()

    assert expected_packet == crafted_packet

def test_craft_set_bad_mode():
    crafter = sds011.Crafter()

    with pytest.raises(ValueError):
        crafted_packet = crafter.reporting_mode(set_mode='junk')

def test_craft_query_pms_all():
    crafter = sds011.Crafter()

    expected_packet = [
        #0     1     2     3     4     5     6     7     8     9
        0xaa, 0xb4, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        #10    11    12    13    14    15    16    17    18
        0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0x02, 0xab
    ]

    crafted_packet = crafter.query_pms()

    assert expected_packet == crafted_packet

def test_craft_query_pms_specific():
    crafter = sds011.Crafter()

    expected_packet = [
        #0     1     2     3     4     5     6     7     8     9
        0xaa, 0xb4, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        #10    11    12    13    14    15    16    17    18
        0x00, 0x00, 0x00, 0x00, 0x00, 0xa1, 0x60, 0x05, 0xab
    ]

    crafted_packet = crafter.query_pms(device_id=0xa160)

    assert expected_packet == crafted_packet
