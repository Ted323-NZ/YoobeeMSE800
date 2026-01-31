import json
import os

from exporter_factory import ExporterFactory

DATA_FILE = "data.json"
OUTPUT_DIR = "output"


def load_data(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    format_name = input("Choose export format (csv/json/xml): ").lower()
    exporter = ExporterFactory.create_exporter(format_name)

    data = load_data(DATA_FILE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_path = os.path.join(OUTPUT_DIR, f"export.{format_name}")
    exporter.export(data, output_path)

    print(f"Exported {len(data)} records to {output_path}")


if __name__ == "__main__":
    main()
