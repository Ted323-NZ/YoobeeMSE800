from __future__ import annotations

from abc import ABC, abstractmethod
import csv
import json
import xml.etree.ElementTree as ET
from typing import Any, Iterable


class DataExporter(ABC):
    @abstractmethod
    def export(self, data: list[dict[str, Any]], output_path: str) -> None:
        raise NotImplementedError


class CsvExporter(DataExporter):
    def export(self, data: list[dict[str, Any]], output_path: str) -> None:
        if not data:
            # Write an empty file if there is no data.
            open(output_path, "w", encoding="utf-8").close()
            return

        fieldnames = list(data[0].keys())
        with open(output_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)


class JsonExporter(DataExporter):
    def export(self, data: list[dict[str, Any]], output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)


class XmlExporter(DataExporter):
    def export(self, data: list[dict[str, Any]], output_path: str) -> None:
        root = ET.Element("records")
        for record in data:
            record_elem = ET.SubElement(root, "record")
            for key, value in record.items():
                child = ET.SubElement(record_elem, str(key))
                child.text = str(value)

        tree = ET.ElementTree(root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
