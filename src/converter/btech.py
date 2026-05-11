import pandas as pd
import io
import json
from typing import List, Dict, Any
from .base import BaseParser, BaseGenerator
from .models import Channel
from .utils import (
    format_freq_to_hz,
    format_sub_audio_to_hz,
    format_freq_to_mhz,
    format_sub_audio_to_units,
    format_power_to_btech,
    normalize_power,
    format_number_to_str,
    is_true,
    calculate_rx_freq_and_duplex,
)

class BtechParser(BaseParser):
    def parse(self, content: str | tuple[str, str | None]) -> List[Channel]:
        is_btech_uv_format = False
        if isinstance(content, tuple):
            content = content[0]
        if not content:
            return []
 
        # 1. Check for known prefixes and set freq_scale
        freq_scale = 'Hz'
        prefixes = [
            ("Copy this text and start BTECH UV", 'MHz'),
            ("BWE/BTECH JSON", 'MHz'),
            ("BTECH UV", 'Hz'),
        ]
        for prefix, scale in prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):].lstrip()
                freq_scale = scale
                if prefix == "BTECH UV":
                    is_btech_uv_format = True
                break


        # 2. Try to find the start of JSON content
        json_start = -1
        for char in ['{', '[']:
            idx = content.find(char)
            if idx != -1:
                if json_start == -1 or idx < json_start:
                    json_start = idx
        
        if json_start != -1:
            try:
                json_content = content[json_start:]
                # Check if it's valid JSON
                json.loads(json_content)
                content = json_content
            except (json.JSONDecodeError, ValueError):
                pass

        # 3. Try to parse as JSON or CSV
        try:
            if content.strip().startswith('{') or content.strip().startswith('['):
                data = json.loads(content)
                channels = []
                if isinstance(data, list):
                    for ch_data in data:
                        channels.append(self._parse_channel_append(ch_data, freq_scale='MHz', sub_audio_scale='Hz'))
                elif isinstance(data, dict):
                    for ch_data in data.get('chs', []):
                        channels.append(self._parse_channel_append(ch_data, freq_scale='MHz', sub_audio_scale='Hz'))
                return channels
            
            df = pd.read_csv(io.StringIO(content))
            if df.empty:
                return []
 
            cols = df.columns.tolist()
            if 'Frequency' in cols:
                freq_scale = 'MHz'


            def find_col(keywords):
                for kw in keywords:
                    for col in cols:
                        if kw.lower() in col.lower():
                            return col
                return None

            col_map = {
                'name': find_col(['title', 'name', 'channel']),
                'location': find_col(['location', 'loc']),
                'skip': find_col(['skip']),
                'tx_freq': find_col(['tx_freq', 'frequency', 'tx']),
                'rx_freq': find_col(['rx_freq', 'frequency', 'rx']),
                'tx_sub_audio': find_col(['tx_sub_audio', 'ctcss', 'dcs', 'rToneFreq']),
                'rx_sub_audio': find_col(['rx_sub_audio', 'ctcss', 'dcs', 'cToneF', 'cToneFreq']),
                'tx_power': find_col(['tx_power', 'pad', 'power']),
                'bandwidth': find_col(['bandwidth', 'TStep']),
                'scan': find_col(['scan']),
                'talk_around': find_col(['t_around', 'ta']),
                'pre_de_emph_bypass': find_col(['pre_de_emph_bypass', 'pre_emphasis', 'pre_de_ph_bypass']),
                'sign': find_col(['sign']),
                'tx_dis': find_col(['tx_dis', 'transmit_disable']),
                'bclo': find_col(['bclo']),
                'mute': find_col(['mute']),
                'rx_mod': find_col(['rx_modulation', 'rx_mode', 'Mode']),
                'tx_mod': find_col(['tx_modulation', 'tx_mode', 'Mode']),
                'offset': find_col(['offset', 'Offset']),
                'duplex': find_col(['duplex', 'Duplex']),
            }

            channels = []
            for _, row in df.iterrows():
                try:
                    ch = Channel()
                    ch.name = str(row[col_map['name']]) if col_map['name'] and not pd.isna(row[col_map['name']]) else ''
                    ch.location = str(row[col_map['location']]) if col_map['location'] and not pd.isna(row[col_map['location']]) else ''
                    ch.skip = is_true(row[col_map['skip']]) if col_map['skip'] and not pd.isna(row[col_map['skip']]) else False

                    tx_f_val_raw = row[col_map['tx_freq']] if col_map['tx_freq'] and not pd.isna(row[col_map['tx_freq']]) else 0.0
                    tx_f_val = float(tx_f_val_raw) if isinstance(tx_f_val_raw, (int, float)) else float(str(tx_f_val_raw).replace('_', ''))
                    ch.tx_freq_hz = float(format_freq_to_hz(tx_f_val, scale=freq_scale))

                    rx_f_val_raw = row[col_map['rx_freq']] if col_map['rx_freq'] and not pd.isna(row[col_map['rx_freq']]) else 0.0
                    rx_f_val = float(rx_f_val_raw) if isinstance(rx_f_val_raw, (int, float)) else float(str(rx_f_val_raw).replace('_', ''))
                    ch.rx_freq_hz = float(format_freq_to_hz(rx_f_val, scale=freq_scale)) if rx_f_val > 0 else 0.0

                    offset_val_raw = row[col_map['offset']] if col_map['offset'] and not pd.isna(row[col_map['offset']]) else 0.0
                    offset_val = float(offset_val_raw) if isinstance(offset_val_raw, (int, float)) else float(str(offset_val_raw).replace('_', ''))
                    ch.offset_hz = float(format_freq_to_hz(offset_val, scale=freq_scale))
                    duplex_val = str(row[col_map['duplex']]) if col_map['duplex'] and not pd.isna(row[col_map['duplex']]) else 'F'
                    ch.rx_freq_hz, ch.duplex = calculate_rx_freq_and_duplex(
                        ch.tx_freq_hz, 
                        ch.offset_hz, 
                        duplex_val, 
                        rx_freq_hz=ch.rx_freq_hz
                    )


                    # Sub-audio (CTCSS/DCS)
                    for side in ['tx', 'rx']:
                        col_key = f'{side}_sub_audio'
                        raw_val = row[col_map[col_key]] if col_map[col_key] and not pd.isna(row[col_map[col_key]]) else 0.0
                        val = float(raw_val) if isinstance(raw_val, (int, float)) else float(str(raw_val).replace('_', ''))
                        hz = 0.0
                        if is_btech_uv_format and val >= 1000:
                            hz = val / 100.0
                        elif val > 0:
                            if val < 1000:
                                ch.extra_fields[f'{side}_dcs_code'] = format_number_to_str(val, precision=0)
                            else:
                                hz = val
                        
                        if side == 'tx':
                            ch.tx_sub_audio_hz = hz
                        else:
                            ch.rx_sub_audio_hz = hz
                        
                        if side == 'rx' and (pd.isna(row[col_map['rx_freq']]) or rx_f_val_raw == 0):
                            ch.rx_sub_audio_hz = ch.tx_sub_audio_hz


                    
                    ch.tx_power = normalize_power(str(row[col_map['tx_power']])) if col_map['tx_power'] and not pd.isna(row[col_map['tx_power']]) else 'M'
                    ch.bandwidth_hz = int(float(row[col_map['bandwidth']])) if col_map['bandwidth'] and not pd.isna(row[col_map['bandwidth']]) else 25000

                    for flag in ['scan', 'talk_around', 'pre_de_emph_bypass', 'sign', 'tx_dis', 'bclo', 'mute']:
                        col_name = col_map.get(flag)
                        if col_name and col_name in row and not pd.isna(row[col_name]):
                            setattr(ch, flag, is_true(row[col_name]))
                        else:
                            setattr(ch, flag, False)
                            
                    rx_mod = str(row[col_map['rx_mod']]) if col_map['rx_mod'] and not pd.isna(row[col_map['rx_mod']]) else 'FM'
                    ch.rx_modulation = 'AM' if rx_mod == 'AM' or rx_mod == '1' else 'FM'
                    
                    tx_mod = str(row[col_map['tx_mod']]) if col_map['tx_mod'] and not pd.isna(row[col_map['tx_mod']]) else 'FM'
                    ch.tx_modulation = 'FM' if tx_mod == 'FM' else 'AM'
                    
                    ch.location = str(row[col_map['location']]) if col_map['location'] and not pd.isna(row[col_map['location']]) else ''
                    ch.skip = is_true(row[col_map['skip']]) if col_map['skip'] and not pd.isna(row[col_map['skip']]) else False

                    channels.append(ch)
                except Exception as e:
                    print(f"Error parsing Btech row: {e}")
                    continue
            return channels
        except Exception as e:
            print(f"Error parsing Btest CSV: {e}")
            return []

    def _parse_channel_append(self, ch_data: Dict[str, Any], freq_scale: str = 'MHz', sub_audio_scale: str = 'Hz') -> Channel:
        ch = Channel()
        ch.name = ch_data.get('n', '')
        tx_f_val = ch_data.get('tf', ch_data.get('f', 0))
        rx_f_val = ch_data.get('rf', ch_data.get('d', 0))
        ch.tx_freq_hz = float(format_freq_to_hz(tx_f_val, scale=freq_scale))
        ch.rx_freq_hz = float(format_freq_to_hz(rx_f_val, scale=freq_scale))
        ch.tx_sub_audio_hz = float(format_sub_audio_to_hz(ch_data.get('ts', ch_data.get('t', 0)), scale=sub_audio_scale))
        if ch.rx_freq_hz == 0:
            ch.rx_freq_hz = ch.tx_freq_hz
            ch.rx_sub_audio_hz = ch.tx_sub_audio_hz
        else:
            ch.rx_sub_audio_hz = float(format_sub_audio_to_hz(ch_data.get('dt', 0), scale=sub_audio_scale))
        
        scan_val = ch_data.get('s')
        ch.scan = is_true(scan_val) if scan_val is not None else False
            
        ch.tx_power = normalize_power(ch_data.get('p', 'M')) if 'p' in ch_data else 'M'
        ch.bandwidth_hz = 25000
        ch.talk_around = False
        ch.pre_de_emph_bypass = False
        ch.sign = False
        ch.tx_dis = False
        ch.bclo = False
        ch.mute = False
        rx_mod = ch_data.get('m', 'FM')
        ch.rx_modulation = 'FM' if rx_mod == 'FM' else 'AM'
        ch.tx_modulation = 'FM' if rx_mod == 'FM' else 'AM'
        return ch

