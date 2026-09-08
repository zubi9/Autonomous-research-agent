from fpdf import FPDF


class ReportFormatter:
    def to_markdown(self, state_report: str, citations: list) -> str:
        """Formats research outputs into structured markdown."""
        return state_report

    def to_pdf(self, markdown_content: str, output_path: str):
        """Generates a styled PDF from markdown using fpdf2."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Configure standard margins
        pdf.set_margins(left=20, top=20, right=20)

        lines = markdown_content.split("\n")
        for line in lines:
            line_str = line.strip()
            if not line_str:
                pdf.ln(4)
                continue

            # Render Headings
            if line_str.startswith("# "):
                pdf.set_font("Helvetica", style="B", size=18)
                pdf.cell(0, 10, line_str[2:], new_x="LMARGIN", new_y="NEXT")
                pdf.ln(3)
            elif line_str.startswith("## "):
                pdf.set_font("Helvetica", style="B", size=14)
                pdf.cell(0, 8, line_str[3:], new_x="LMARGIN", new_y="NEXT")
                pdf.ln(2)
            elif line_str.startswith("### "):
                pdf.set_font("Helvetica", style="B", size=12)
                pdf.cell(0, 7, line_str[4:], new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
            # Render Bullets
            elif line_str.startswith(("- ", "* ")):
                pdf.set_font("Helvetica", size=11)
                pdf.write(5, "  * ")
                # Strip simple bold markup
                clean_txt = line_str[2:].replace("**", "")
                pdf.write(5, clean_txt)
                pdf.ln(5)
            # Render Text
            else:
                pdf.set_font("Helvetica", size=11)
                clean_txt = line_str.replace("**", "")
                pdf.multi_cell(0, 5, clean_txt)
                pdf.ln(1)

        pdf.output(output_path)
        print(f"Generated PDF report saved to {output_path}")
