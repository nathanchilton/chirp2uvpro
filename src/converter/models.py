from dataclasses import dataclass, field

@dataclass
class Channel:
    """
    Represents a radio frequency channel in a universal format.
    """
    name: str = ""
    location: str = ""
    tx_freq_hz: float = 0.0
    rx_freq_hz: float = 0.0
    offset_hz: float = 0.0
    duplex: str = "none"
    bandwidth_hz: int = 25000
    tx_sub_audio_hz: float = 0.0
    rx_sub_audio_hz: float = 0.0
    tx_power: str = "M"
    skip: bool = False
    scan: bool = False
    talk_around: bool = False
    pre_de_emph_bypass: bool = False
    sign: bool = False
    tx_dis: bool = False
    bclo: bool = False
    mute: bool = False
    rx_modulation: str = "FM"
    tx_modulation: str = "FM"
    # Extra fields that might be present in some formats
    extra_fields: dict = field(default_factory=dict)
