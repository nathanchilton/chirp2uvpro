import json
from .parsers import (
    ClipboardParser,
    ChirpParser,
    BtechParser,
    ChirpGenerator,
    BtechGenerator,
    ClipboardGenerator
)

def detect_format(content: str) -> str:
    if not content:
        return 'auto'
    
    # Try Chirp (most specific)
    try:
        if ChirpParser().parse(content):
            return 'chirp'
    except:
        pass

    # Try Btech
    try:
        if BtechParser().parse(content):
            return 'btech'
    except:
        pass

    # Try Clipboard (most general)
    try:
        if ClipboardParser().parse(content):
            return 'clipboard'
    except:
        pass

    return 'auto'

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
    if not csv_content:
        return "", None
    
    try:
        return convert_format(csv_content, 'chirp', 'btech')
    except ConversionError as e:
        return "", str(e)
    except Exception as e:
        return "", str(e)

def btech_to_chirp(csv_content: str) -> tuple[str, str | None]:
    """Wrapper for BtechParser and ChirpGenerator to maintain backward compatibility."""
    if not csv_content:
        return "", None
    
    try:
        return convert_format(csv_content, 'btech', 'chirp')
    except ConversionError as e:
        return "", str(e)
    except Exception as e:
        return "", str(e)

def internal_to_clipboard(channels: list) -> tuple[str, str | None]:
    """Wrapper for ClipboardGenerator to maintain backward compatibility."""
    if not channels:
        return "", None

    try:
        generator = ClipboardGenerator()
        return generator.generate(channels), None
    except Exception as e:
        return "", str(e)

def convert_format(content: str, input_format: str, output_format: str) -> tuple[str, str | None]:
    """Unified conversion function that handles any supported format combination."""
    if not content:
        return "", None

    if input_format == 'auto':
        input_format = detect_format(content)
    
    if input_format == 'auto':
        # If we still have 'auto', it means detection failed. 
        # We can't proceed without knowing the format.
        return "", None

    try:
        # 1. Parse to internal channels
        channels = []
        if input_format == 'chirp':
            channels = ChirpParser().parse(content)
        elif input_format == 'btech':
            channels = BtechParser().parse(content)
        elif input_format == 'clipboard':
            channels = ClipboardParser().parse(content)
        else:
            raise ConversionError(f"Unsupported input format: {input_format}")

        if not channels:
            return "", None
        
        # 2. Generate from channels
        if output_format == 'chirp':
            output_csv = ChirpGenerator().generate(channels)
        elif output_format == 'btech':
            output_csv = BtechGenerator().generate(channels)
        elif output_format == 'clipboard':
            output_csv = ClipboardGenerator().generate(channels)
        else:
            raise ConversionError(f"Unsupported output format: {output_format}")

        return output_csv, None

    except Exception as e:
        raise ConversionError(str(e))

