# API Import Format Specification

This format is used for transferring repeater data from external web APIs (including our simulated `mock_repeaterbook.py`) to the Chirp2UVPro application.

## Structure

The format is a JSON object containing a list of repeater objects.

## Schema

### Root Object
- `repeaters` (Array of objects): A list of repeater objects.

### Repeater Object
Each object in the `repeaters` array represents a single repeater and contains the following properties:

| Property | Type | Description |
| :--- | :--- | :--- |
| `n` | `string` | The display name of the repeater. |
| `rf` | `number` | The receiving frequency in **MHz**. |
| `tf` | `number` | The transmitting frequency in **MHz**. |
| `ts` | `number` | The transmitting sub-audio (CTCSS/DCS) frequency in **Hz**. |
| `rs` | `number` | The receiving sub-audio (CTCSS/DCS) frequency in **Hz**. |

## Example JSON

```json
{
  "repeaters": [
    {
      "n": "Repeater 1 (40.71, -74.01)",
      "rf": 147.88,
      "tf": 147.88,
      "ts": 100.0,
      "rs": 100.0
    },
    {
      "n": "Repeater 2 (40.72, -74.02)",
      "rf": 146.55,
      "tf": 146.55,
      "ts": 123.0,
      "rs": 123.0
    }
  ]
}
```
