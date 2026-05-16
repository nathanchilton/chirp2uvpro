# Clipboard Format

The Clipboard format is a text-based format designed to be copied from a source and used to start the BTECH UV application.

## Structure

The format consists of a prefix string followed by a JSON object.

### Prefix
`Copy this text and start BTECH UV`

### JSON Object
The JSON object contains a `chs` array, where each element in the array represents a radio channel.

#### Channel Object Fields

| Field | Description |
| --- | --- |
| `n` | Name of the channel. |
| `rf` | Receive frequency (MHz, as a string). |
| `tf` | Transmit frequency (MHz, as a string, optional). |
| `ts` | Transmit sub-audio: CTCSS tone or DCS code. For CTCSS frequencies, the value is the frequency multiplied by 100 (e.g., `13180` = 131.8 Hz). For DCS codes, the value is the DCS code directly (< 1000). Use threshold: > 1000 = CTCSS (divide by 100 to get Hz), < 1000 = DCS code. |
| `rs` | Receive sub-audio: same encoding as `ts`. |
| `s` | Split mode (1 for enabled, 0 for disabled, optional). |
| `id` | ID (optional). |
| `p` | Power (optional). |
| `m` | Mode (e.g., 1 for FM, optional). |
| `w` | Wideband mode (0 or 1, optional). |

## Example

```text
Copy this text and start BTECH UV{"chs":[{"n":"N5RCA","rf":"146.780","tf":"146.180","ts":13180,"s":1,"id":1,"p":0}, ...]}
```
