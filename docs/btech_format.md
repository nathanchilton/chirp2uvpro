# BTECH Format

The BTECH format is a CSV-based format used by the BTECH application.

## Columns

| Column | Description |
| --- | --- |
| Location | The index or location number of the channel. |
| Name | The name of the repeater or frequency. |
| Frequency | The receive frequency. |
| Duplex | The duplex mode (`+`, `-`, or empty). |
| Offset | The frequency offset. |
| Tone | The tone mode (`Tone`, `TSQL-R`, or empty). |
| rToneFreq | The receive tone frequency. |
| cToneFreq | The transmit tone frequency. |
| DtcsCode | DTCS code. |
| DtcsPolarity | DTCS polarity (`NN` or `SS`). |
| RxDtcsCode | Receive DTCS code. |
| CrossMode | Cross mode (`Tone->Tone` or empty). |
| Mode | The modulation mode (`FM`, `NFM`, `AM`). |
| TStep | The transmission step size. |
| Skip | Whether to skip this channel (`S` or empty). |
| Power | The power level (e.g., `5.0W`, `0.5W`). |
| Comment | Any additional comments. |
| URCALL | URCALL information. |
| RPT1CALL | RPT1CALL information. |
| RPT2CALL | RPT2CALL information. |
| DVCODE | DVCODE information. |

## Example

```csv
1,N5RCA,146.780000,-,0.600000,Tone,131.8,131.8,023,NN,023,Tone->Tone,FM,5.00,,5.0W,,,,,
```
