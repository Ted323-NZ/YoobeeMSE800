from exporters import CsvExporter, JsonExporter, XmlExporter, DataExporter


class ExporterFactory:
    @staticmethod
    def create_exporter(format_name: str) -> DataExporter:
        format_name = format_name.lower()

        if format_name == "csv":
            return CsvExporter()
        if format_name == "json":
            return JsonExporter()
        if format_name == "xml":
            return XmlExporter()

        raise ValueError("Invalid export format")
