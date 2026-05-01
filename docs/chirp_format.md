# CHIRP Format

The CHIRP format is a CSV-based format used by the CHIRP application.

## Columns

The column structure is similar to the BTECH format.

| Column | Description |
| --- | --- |
| Location | The index or location number of the channel. |
| Name | The name of the repeater or frequency. |
| Frequency | The receive frequency (MHz). |
| Duplex | The duplex mode (`+`, `-`, or empty). |
| Offset | The frequency offset (MHz). |
| Tone | The tone mode (`Tone`, `TSQL-R`, or empty). |
| rToneFreq | The receive tone frequency (Hz). |
| cToneFreq | The transmit tone frequency (Hz).

*(Note: Based on the provided examples, the column structure for CHIRP and BTECH is identical.)*

## Example

```csv
1,N5RCA,146.780000,-,0.600000,Tone,131.8,131.8,023,NN,023,Tone->Tone,FM,5.00,,5.0W,,,,,
```
