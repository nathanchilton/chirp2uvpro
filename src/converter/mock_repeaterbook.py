import random

def get_mock_repeaters(lat, lon):
    """
    Returns a list of 30 simulated repeater objects based on a given location.
    Each repeater has a name and a frequency.
    """
    repeaters = []
    # Use the lat/lon to seed the random generator so it's somewhat deterministic for a location
    seed = hash((lat, lon))
    random.seed(seed)

    for i in range(30):
        # Generate a plausible frequency (e.g., between 144.0 and 148.0 MHz)
        frequency = round(random.uniform(144.0, 148.0), 4)
        
        # Generate a plausible sub-audio (CTCSS) frequency (e.g., between 67.0 and 250.0 Hz)
        sub_audio = round(random.uniform(67.0, 250.0), 1)
        
        # Generate a name
        name = f"Repeater {i+1} ({lat:.2f}, {lon:.2f})"
        
        repeaters.append({
            "n": name,
            "rf": frequency,
            "tf": frequency,
            "ts": sub_audio,
            "rs": sub_audio
        })
    
    return repeaters
