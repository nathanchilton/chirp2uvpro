import pandas as pd

def is_true(val):
    """Checks if a value represents True."""
    try:
        return float(val) == 1.0
    except (ValueError, TypeError):
        return str(val).strip() == '1'

def format_number_to_str(val):
    """Converts a number to a string, removing .0 if it is an integer."""
    try:
        f = float(val)
        if f.is_integer():
            return f"{int(f)}"
        else:
            return f"{f}"
    except (ValueError, TypeError):
        return str(val)

def format_freq_to_hz(freq_val):
    """Converts frequency to Hz. If value < 3000, assumes MHz. If < 3000000, assumes kHz. Otherwise assumes Hz."""
    try:
        if pd.isna(freq_val):
            return 0
        f = float(freq_val)
        if f < 3000: # Assumes MHz
            return round(f * 1_000_000, 3)
        elif f < 3000000: # Assumes kHz
            return round(f * 1000, 3)
        else: # Assumes Hz
            return round(f, 3)
    except (ValueError, TypeError):
        return 0

def format_sub_audio_to_hz(sub_audio_val):
    """Converts sub-audio frequency to Hz. If value < 0.001, assumes MHz. If < 1, assumes kHz. Otherwise assumes Hz."""
    try:
        if pd.isna(sub_audio_val):
            return 0
        v = float(sub_audio_val)
        print(f"DEBUG: format_sub_audio_to_hz called with v={v}")
        if v <= 0.001: # Assumes MHz
            return round(v * 1_000_000, 3)
        elif v < 1: # Assumes kHz
            return round(v * 1000, 3)
        else: # Assumes Hz
            return round(v, 3)
    except (ValueError, TypeError):
        return 0

def format_freq_to_mhz(freq_val):
    """Converts frequency to MHz."""
    try:
        if pd.isna(freq_val):
            return 0.0
        f = float(freq_val)
        f /= 1_000_000
        return f
    except (ValueError, TypeError):
        return 0.0

def format_sub_audio_to_mhz(sub_audio_val):
    """Converts sub-audio frequency to MHz."""
    try:
        if pd.isna(sub_audio_val):
            return 0.0
        v = float(sub_audio_val)
        v /= 1_000_000
        return v
    except (ValueError, TypeError):
        return 0.0

def normalize_power(p_str):
    """Normalizes power string to 'H', 'M', or 'L'."""
    if pd.isna(p_str) or str(p_str).lower() == 'nan':
        return 'M'
    p_str = str(p_str).upper()
    if p_str in ['H', '4.0W']:
        return 'H'
    if p_str in ['M', '2.5W']:
        return 'M'
    if p_str in ['L', '1.0W']:
        return 'L'
    return p_str
    p_str = str(p_str).upper()
    if p_str in ['H', '4.0W']:
        return 'H'
    if p_str in ['M', '2.5W']:
        return 'M'
    if p_str in ['L', '1.0W']:
        return 'L'
    return 'M'

def format_power_to_btech(p_str):
    """Converts power string (H, M, L, 4.0W, etc.) to Btech format (H, M, L)."""
    if pd.isna(p_str) or str(p_str).lower() == 'nan' or str(p_str).strip() == '':
        return ''
    p_str = str(p_str).upper()
    p_map = {"H": "H", "M": "M", "L": "L", "4.0W": "H", "2.5W": "M", "1.0W": "L"}
    return p_map.get(p_str, p_str)

def format_power_to_chirp(p_str):
    """Converts power string (H, M, L, 4.0W, etc.) to Chirp format (4.0W, 2.5W, 1.0W)."""
    if pd.isna(p_str) or str(p_str).lower() == 'nan' or str(p_str).strip() == '':
        return ''
    p_str = str(p_str).upper()
    p_map = {"H": "4.0W", "M": "2.5W", "L": "1.0W", "4.0W": "4.0W", "2.5W": "2.5W", "1.0W": "1.0W"}
    return p_map.get(p_str, p_str)
