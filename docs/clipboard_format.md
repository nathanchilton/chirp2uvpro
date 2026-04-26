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
| `rf` | Receive frequency (as a string). |
| `tf` | Transmit frequency (as a string, optional). |
| `ts` | Tone frequency in Hz (as a string, optional). |
| `s` | Split mode (1 for enabled, 0 for disabled, optional). |
| `id` | ID (optional). |
| `p` | Power (optional). |
| `m` | Mode (e.g., 1 for FM, optional). |
| `rs` | Rx Split frequency in Hz (optional). |
| `w` | Wideband mode (0 or 1, optional). |

## Example

```text
Copy this text and start BTECH UV{"chs":[{"n":"N5RCA","rf":"146.780","tf":"146.180","ts":13180,"s":1,"id":1,"p":0}, ...]}
```
