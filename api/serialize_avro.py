import json
import sys
from avrogen import write_schema_files
from pathlib import Path

schema_json_file = sys.argv[1]
output_directory = sys.argv[2]

schema_json = Path(schema_json_file).read_text()
write_schema_files(schema_json, output_directory)