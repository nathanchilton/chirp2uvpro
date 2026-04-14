import pandas as pd
import io
import json
import re

class ConversionError(Exception):
    pass

def format_freq_to_hz(freq_val):
    try:
        if pd.isna(freq_val):
            return 0
        f = float(freq_val)
        if f < 1000:
            f *= 1_000_000
        return int(f)
    except (ValueError, TypeError):
        return 0

def format_freq_to_mhz(freq_val):
    try:
        f = float(freq_val)
        if f < 1000:
            f /= 1_000_000
        return f
    except (ValueError, TypeError):
        return 0.0

def format_sub_audio_to_hz(sub_audio_val):
    try:
        if pd.isna(sub_audio_val):
            return 0
        v = float(sub_audio_val)
        if v < 1000:
            v *= 1000
        return int(v)
    except (ValueError, TypeError):
        return 0

def format_sub_audio_to_mhz(sub_audio_val):
    try:
        v = float(sub_audio_val)
        if v < 1000:
            v /= 1000
        return v
    except (ValueError, TypeError):
        return 0.0

def format_power_to_btech(p_str):
    if pd.isna(p_str) or str(p_str).lower() == 'nan':
        return ''
    p_map = {"H": "H", "M": "M", "L": "L", "4.0W": "H", "2.5W": "M", "1.0W": "L"}
    return p_map.get(p_str, p_str)

def format_power_to_chirp(p_str):
    if pd.isna(p_str) or str(p_str).lower() == 'nan':
        return ''
    p_map = {"H": "4.0W", "M": "2.5W", "L": "1.0W"}
    return p_map.get(p_str, p_str)

def clipboard_to_internal_wrapper(text_content: str) -> list:
    if not text_content or not text_content.strip():
        return []

    # Try to extract JSON part first
    try:
        match = re.search(r'\{"chs":.*\}', text_content)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            return data.get("chs", [])
    except Exception:
        pass

    # Fallback: Try CSV format
    try:
        df = pd.read_csv(io.StringIO(text_content), index_col=False)
        channels = []
        for _, row in df.iterrows():
            ch = {}
            for col in df.columns:
                val = str(row.get(col, ""))
                if val == "nan": val = ""
                
                # Normalizing column names to a
                if "title" in col: key = "n"
                elif "tx_freq" in col: key = "tx_f"
                elif "rx_freq" in col: key = "f"
                elif "tx_sub_audio" in col: key = "t"
                elif "rx_sub_audio" in col: key = "t"
                elif "tx_power" in col: key = "p"
                elif "bandwidth" in col: key = "tstep"
                elif "scan" in col: key = "s_scan"
                elif "talk around" in col: key = "s_ta"
                elif "pre_de_emph_bypass" in col: key = "s_ped"
                elif "sign" in col: key = "s_si"
                elif "tx_dis" in col: key = "s_td"
                elif "bclo" in col: key = "s_bc"
                elif "mute" in col: key = "s_mu"
                elif "rx_modulation" in col: key = "m_rx"
                elif "tx_modulation" in col: key = "m_tx"
                elif "Duplex" in col: key = "d"
                elif "Dtune" in col: key = "dt"
                else: key = col
                
                if key == "p":
                    val = format_power_to_btech(val)
                
                ch[key] = val
            channels.append(ch)
        return channels
    except Exception as e:
        print(f"Error parsing clipboard content: {str(e)}")
        return []

def internal_to_btech_csv(channels: list) -> str:
    if not channels:
        return ""

    header = "title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)"
    output = io.StringIO()
    output.write(header + "\n")

    for ch in channels:
        row = [
            ch.get('n', ''),
            str(format_freq_to_hz(ch.get('tx_f', ch.get('f', 0)))),
            str(format_freq_to_hz(ch.get('f', 0))),
            str(format_sub_audio_to_hz(ch.get('t', 0))),
            str(format_sub_audio_to_hz(ch.get('t', 0))),
            format_power_to_btech(ch.get('p', '')),
            str(int(float(ch.get('tstep', 25000)))),
            ch.get('s_scan', '0'),
            ch.get('s_ta', '0'),
            ch.get('s_ped', '0'),
            ch.get('s_si', '0'),
            ch.get('s_td', '0'),
            ch.get('s_bc', '0'),
            ch.get('s_mu', '0'),
            ch.get('m_rx', '0'),
            ch.get('m_tx', '0')
        ]
        output.write(",".join(row) + "\n")
    
    return output.getvalue().strip()

