# Internal Channel Format Specification

This document specifies the internal representation of radio channels used throughout the `chirp2uvpro` application. All parsers (`BaseParser`) must output a list of dictionaries, and all generators (`BaseGenerator`) must accept this format.

## Data Structure

A channel is represented as a `Dict[str, Any]` within a `List[Dict[str, Any]]`.

## Channel Fields

| Field | Type | Description |
| --- | --- | --- |
| `name` | `str` | The name of the channel/repeater. |
| `location` | `str` | The location or index of the channel. |
| `tx_freq_hz` | `float` | Transmit frequency in Hertz. |
| `rx_freq_hz` | `float` | Receive frequency in Hertz. |
| `offset_hz` | `float` | Frequency offset in Hertz (relative to `tx_freq_hz`). |
| `duplex` | `str` | Duplex mode: `'+'`, `'-'`, or `'none'`. |
| `tx_sub_audio_hz` | `float` | Transmit sub-audio (CTCSS/DCS) frequency in Hertz. |
| `rx_sub_audio_hz` | `float` | Receive sub-audio (CTCSS/DCS) frequency in Hertz. |
| `tx_power` | `str` | Transmit power level (e.g., `'5.0W'`, `'0.5W'`, `'M'`). |
| `bandwidth_hz` | `int` | Channel bandwidth in Hertz (e.g., `25000`). |
| `scan` | `bool` | Whether scanning is enabled for this channel. |
| `talk_around` | `bool` | Whether talk-around mode is enabled. |
| `pre_de_emph_bypass` | `bool` | Whether pre/de-emphasis bypass is enabled. |
| `sign` | `bool` | Whether DTMF signaling is enabled. |
| `tx_dis` | `bool` | Whether transmit disable is enabled. |
| `bclo` | `bool` | Whether BCLO (Busy Channel Lockout) is enabled. |
| `mute` | `bool` | Whether mute is enabled. |
| `rx_modulation` | `str` | Receive modulation: `'FM'` or `'AM'`. |
| `tx_modulation` | `str` | Transmit modulation: `'FM'` or `'AM'`. |
| `skip` | `bool` | Whether the channel should be skipped. |

## Implementation Notes

- **Frequency Normalization**: All frequencies must be in Hertz (`float`).
- **Sub-audio**: If no sub-audio is present, the frequency should be `0.0`.
- **Duplex**: If `duplex` is `'none'`, then `rx_freq_hz` should be equal to `tx_freq_hz` and `offset_hz` should be `0.0`.
- **Power**: Power should be normalized (e.g., via `normalize_power` utility).
