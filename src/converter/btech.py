import pandas as pd
import io
from typing import List, Dict, Any
from .base import BaseParser, BaseGenerator
from .utils import (
    format_freq_to_hz,
    format_sub_audio_to_hz,
    format_freq_to_mhz,
    format_sub_audio_to_mhz,
    format_power_to_btech,
    normalize_power,
    format_number_to_str,
)

class BtechParser(BaseParser):
    def parse(self, content: str) -> List[Dict[str, Any]]:
        print(f"DEBUG: content repr: {repr(content)}")
        if not content:
            return []

        def is_true(val):
            try:
                return float(val) == 1.0
            except (ValueError, TypeError):
                return str(val).strip() == '1'

        # 1. Try to find the start of JSON content
        json_start = -1
        for char in ['{', '[']:
            idx = content.find(char)
            if idx != -1:
                if json_start == -1 or idx < json_start:
                    json_start = idx
        
        if json_start != -1:
            try:
                import json
                json_content = content[json_start:]
                # Check if it's valid JSON
                json.loads(json_content)
                content = json_content
            except (json.JSONDecodeError, ValueError):
                pass

        # 2. Try to find the start of CSV content
        for header in ['title,', 'Name,']:
            idx = content.find(header)
            if idx != -1:
                content = content[idx:]
                break

        try:
            if content.startswith('{') or content.startswith('['):
                import json
                data = json.loads(content)
                channels = []
                if isinstance(data, list):
                    # If it's a list of channels directly
                    for ch_data in data:
                        channels.append(self._parse_channel_append(ch_data))
                elif isinstance(data, dict):
                    # If it's a dict with 'chs' key
                    for ch_data in data.get('chs', []):
                        channels.append(self._parse_channel_append(ch_data))
                return channels
            
            df = pd.read_csv(io.StringIO(content))
            if df.empty:
                return []

            cols = df.columns.tolist()
            def find_col(keywords):
                for kw in keywords:
                    for col in cols:
                        if kw.lower() in col.lower():
                            return col
                return None

            col_map = {
                'name': find_col(['title', 'name', 'channel']),
                'tx_freq': find_col(['tx_freq', 'frequency', 'tx']),
                'rx_freq': find_col(['rx_freq', 'frequency', 'rx']),
                'tx_sub_audio': find_col(['tx_sub_audio', 'ctcss', 'dcs', 'rToneFreq']),
                'rx_sub_audio': find_col(['rx_sub_audio', 'ctcss', 'dcs', 'cToneF']),
                'tx_power': find_col(['tx_power', 'power']),
                'bandwidth': find_col(['bandwidth']),
                'scan': find_col(['scan']),
                'talk_around': find_col(['talk_around', 'ta']),
                'pre_de_emph_bypass': find_col(['pre_de_emph_bypass', 'pre_emphasis']),
                'sign': find_col(['sign']),
                'tx_dis': find_col(['tx_dis', 'transmit_disable']),
                'bclo': find_col(['bclo']),
                'mute': find_col(['mute']),
                'rx_mod': find_col(['rx_modulation', 'rx_mode']),
                'tx_mod': find_col(['tx_modulation', 'tx_mode']),
                'offset': find_col(['offset']),
                'duplex': find_col(['duplex']),
            }

            channels = []
            for _, row in df.iterrows():
                try:
                    ch = {}
                    ch['name'] = str(row[col_map['name']]) if col_map['name'] and not pd.isna(row[col_map['name']]) else ''
                    
                    tx_f = format_freq_to_hz(row[col_map['tx_freq']]) if col_map['tx_freq'] else 0
                    rx_f = format_freq_to_hz(row[col_map['rx_freq']]) if col_map['rx_freq'] else 0
                    
                    if col_map['offset'] and not pd.isna(row[col_map['offset']]):
                        offset_val = row[col_map['offset']]
                        offset_f = format_freq_to_hz(offset_val)
                        ch['offset_hz'] = float(offset_f)
                        if col_map['duplex'] and not pd.isna(row[col_map['duplex']]):
                            duplex = str(row[col_map['duplex']]).strip()
                            ch['duplex'] = duplex
                            if duplex == '-':
                                rx_f = tx_f - offset_f
                            elif duplex == '+':
                                rx_f = tx_f + offset_f
                        else:
                            rx_f = tx_f + offset_f
                    else:
                        ch['offset_hz'] = 0.0
                        ch['duplex'] = 'none'

                    if rx_f == 0:
                        rx_f = tx_f
                    ch['tx_freq_hz'] = float(tx_f)
                    ch['rx_freq_hz'] = float(rx_f)
                    ch['tx_sub_audio_hz'] = format_sub_audio_to_hz(row[col_map['tx_sub_audio']]) if col_map['tx_sub_audio'] and not pd.isna(row[col_map['tx_sub_audio']]) else 0
                    ch['rx_sub_audio_hz'] = format_sub_audio_to_hz(row[col_map['rx_sub_audio']]) if col_map['rx_sub_audio'] and not pd.isna(row[col_map['rx_sub_audio']]) else 0
                    
                    ch['tx_power'] = normalize_power(str(row[col_map['tx_power']])) if col_map['tx_power'] and not pd.isna(row[col_map['tx_power']]) else 'M'
                    
                    ch['bandwidth_hz'] = int(float(row[col_map['bandwidth']])) if col_map['bandwidth'] and not pd.isna(row[col_map['bandwidth']]) else 25000
                    
                    for flag in ['scan', 'talk_around', 'pre_de_emph_bypass', 'sign', 'tx_dis', 'bclo', 'mute']:
                        col = col_map.get(flag)
                        if col and not pd.isna(row[col]):
                            ch[flag] = is_true(row[col])
                        else:
                            ch[flag] = False

                    rx_mod = str(row[col_map['rx_mod']]) if col_map['rx_mod'] and not pd.isna(row[col_map['rx_mod']]) else 'FM'
                    ch['rx_modulation'] = 'AM' if rx_mod == '1' else 'FM'
                    
                    tx_mod = str(row[col_map['tx_mod']]) if col_map['tx_mod'] and not pd.isna(row[col_map['tx_mod']]) else 'FM'
                    ch['tx_modulation'] = 'AM' if tx_mod == '1' else 'FM'

                    channels.append(ch)
                except Exception as e:
                    print(f"Error parsing Btech row: {fmt_err(e)}")
                    continue
            return channels
        except Exception as e:
            print(f"Error parsing Btech CSV: {fmt_err(e)}")
            return []

    def _parse_channel_append(self, ch_data: Dict[str, Any]) -> Dict[str, Any]:
        ch = {}
        ch['name'] = ch_data.get('n', '')
        tx_f = format_freq_to_hz(ch_data.get('tf', ch_data.get('f', 0)))
        rx_f = format_freq_to_hz(ch_data.get('rf', ch_data.get('d', 0)))
        ch['tx_freq_hz'] = float(tx_f)
        ch['rx_freq_hz'] = float(rx_f)
        ch['tx_sub_audio_hz'] = format_sub_audio_to_hz(ch_data.get('ts', ch_data.get('t', 0)))
        if rx_f == 0:
            ch['rx_freq_hz'] = ch['tx_freq_hz']
            ch['rx_sub_audio_hz'] = ch['tx_sub_audio_hz']
        else:
            ch['rx_sub_audio_hz'] = format_sub_audio_to_hz(ch_data.get('dt', 0))
        
        def is_true(val):
            try:
                return float(val) == 1.0
            except (ValueError, TypeError):
                return str(val).strip() == '1'

        scan_val = ch_data.get('s')
        if scan_val is not None:
            ch['scan'] = is_true(scan_val)
        else:
            ch['scan'] = False
            
        ch['tx_power'] = normalize_power(ch_data.get('p', 'M')) if 'p' in ch_data else 'M'
        ch['bandwidth_hz'] = 25000
        ch['talk_around'] = False
        ch['pre_de_emph_bypass'] = False
        ch['sign'] = False
        ch['tx_dis'] = False
        ch['bclo'] = False
        ch['mute'] = False
        rx_mod = ch_data.get('m', 'FM')
        ch['rx_modulation'] = 'FM' if rx_mod == 'FM' else 'AM'
        ch['tx_modulation'] = 'FM' if rx_mod == 'FM' else 'AM'
        return ch

    def _parse_channel_dict(self, ch_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._parse_channel_append(ch_data)


def fmt_err(e):
    return str(e)

class BtechGenerator(BaseGenerator):
    def generate(self, channels: List[Dict[str, Any]]) -> str:
        if not channels:
            return ""

        header = "title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)"
        output = io.StringIO()
        output.write(header + "\n")

        for ch in channels[:30]:
            row = [
                ch.get('name', ''),
                format_number_to_str(format_freq_to_hz(ch.get('tx_freq_hz', 0))),
                format_number_to_str(format_freq_to_hz(ch.get('rx_freq_hz', 0))),
                format_number_to_str(format_sub_audio_to_hz(ch.get('tx_sub_audio_hz', 0))),
                format_number_to_str(format_sub_audio_to_hz(ch.get('rx_sub_audio_hz', 0))),
                format_power_to_btech(ch.get('tx_power', 'M')),
                format_number_to_str(ch.get('bandwidth_hz', 25000)),
                '1' if ch.get('scan', False) else '0',
                '1' if ch.get('talk_around', False) else '0',
                '1' if ch.get('pre_de_emph_bypass', False) else '0',
                '1' if ch.get('sign', False) else '0',
                '1' if ch.get('tx_dis', False) else '0',
                '1' if ch.get('bclo', False) else '0',
                '1' if ch.get('mute', False) else '0',
                '0' if ch.get('rx_modulation', 'FM') == 'FM' else '1',
                '0' if ch.get('tx_modulation', 'FM') == 'FM' else '1'
            ]
            output.write(",".join(row) + "\n")

        return output.getvalue().strip()