def chirp_to_btech(csv_content: str) -> tuple[str, str | None]:
    if csv_content is None:
        raise ConversionError("CSV content is None")
    if not csv_content:
        return "", None
    
    try:
        df = pd.read_csv(io.StringIO(csv_content), index_col=False)
        if df.empty:
            return "", None
        
        status_msg = None
        if len(df) > 30:
            df = df.head(30)
            status_msg = "Truncated"
            
        channels = []
        for _, row in df.iterrows():
            ch = {}
            ch['n'] = str(row.get('Name', ''))
            
            tx_f_val = row.get('Frequency', 0)
            tx_f = format_freq_to_hz(tx_f_val)
            
            duplex = str(row.get('Duplex', '-')).strip()
            offset_val = row.get('Offset', 0)
            offset = format_freq_to_hz(offset_val)
            
            if duplex == '-':
                rx_f = tx_f - offset
            elif duplex == '+':
                rx_f = tx_f + offset
            else:
                rx_f = tx_f
            
            ch['f'] = str(rx_f)
            ch['tx_f'] = str(tx_f)
            ch['d'] = duplex
            ch['do'] = str(offset)
            
            tone = str(row.get('Tone', ''))
            if tone in ['Tone', 'CTCSS']:
                r_tone = float(row.get('rToneFreq', 0))
                ch['t'] = str(format_sub_audio_to_hz(r_tone))
            else:
                ch['t'] = '0'
                
            ch['m'] = str(row.get('Mode', 'FM'))
            
            tstep = float(row.get('TStep', 25.0))
            ch['tstep'] = str(int(tstep * 1000))
            
            ch['p'] = format_power_to_btech(str(row.get('Power', '')))
            
            # Defaults
            ch['s_scan'] = '0'
            ch_s_ta = '0'
            ch['s_ped'] = '0'
            ch['s_si'] = '0'
            ch['s_td'] = '0'
            ch['s_bc'] = '0'
            ch['s_mu'] = '0'
            ch['m_rx'] = '0' if ch['m'] == 'FM' else '1'
            ch['m_tx'] = '0' if ch['m'] == 'FM' else '1'
            
            channels.append(ch)
            
        return internal_to_btech_csv(channels), status_msg
    except Exception as e:
        return "", str(e)


def btech_to_chirp(csv_content: str) -> tuple[str, str | None]:
    if not csv_content:
        return "", None
        
    try:
        df = pd.read_csv(io.StringIO(csv_content))
        if df.empty:
            return "", None

        rows = []
        for _, row in df.iterrows():
            ch_row = {}
            ch_row['Name'] = row.get('title', '')
            
            tx_f_val = row.get('tx_freq', 0)
            rx_f_val = row.get('rx_freq', 0)
            try:
                tx_f = float(tx_f_val)
                if pd.isna(tx_f): tx_f = 0.0
            except (ValueError, TypeError):
                tx_f = 0.0
            try:
                rx_f = float(rx_f_val)
                if pd.isna(rx_f): rx_f = 0.0
            except (ValueError, TypeError):
                rx_f = 0.0
            ch_row['Frequency'] = tx_f / 1_000_000 if tx_f >= 1_000_000 else tx_f
            
            if tx_f < rx_f:
                ch_row['Duplex'] = '-'
                ch_row['Offset'] = (rx_f - tx_f) / 1_000_000
            elif tx_f > rx_f:
                ch_row['Duplex'] = '+'
                ch_row['Offset'] = (tx_f - rx_f) / 1_000_000
            else:
                ch_row['Duplex'] = '-'
                ch_row['Offset'] = '0'
                
            sub_audio_val = row.get('tx_sub_audio(CTCSS=freq/DCS=number)', 0)
            try:
                sub_audio = float(sub_audio_val)
                if pd.isna(sub_audio): sub_audio = 0.0
            except (ValueError, TypeError):
                sub_audio = 0.0
            if sub_audio > 0:
                ch_row['Tone'] = 'Tone'
                ch_row['rToneFreq'] = sub_audio / 1000
            else:
                ch_row['Tone'] = 'None'
                ch_row['rToneFreq'] = '0'
                
            ch_row['Mode'] = 'FM' if row.get('rx_modulation(0=FM/1=AM)', '0') == '0' else 'NFM'
            tstep_val = row.get('bandwidth(12500/25000)', 25000)
            try:
                tstep_f = float(tstep_val)
                if pd.isna(tstep_f):
                    tstep_f = 25.0
            except (ValueError, TypeError):
                tstep_f = 25.0
            ch_row['TStep'] = tstep_f / 1000
            ch_row['Power'] = format_power_to_chirp(row.get('tx_power(H/M/L)', ''))
            
            # Add other columns if needed for CHIRP compatibility
            ch_row['DtcsCode'] = '023'
            ch_row['DtcsPolarity'] = 'NN'
            ch_row['RxDtcsCode'] = '023'
            ch_row['CrossMode'] = 'Tone->Tone'
            ch_row['Skip'] = '0'
            ch_row['Comment'] = ''
            ch_row['URCALL'] = ''
            ch_row['RPT1CALL'] = ''
            ch_row['RPT2CALL'] = ''
            ch_row['DVCODE'] = ''
            
            rows.append(ch_row)
            
        if not rows:
            return "", None
            
        output_df = pd.DataFrame(rows)
        # Reorder columns to match CHIRP
        chirp_cols = ['Location', 'Name', 'Frequency', 'Duplex', 'Offset', 'Tone', 'rToneFreq', 'cToneF', 'DtcsCode', 'DtcsPolarity', 'RxDtcsCode', 'CrossMode', 'Mode', 'TStep', 'Skip', 'Power', 'Comment', 'URCALL', 'RPT1CALL', 'RPT2CALL', 'DVCODE']
        # Ensure all columns exist
        for col in chirp_cols:
            if col not in output_df.columns:
                output_df[col] = ''
        
        # Filter to only CHIRP columns and reorder
        output_df = output_df[chirp_cols]
        # Note: 'Location' is missing in our construction, but it's in the test.
        # Let's add it.
        if 'Location' not in output_df.columns:
            output_df.insert(0, 'Location', range(len(output_df)))
        
        return output_df.to_csv(index=False), None
    except Exception as e:
        return "", str(e)

def internal_to_clipboard(channels: list) -> str:
    if not channels:
        return ""

    chs_data = {"chs": channels}
    json_str = json.dumps(chs_data)
    
    return f"BWE/BTECH JSON{json_str}"
