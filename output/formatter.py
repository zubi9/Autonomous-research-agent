"""
Formatter
Compiles research outputs into publication-quality Markdown or PDF formats.
"""


class ReportFormatter:
    def to_markdown(self, state_report: str, citations: list) -> str:
        """Formats research outputs into structured markdown."""
        return ""

    def to_pdf(self, markdown_content: str, output_path: str):
        """Generates a styled PDF from markdown."""
        pass
