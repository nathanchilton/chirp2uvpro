import json
from .parsers import (
    ClipboardParser,
    ChirpParser,
    BtechParser,
    ChirpGenerator,
    BtechGenerator,
    ClipboardGenerator
)

class ConversionError(Exception):
    pass

def clipboard_to_internal_wrapper(text_content: str) -> tuple[list, str | None]:
    """Wrapper for ClipboardParser to maintain backward compatibility."""
    try:
        return ClipboardParser().parse(text_content), None
    except Exception as e:
        return [], str(e)

def clipboard_to_btech(text_content: str) -> tuple[str, str | None]:
    """Wrapper for ClipboardParser and BtechGenerator to maintain backward compatibility."""
    if not text_content:
        return "", None
    try:
        parser = ClipboardParser()
        generator = BtechGenerator()
        channels = parser.parse(text_content)
        if not channels:
            return "", None
        return generator.generate(channels), None
    except Exception as e:
        return "", str(e)

def internal_to_btech_csv(channels: list) -> tuple[str, str | None]:
    """Wrapper for BtechGenerator to maintain backward compatibility."""
    try:
        return BtechGenerator().generate(channels), None
    except Exception as e:
        return "", str(e)

def chirp_to_btech(csv_content: str) -> tuple[str, str | None]:
    """Wrapper for ChirpParser and BtechGenerator to maintain backward compatibility."""
    if csv_content is None:
        raise ConversionError("CSV content is None")
    if not csv_content:
        return "", None
    
    try:
        parser = ChirpParser()
        generator = BtechGenerator()
        channels = parser.parse(csv_content)
        if not channels:
            return "", None
        
        warning = None
        if len(channels) > 30:
            warning = "Truncated"
            channels = channels[:30]
            
        return generator.generate(channels), warning
    except Exception as e:
        return "", str(e)

def btech_to_chirp(csv_content: str) -> tuple[str, str | None]:
    """Wrapper for BtechParser and ChirpGenerator to maintain backward compatibility."""
    if not csv_content:
        return "", None
    
    try:
        parser = BtechParser()
        generator = ChirpGenerator()
        channels = parser.parse(csv_content)
        if not channels:
            return "", None
        
        return generator.generate(channels), None
    except Exception as e:
        return "", str(e)

def internal_to_clipboard(channels: list) -> tuple[str, str | None]:
    """Wrapper for ChirpGenerator to maintain backward compatibility."""
    if not channels:
        return "", None

    try:
        generator = ChirpGenerator()
        return generator.generate(channels), None
    except Exception as e:
        return "", str(e)
