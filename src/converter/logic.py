import pandas as pd
import io

class ConversionError(Exception):
    pass

def chirp_to_btech(csv_content: str):
    """Converts CHIRP CSV content to BTECH UV-Pro CSV format."""
    if csv_content is None:
        raise ConversionError("Input CSV content is None")
    if not csv_content.strip():
        return "", None

    try:
        df = pd.read_csv(io.StringIO(csv_content), sep=',', index_col=False)
        if df.empty:
            # If the CSV is just a header, return the header
            header = ','.join(df.columns)
            return header + '\n', None
    except pd.errors.EmptyDataError:
        # This happens if the CSV is completely empty (no header)
        return "", None
    except Exception as e:
        raise ConversionError(f"Failed to parse CHIRP CSV: {str(e)}")

    warning = None
    if len(df) > 30:
        df = df.head(30)
        warning = "More than 30 channels detected. Truncated to 30 channels for BTECH UV-Pro compatibility."

    btech_rows = []

    for _, row in df.iterrows():
        try:
            name = str(row.get('Name', ''))
            if name.strip() == '':
                name = 'Unknown'
            name = name.strip()

            freq_val = row.get('Frequency', 0.0)
            try:
                freq = float(freq_val)
            except (ValueError, TypeError):
                freq = 0.0

            duplex = str(row.get('Duplex', ''))

            offset_val = row.get('Offset', 0.0)
            try:
                offset = float(offset_val)
                if pd.isna(offset):
                    offset = 0.0
            except (ValueError, TypeError):
                offset = 0.0
            if isinstance(offset, str) and offset == '-':
                offset = 0.0

            if duplex == '-':
                tx_freq = freq - offset
            elif duplex == '+':
                tx_freq = freq + offset
            else:
                tx_freq = freq

            rx_freq_hz = int(round(freq * 1_000_000))
            tx_freq_hz = int(round(tx_freq * 1_000_000))

            mode = str(row.get('Mode', 'FM'))
            r_tone_val = row.get('rToneFreq', '')
            c_tone_val = row.get('cToneFreq', '')

            tx_sub = 0
            rx_sub = 0

            if pd.notna(r_tone_val) and str(r_tone_val).strip() != '':
                try:
                    tx_sub = int(round(float(r_tone_val) * 1000))
                except (ValueError, TypeError):
                    tx_sub = 0

            if pd.notna(c_tone_val) and str(c_tone_val).strip() != '':
                try:
                    rx_sub = int(round(float(c_tone_val) * 1000))
                except (ValueError, TypeError):
                    rx_sub = 0

            power_raw = str(row.get('Power', '4.0W')).replace('W', '')
            try:
                power_val = float(power_raw)
                tx_power = 'H' if power_val >= 4.0 else ('M' if power_val >= 2.0 else 'L')
            except Exception:
                tx_power = 'H'

            bw = 25000 if mode == 'NFM' else 12500

            btech_rows.append({
                'title': name,
                'tx_freq': tx_freq_hz,
                'rx_freq': rx_freq_hz,
                'tx_sub_audio(CTCSS=freq/DCS=number)': tx_sub,
                'rx_sub_audio(CTCS=freq/DCS=number)': rx_sub,
                'tx_power(H/M/L)': tx_power,
                'bandwidth(12500/25000)': bw,
                'scan(0=OFF/1=ON)': 1,
                'talk around(0=OFF/1=ON)': 0,
                'pre_de_emph_bypass(0=OFF/1=ON)': 0,
                'sign(0=OFF/1=ON)': 1,
                'tx_dis(0=OFF/1=ON)': 0,
                'mute(0=OFF/1=ON)': 0,
                'rx_modulation(0=FM/1=AM)': 0,
                'tx_modulation(0=FM/1=AM)': 0
            })

        except Exception:
            continue

    if not btech_rows:
        return "", None

    output_df = pd.DataFrame(btech_rows)
    output_csv = io.StringIO()
    output_df.to_csv(output_csv, index=False)

    return output_csv.getvalue(), warning

def btech_to_chirp(csv_content: str):
    """Converts BTECH UV-Pro CSV content to CHIRP CSV format."""
    if csv_content is None or not csv_content.strip():
        return "", None

    try:
        df = pd.read_csv(io.StringIO(csv_content), sep=',')
    except Exception as e:
        raise ConversionError(f"Failed to parse BATCH CSV: {e}")

    chirp_rows = []

    for _, row in df.iterrows():
        try:
            name = str(row.get('title', ''))
            rx_freq_hz = int(row.get('rx_freq', 0))
            tx_freq_hz = int(row.get('tx_freq', 0))

            rx_freq = rx_freq_hz / 1_000_000
            tx_freq = tx_freq_hz / 1_000_000

            if tx_freq > rx_freq:
                offset = float(round((tx_freq - rx_freq) * 1000000) / 1000000)
                duplex = '-'
            elif tx_freq < rx_freq:
                offset = float(round((rx_freq - tx_freq) * 1000000) / 1000000)
                duplex = '+'
            else:
                offset = 0.0
                duplex = ''

            tx_sub = int(row.get('tx_sub_audio(CTCSS=freq/DCS=number)', 0))
            rx_sub = int(row.get('rx_sub_audio(CTCS=freq/DCS=number)', 0))

            r_tone = (tx_sub / 1000.0) if tx_sub > 0 else ''
            c_tone = (rx_sub / 1000.0) if rx_sub > 0 else ''

            power_map = {'H': '4.0W', 'M': '2.5W', 'L': '1.0W'}
            p_val = str(row.get('tx_power(H/M/L)', 'H'))
            power = power_map.get(p_val, '4.0W')

            bw = int(row.get('bandwidth(12500/25000)', 25000))
            mode = 'NFM' if bw == 12500 else 'FM'

            chirp_rows.append({
                'Name': name,
                'Frequency': rx_freq,
                'Duplex': duplex,
                'Offset': offset,
                'Tone': 'Tone' if (r_fmt_fmt_exists(r_tone, tx_sub, rx_sub)) else '',
                'rToneFreq': r_tone,
                'cToneFreq': c_tone,
                'DtcsCode': '023',
                'DtcsPolarity': 'NN',
                'RxDtcsCode': '023',
                'CrossMode': 'Tone->Tone',
                'Mode': mode,
                'TStep': 5.0,
                'Skip': '',
                'Power': power,
                'Comment': '',
                'URCALL': '',
                'RPT1CALL': '',
                'RPT2CALL': '',
                'DVCODE': ''
            })
        except Exception:
            continue

    if not chirp_rows:
        return "", None

    output_df = pd.DataFrame(chirp_rows)
    output_df.insert(0, 'Location', range(1, len(output_df) + 1))

    output_csv = io.StringIO()
    output_df.to_csv(output_csv, index=False)

    return output_csv.getvalue(), None

def r_fmt_fmt_exists(r_tone, tx_sub, rx_sub):
    return r_tone != '' and (tx_sub > 0 or rx_sub > 0)