class BtechGenerator(BaseGenerator):
    def generate(self, channels: List[Channel]) -> tuple[str, str | None]:
        if not channels:
            return "", None

        status_msg = None
        if len(channels) > 30:
            channels = channels[:30]
            status_msg = "Truncated"

        header = (
            "title,location,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),"
            "rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),"
            "bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),"
            "pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),"
            "bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)"
        )
        output = io.StringIO()
        output.write(header + "\n")

        for ch in channels:
            row = [
                ch.name,
                ch.location,
                format_number_to_str(ch.tx_freq_hz),
                format_number_to_str(ch.rx_freq_hz),
                (str(int(ch.tx_sub_audio_hz)) if ch.tx_sub_audio_hz > 0 else ch.extra_fields.get('tx_dcs_code', '0')),
                (str(int(ch.rx_sub_audio_hz)) if ch.rx_sub_audio_hz > 0 else ch.extra_fields.get('rx_dcs_code', '0')),
                format_power_to_btech(ch.tx_power),
                format_number_to_str(ch.bandwidth_hz),
                '1' if ch.scan else '0',
                '1' if ch.talk_around else '0',
                '1' if ch.pre_de_emph_bypass else '0',
                '1' if ch.sign else '0',
                '1' if ch.tx_dis else '0',
                '1' if ch.bclo else '0',
                '1' if ch.mute else '0',
                'FM' if ch.rx_modulation == 'FM' else 'AM',
                'FM' if ch.tx_modulation == 'FM' else 'AM'
            ]
            output.write(",".join(map(str, row)) + "\n")


        return output.getvalue().strip(), status_msg

