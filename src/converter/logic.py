import pandas as pd
import io
import json
import re

class ConversionError(Exception):
    pass

def clipboard_to_internal(text_content: str):
    """
    Parses the BTECH Clipboard Sharing Format text into an internal list of channel dictionaries.
    Format: Copy this text and start BWE/B1TECH JSON{"chs":[...]}
    Also supports fallback to CSV format.
    """
    if not text_content or not text_content.strip():
        return None

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
        
        # Map BTECH CSV columns to internal keys
        column_mapping = {
            "title": "n",
            "tx_freq": "tx_f",
            "rx_freq": "f",
            "tx_sub_audio(CTCSS=freq/DCS=number)": "t",
            "rx_sub_audio(CTCS=freq/DCS=number)": "t",
            "tx_power(H/M/L)": "p",
            "bandwidth(12500/25000)": "tstep",
            "scan(0=OFF/1=ON)": "s",
            "talk around(0=OFF/1=ON)": "s",
            "pre_de_emph_bypass(0=OFF/1=ON)": "s",
            "sign(0=OFF/1=ON)": "s",
            "tx_dis(0=OFF/1=ON)": "s",
            "mute(0=OFF/1=ON)": "s",
            "rx_modulation(0=FM/1=AM)": "m",
            "tx_modulation(0=FM/1=AM)": "m",
            "Duplex": "d",
            "Dtune": "dt"
        }
        
        channels = []
        for _, row in df.iterrows():
            channel = {}
            for col in df.columns:
                val = str(row.get(col, ""))
                if val == "nan": val = ""
                
                mapped_col = column_mapping.get(col, col)
                
                if mapped_col == "n": channel["n"] = val
                elif mapped_col == "f": channel["f"] = val
                elif mapped_col == "tx_f": channel["tx_f"] = val
                elif mapped_col == "t": channel["t"] = val
                elif mapped_col == "dt": channel["dt"] = val
                elif mapped_col == "s": channel["s"] = val
                elif mapped_col == "p":
                    power_map = {"H": "4.0W", "M": "2.5W", "L": "1.0W"}
                    channel["p"] = power_map.get(val, val)
                elif mapped_col == "m": channel["m"] = val
                elif mapped_col == "tstep": channel["tstep"] = val
                elif mapped_col == "d": channel["d"] = val
                else:
                    # For any other column, just add it to the channel
                    channel[mapped_col] = val
            
            if channel:
                channels.append(channel)
        return channels
    except Exception as e:
        print(f"Error parsing clipboard content: {e}")
        return None

def internal_to_clipboard(channels: list) -> str:
    """
    Converts the internal list of channel dictionaries into the Bint_BTECH Clipboard Sharing Format text.
    """
    if not channels:
        return ""

    # Create the JSON part
    chs_data = {"chs": channels}
    json_str = json.dumps(chs_data)
    
    return f"BWE/BTECH JSON{json_str}"

def chirp_to_btech(csv_content: str) -> tuple[str, str]:
    """
    Converts Chirp CSV content to BTECH Clipboard Sharing Format.
    Returns (output_format, warning)
    """
    if csv_content is None:
        raise ConversionError("CSV content is None")
    if not csv_content.strip():
        return "", None

    try:
        df = pd.read_csv(io.StringIO(csv_content), index_col=False)
        
        # Map columns if necessary (assuming standard Chirps CSV columns)
        channels = []
        for _, row in df.iterrows():
            freq = row.get("Frequency", "0")
            try:
                freq_val = float(freq)
                if freq_val < 1000:
                    freq_val *= 1_000_000
                freq = f"{int(freq_val)}"
            except ValueError:
                pass

            # Handle Duplex and Offset
            duplex = str(row.get("Duplex", ""))
            offset = row.get("Offset", "0")
            tx_f = None
            try:
                offset_val = float(offset)
                if offset_val < 1000:
                    offset_val *= 1_000_000
                if duplex == "-" or duplex == "+":
                    tx_f = freq_val - offset_val if duplex == "-" else freq_val + offset_val
                    tx_f = f"{int(tx_f)}"
            except ValueError:
                pass

            channel = {
                "n": str(row.get("Name", "")),
                "f": freq,
                "d": duplex,
                "tx_f": tx_f,
                "t": str(row.get("Tone", "")),
                "dt": str(row.get("Dtune", "")),
                "s": str(row.get("Power", "")), # For compatibility with existing tests
                "p": str(row.get("Power", "")),
                "m": str(row.get("mode", "")), # Handle lowercase mode if present
                "tstep": str(row.get("TStep", "")),
            }
            # Handle case where Mode might be in 'Mode' instead of 'mode'
            if not channel["m"]:
                channel["m"] = str(row.get("Mode", ""))

            # Cleanup: Remove None values
            channel = {k: v for k, v in channel.items() if v is not None}
            channels.append(channel)
        
        warning = None
        if len(channels) > 30:
            channels = channels[:30]
            warning = "Truncated: Too many channels in Chirps CSV."

        return internal_to_clipboard(channels), warning
    except Exception as e:
        raise ConversionError(f"Error converting Chirp to BTECH: {e}")

def btech_to_chirp(clipboard_content: str) -> tuple[str, str]:
    """
    Converts BTECH Clipboard Sharing Format text back to Chirp CSV content.
    Returns (output_format, warning)
    """
    try:
        channels = clipboard_to_internal(clipboard_content)
        if not channels:
            raise ConversionError("No valid channels found in clipboard content.")

        output = io.StringIO()
        output.write("Channel,Name,Frequency,Duplex,Tone,Dtune,Skip,Power,Offset,Mode\n")
        
        for i, ch in enumerate(channels, 1):
            freq = ch.get('f', '')
            tx_f = ch.get('tx_f', '')
            duplex = ch.get('d', '')
            offset = "0"
            
            if tx_f and tx_f != freq:
                try:
                    f_val = float(freq)
                    tf_val = float(tx_f)
                    if tf_val < f_val:
                        duplex = "-"
                    else:
                        duplex = ""
                    
                    # Calculate offset in MHz for the CSV
                    offset_val = abs(tf_val - f_val)
                    if offset_val >= 1000: # Changed from 1,000,000 to 1000
                        offset = f"{offset_val / 1_000_000:g}"
                    else:
                        offset = f"{offset_val}"
                except ValueError:
                    pass
            
            try:
                freq_val = float(freq)
                if freq_val >= 1_000_000:
                    freq = f"{freq_val / 1_000_000:g}"
            except ValueError:
                pass
            
            output.write(f"{i},{ch.get('n','')},{freq},{duplex},{ch.get('t','')},{ch.get('dt','')},{ch.get('s','')},{ch.get('p','')},{offset},{ch.get('m','')}\n")
            
        return output.getvalue(), None
    except Exception as e:
        raise ConversionError(f"Error converting BTECH to Chirp: {e}")

def clipboard_to_internal_wrapper(text_content: str) -> tuple[list, str]:
    """
    Wrapper for the routes to match the expected signature (channels, warning)
    """
    channels = clipboard_to_internal(text_content)
    if channels is None:
        raise ConversionError("Invalid clipboard format")
    return channels, None
