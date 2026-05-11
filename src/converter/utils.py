import pandas as pd

def is_true(val):
    """Checks if a value represents True."""
    try:
        return float(val) == 1.0
    except (ValueError, TypeError):
        return str(val).strip() == '1'

def format_number_to_str(val, precision=None):
    """Converts a number to a string, removing .0 if it is an integer."""
    try:
        f = float(val)
        if precision is not None:
            return f"{f:.{precision}f}"
        if f.is_integer():
            return f"{int(f)}"
        else:
            return f"{f}"
    except (ValueError, TypeError):
        return str(val)

def format_freq_to_hz(freq_val, scale='MHz'):
    """Converts frequency to Hz based on provided scale."""
    try:
        if pd.isna(freq_val):
            return 0.0
        f = float(freq_val)
        if f == 0:
            return 0.0
        
        if isinstance(scale, (int, float)):
            multiplier = scale
        elif scale == 'MHz':
            multiplier = 1_000_000
        elif scale == 'kHz':
            multiplier = 1_000
        elif scale == 'Hz':
            multiplier = 1
        else:
            raise ValueError(f"Unknown scale: {scale}")
            
        return round(f * multiplier, 3)
    except (ValueError, TypeError):
        return 0.0

def format_sub_audio_to_hz(sub_audio_val, scale='Hz'):
    """Converts sub-audio frequency to Hz based on provided scale."""
    try:
        if pd.isna(sub_audio_val):
            return 0.0
        f = float(sub_audio_val)
        if f == 0:
            return 0.0
        
        if isinstance(scale, (int, float)):
            multiplier = scale
        elif scale == 'MHz':
            multiplier = 1_000_000
        elif scale == 'kHz':
            multiplier = 1_000
        elif scale == 'Hz':
            multiplier = 1
        elif scale == '0.1Hz':
            multiplier = 0.1
        elif scale == '0.01Hz':
            multiplier = 0.01
        else:
            raise ValueError(f"Unknown scale: {scale}")
            
        return round(f * multiplier, 3)
    except (ValueError, TypeError):
        return 0.0

def format_sub_audio_to_units(sub_audio_hz, unit_scale='0.01Hz'):
    """Converts sub-audio frequency in Hz to units (e.g., 0.01Hz units)."""
    try:
        if pd.isna(sub_audio_hz):
            return 0.0
        f = float(sub_audio_hz)
        if f == 0:
            return 0.0
        
        if isinstance(unit_scale, (int, float)):
            multiplier = unit_scale
        elif unit_scale == 'MHz':
            multiplier = 1_000_000
        elif unit_scale == 'kHz':
            multiplier = 1_000
        elif unit_scale == 'Hz':
            multiplier = 1
        elif unit_scale == '0.1Hz':
            multiplier = 0.1
        elif unit_scale == '0.01Hz':
            multiplier = 0.01
        else:
            raise ValueError(f"Unknown unit scale: {unit_scale}")
            
        return int(round(f / multiplier))
    except (ValueError, TypeError):
        return 0.0

def format_freq_to_mhz(freq_val, scale='Hz'):
    """Converts frequency to MHz based on provided scale."""
    return format_freq_to_hz(freq_val, scale=scale) / 1_000_000

def format_sub_audio_to_mhz(sub_audio_val, scale='Hz'):
    """Converts sub-audio frequency to MHz based on provided scale."""
    return format_sub_audio_to_hz(sub_audio_val, scale=scale) / 1_000_000

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

def format_power_to_btech(p_str):
    """Converts power string (H, M, L, 4.0W, etc.) to Btech format (H, M, L)."""
    if pd.isna(p_str) or str(p_str).lower() == 'far' or str(p_str).strip() == '':
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

def calculate_rx_freq_and_duplex(tx_freq_hz: float, offset_hz: float, duplex: str, rx_freq_hz: float = 0.0) -> tuple[float, str]:
    """Calculates rx_freq_rad and duplex based on tx_freq_hz, offset_hz, and duplex string."""
    duplex = str(duplex).lower().strip()
    if duplex == '-':
        return tx_freq_hz - offset_hz, '-'
    elif duplex == '+':
        return tx_freq_hz + offset_hz, '+'
    elif duplex == 'none' or duplex == '':
        if offset_hz != 0:
            if offset_hz > 0:
                return tx_freq_hz + offset_hz, '+'
            else:
                return tx_freq_hz + offset_hz, '-'
        if rx_freq_hz > 0 and rx_freq_hz != tx_freq_hz:
            if rx_freq_hz > tx_freq_hz:
                return rx_freq_hz, '+'
            else:
                return rx_freq_hz, '-'
        return tx_freq_hz, 'none'
    else:
        # Inference
        if rx_freq_hz > 0:
            if rx_freq_hz > tx_freq_hz:
                return rx_freq_hz, '+'
            elif rx_freq_hz < tx_freq_hz:
                return rx_freq_hz, '-'
        return tx_freq_hz, 'none'
