import pytest
import pandas as pd
import io
from src.converter.btech import BtechParser

def test_btech_duplex_inference_plus():
    # CSV with NaN duplex and an offset that should result in '+'
    # We use a comma for the empty column to create NaN in pandas
    # Columns: name,tx_freq,rx_freq,duplex,offset
    csv_content = "name,tx_freq,rx_freq,duplex,offset\n" \
                  "Test Plus,462.550,463.150,,0.600"
    
    parser = BtechParser()
    channels = parser.parse(csv_content)
    
    assert len(channels) == 1
    assert channels[0]['duplex'] == '+'
    assert channels[0]['rx_freq_hz'] == 463150000.0

def test_btech_duplex_inference_minus():
    # CSV with NaN duplex and an or offset that should result in '-'
    csv_content = "name,tx_freq,rx_freq,duplex,offset\n" \
                  "Test Minus,462.550,461.950,,0.600"
    
    parser = BtechParser()
    channels = parser.parse(csv_content)
    
    assert len(channels) == 1
    assert channels[0]['duplex'] == '-'
    assert channels[0]['rx_freq_hz'] == 461950000.0

def test_btech_duplex_inference_none():
    # CSV with NaN duplex and no difference between rx and tx
    csv_content = "name,tx_freq,rx_freq,duplex,offset\n" \
                  "Test None,462.550,462.550,,0.600"
    
    parser = BtechParser()
    channels = parser.parse(csv_content)
    
    assert len(channels) == 1
    assert channels[0]['duplex'] == 'none'
    assert channels[0]['rx_freq_hz'] == 462550000.0

def test_btech_duplex_explicit_plus():
    # CSV with explicit '+' duplex
    csv_content = "name,tx_freq,rx_freq,duplex,offset\n" \
                  "Test Explicit Plus,462.550,463.150,+,0.600"
    
    parser = BtechParser()
    channels = parser.parse(csv_content)
    
    assert len(channels) == 1
    assert channels[0]['duplex'] == '+'
    assert channels[0]['rx_freq_hz'] == 463150000.0

def test_btech_duplex_explicit_minus():
    # CSV with explicit '-' duplex
    csv_content = "name,tx_freq,rx_freq,duplex,offset\n" \
                  "Test Explicit Minus,462.550,461.950,-,0.600"
    
    parser = BtechParser()
    channels = parser.parse(csv_content)
    
    assert len(channels) == 1
    assert channels[0]['duplex'] == '-'
    assert channels[0]['rx_freq_hz'] == 461950000.0
