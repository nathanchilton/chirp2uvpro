import io
import pandas as pd
import json
import re
from src.converter.logic import btech_to_chirp

btech_content = 'BTECH UV{"chs":[{"n":"Test","rf":"146.520","tf":"146.520","ts":0,"s":0,"m":"FM"}]}'
output, error = btech_to_chirp(btech_content)
print(f"Output: {output}")
print(f"Error: {error}")

