import json
from typing import List, Dict, Any
from ..base import BaseParser
from ..models import Channel
from ..utils import format_freq_to_hz, format_sub_audio_to_hz

class ApiImportParser(BaseParser):
    """
    Parses the 'api-import' JSON format into Internal Channel models.
    Format: { "repeaters": [ { "n": "Name", "rf": 147.88, "tf": 147.88, "ts": 100.0, "rs": 100.0 }, ... ] }
    """
    def parse(self, content: str) -> List[Channel]:
        if not content:
            return []

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return []

        repeaters_data = data.get('repeaters', [])
        if not isinstance(repeaters_data, list):
            return []

        channels = []
        for item in repeaters_data:
            try:
                ch = Channel()
                ch.name = item.get('n', '')
                
                # Frequencies are in MHz in the API format
                rf_mhz = item['rf']
                tf_mhz = item['tf']
                
                ch.rx_freq_hz = format_freq_to_hz(rf_mhz, scale='MHz')
                ch.tx_freq_hz = format_freq_to_hz(tf_mhz, scale='MHz')
                
                # Sub-audio are in Hz in the API format
                ts_hz = item.get('ts', 0.0)
                rs_hz = item.get('rs', 0.0)
                
                ch.tx_sub_audio_hz = float(format_sub_audio_to_hz(ts_hz, scale='Hz'))
                ch.rx_sub_audio_hz = float(format_sub_audio_to_hz(rs_hz, scale='Hz'))
                
                # If RX freq equals TX freq, assume no duplex
                if ch.rx_freq_hz == ch.tx_freq_hz:
                    ch.duplex = 'none'
                    ch.offset_hz = 0.0
                else:
                    # This parser assumes the API provides the absolutely frequencies.
                    # If they differ, we must determine the duplex and offset.
                    # However, the specification says rf and tf are provided.
                    # We'll infer the duplex based on the difference.
                    diff = abs(ch.tx_freq_hz - ch.rx_freq_hz)
                    ch.offset_hz = diff
                    if ch.rx_freq_hz > ch.tx_freq_hz:
                        ch.duplex = '+'
                    else:
                        ch.duplex = '-'

                # Default values for other fields
                ch.bandwidth_hz = 25000
                ch.tx_power = 'M'
                ch.rx_modulation = 'FM'
                ch.tx_modulation = 'FM'
                ch.scan = False
                ch.talk_around = False
                ch.pre_de_emph_bypass = False
                ch.sign = False
                ch.tx_dis = False
                ch.bclo = False
                ch.mute = False

                channels.append(ch)
            except Exception:
                continue

        return channels
