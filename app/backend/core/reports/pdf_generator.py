# pyre-ignore-all-errors
"""Professional PDF Report Generator for DesignBook.

Implements plan.md §Module 6: Output Generation.
Generates a strictly-formatted multi-section ReportLab PDF summarizing:
  1. Project Information
  2. Material Data
  3. Load Summaries
  4. Analysis Results (Periods, Base Shear)
  5. Member Design Summaries
  6. Deflection / Drift Checks
  7. Quantity Takeoff
  8. Cost Estimate
  9. Appendix: Iteration History
 10. Footer / Disclaimer
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("designbook.reports")

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.warning("reportlab not installed — PDF generation unavailable")


class PDFReportGenerator:
    """Professional multi-section PDF report for structural design projects."""

    PAGE_WIDTH, PAGE_HEIGHT = A4 if HAS_REPORTLAB else (595, 842)
    MARGIN_LEFT = 50
    MARGIN_RIGHT = 50
    MARGIN_TOP = 50
    MARGIN_BOTTOM = 70
    LINE_HEIGHT = 16

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.y_cursor = self.PAGE_HEIGHT - self.MARGIN_TOP
        self.page_num = 0
        self.c: Any = None

    def _start(self):
        """Initialize the canvas."""
        if not HAS_REPORTLAB:
            raise RuntimeError("reportlab is required for PDF generation")
        self.c = canvas.Canvas(self.output_path, pagesize=A4)
        self.c.setTitle("DesignBook Structural Report")
        self.c.setAuthor("DesignBook — AntiGravity Toolkit")
        self.page_num = 1

    def _new_page(self):
        """Start a new page with footer."""
        self._draw_footer()
        self.c.showPage()
        self.page_num += 1
        self.y_cursor = self.PAGE_HEIGHT - self.MARGIN_TOP

    def _check_space(self, needed: float = 40):
        """Ensure enough vertical space, or start a new page."""
        if self.y_cursor < self.MARGIN_BOTTOM + needed:
            self._new_page()

    def _draw_footer(self):
        """Draw page footer with page number and timestamp."""
        self.c.setFont("Helvetica", 8)
        self.c.setFillColor(colors.grey)
        self.c.drawString(self.MARGIN_LEFT, 30,
                          f"DesignBook v1.0 — Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        self.c.drawRightString(self.PAGE_WIDTH - self.MARGIN_RIGHT, 30,
                               f"Page {self.page_num}")
        self.c.setFillColor(colors.black)

    def _heading(self, text: str, level: int = 1):
        """Draw a section heading."""
        self._check_space(30)
        sizes = {1: 18, 2: 14, 3: 12}
        font_size = sizes.get(level, 12)
        self.c.setFont("Helvetica-Bold", font_size)
        self.c.drawString(self.MARGIN_LEFT, self.y_cursor, text)
        self.y_cursor -= font_size + 8
        if level == 1:
            self.c.setStrokeColor(colors.HexColor("#0066CC"))
            self.c.setLineWidth(1.5)
            self.c.line(self.MARGIN_LEFT, self.y_cursor + 4,
                        self.PAGE_WIDTH - self.MARGIN_RIGHT, self.y_cursor + 4)
            self.y_cursor -= 6
        self.c.setFont("Helvetica", 10)

    def _text(self, text: str, indent: float = 0):
        """Draw a line of body text."""
        self._check_space()
        self.c.drawString(self.MARGIN_LEFT + indent, self.y_cursor, text)
        self.y_cursor -= self.LINE_HEIGHT

    def _key_value(self, key: str, value: str, indent: float = 20):
        """Draw a key: value pair."""
        self._check_space()
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawString(self.MARGIN_LEFT + indent, self.y_cursor, f"{key}:")
        self.c.setFont("Helvetica", 10)
        self.c.drawString(self.MARGIN_LEFT + indent + 180, self.y_cursor, str(value))
        self.y_cursor -= self.LINE_HEIGHT

    def _table_row(self, cols: List[str], col_widths: List[float], bold: bool = False):
        """Draw a simple table row."""
        self._check_space()
        font = "Helvetica-Bold" if bold else "Helvetica"
        self.c.setFont(font, 9)
        x = self.MARGIN_LEFT
        for text, w in zip(cols, col_widths):
            self.c.drawString(x + 4, self.y_cursor, str(text)[:int(w/5)])
            x += w
        self.y_cursor -= self.LINE_HEIGHT

    # ── Report Sections ──────────────────────────────────────────────

    def _section_title_page(self, project: Dict[str, Any]):
        """Section 1: Title Page."""
        self.c.setFont("Helvetica-Bold", 28)
        self.c.drawCentredString(self.PAGE_WIDTH / 2, self.PAGE_HEIGHT - 200,
                                  "Structural Design Report")
        self.c.setFont("Helvetica", 16)
        self.c.drawCentredString(self.PAGE_WIDTH / 2, self.PAGE_HEIGHT - 250,
                                  project.get("name", "Untitled Project"))
        self.c.setFont("Helvetica", 12)
        self.c.drawCentredString(self.PAGE_WIDTH / 2, self.PAGE_HEIGHT - 300,
                                  f"Design Code: {project.get('code', 'BNBC 2020 / ACI 318-19')}")
        self.c.drawCentredString(self.PAGE_WIDTH / 2, self.PAGE_HEIGHT - 330,
                                  f"Date: {datetime.now().strftime('%B %d, %Y')}")
        self.c.setFont("Helvetica-Oblique", 10)
        self.c.drawCentredString(self.PAGE_WIDTH / 2, 120,
                                  "Generated by DesignBook — AntiGravity Structural OS")
        self._draw_footer()
        self.c.showPage()
        self.page_num += 1
        self.y_cursor = self.PAGE_HEIGHT - self.MARGIN_TOP

    def _section_materials(self, materials: Dict[str, Any]):
        """Section 2: Material Properties."""
        self._heading("2. Material Properties")
        self._key_value("Concrete Strength (f'c)", f"{materials.get('fc', 25)} MPa")
        self._key_value("Steel Yield (fy)", f"{materials.get('fy', 500)} MPa")
        self._key_value("Shear Steel (fy_v)", f"{materials.get('fy_v', 500)} MPa")
        self._key_value("Elastic Modulus (Ec)", f"{4700 * (materials.get('fc', 25) ** 0.5):.0f} MPa")
        self.y_cursor -= 10

    def _section_loads(self, loads: Dict[str, Any]):
        """Section 3: Load Summary."""
        self._heading("3. Load Summary")
        self._key_value("Dead Load", f"{loads.get('dead_kpa', 0):.2f} kPa")
        self._key_value("Live Load", f"{loads.get('live_kpa', 0):.2f} kPa")
        self._key_value("Seismic Zone Factor (Z)", f"{loads.get('Z', 0.2)}")
        self._key_value("Importance Factor (I)", f"{loads.get('I', 1.0)}")
        self._key_value("Response Modification (R)", f"{loads.get('R', 5.0)}")
        self._key_value("Base Shear (V)", f"{loads.get('base_shear_kn', 0):.2f} kN")
        self.y_cursor -= 10

    def _section_analysis(self, analysis: Dict[str, Any]):
        """Section 4: Analysis Results."""
        self._heading("4. Analysis Results")
        gravity = analysis.get("gravity", {})
        modal = analysis.get("modal", {})
        telemetry = analysis.get("telemetry", {})

        self._key_value("Gravity Status", gravity.get("status", "N/A"))
        self._key_value("Analysis Time", f"{telemetry.get('total_pipeline_seconds', 0):.3f} s")
        self._key_value("Nodes", str(telemetry.get("n_nodes", "N/A")))
        self._key_value("Elements", str(telemetry.get("n_elements", "N/A")))

        periods = modal.get("periods", [])
        if periods:
            self.y_cursor -= 6
            self._heading("Natural Periods", level=3)
            widths = [60.0, 100.0, 100.0]
            self._table_row(["Mode", "Period (s)", "Freq (Hz)"], widths, bold=True)
            for i, t in enumerate(periods[:6]):
                freq = 1.0 / max(t, 1e-15) if t > 0 and t < 1e10 else 0.0
                self._table_row([str(i + 1), f"{t:.4f}", f"{freq:.4f}"], widths)
        self.y_cursor -= 10

    def _section_member_design(self, members: Dict[str, Any]):
        """Section 5: Member Design Summary."""
        self._heading("5. Member Design Summary")
        widths = [80.0, 100.0, 100.0, 120.0, 80.0]
        self._table_row(["Member", "Type", "Status", "As_req (mm\u00b2)", "Iter"], widths, bold=True)

        for label, data in members.items():
            design = data.get("design", {})
            status = "OK"
            as_req = ""
            for k, v in design.items():
                if isinstance(v, dict):
                    st = v.get("status", "")
                    if "FAIL" in str(st).upper():
                        status = "FAIL"
                    if "As_req_mm2" in v:
                        as_req = f"{v['As_req_mm2']:.1f}"
            iteration = data.get("iteration", "")
            self._table_row([label, k, status, as_req, str(iteration)], widths)
        self.y_cursor -= 10

    def _section_drift(self, drifts: List[Dict[str, float]]):
        """Section 6: Story Drift Check."""
        self._heading("6. Serviceability — Story Drift")
        widths = [60.0, 100.0, 100.0, 100.0]
        self._table_row(["Story", "Drift (mm)", "Drift Ratio", "Status"], widths, bold=True)

        for d in drifts:
            ratio = d.get("drift_ratio", 0.0)
            status = "Pass" if ratio <= 0.020 else "FAIL"
            self._table_row(
                [str(int(d.get("story", 0))),
                 f"{d.get('drift_mm', 0):.3f}",
                 f"{ratio:.5f}",
                 status],
                widths
            )
        self.y_cursor -= 10

    def _section_quantities(self, qto: Dict[str, Any]):
        """Section 7: Quantity Takeoff."""
        self._heading("7. Bill of Quantities")
        self._key_value("Concrete Volume", f"{qto.get('concrete_vol', 0):.2f} m\u00b3")
        self._key_value("Steel Weight", f"{qto.get('steel_weight', 0):.2f} kg")
        self._key_value("Formwork Area", f"{qto.get('formwork_area', 0):.2f} m\u00b2")
        self.y_cursor -= 10

    def _section_cost(self, cost: Dict[str, Any]):
        """Section 8: Cost Estimate."""
        self._heading("8. Cost Estimate (BDT)")
        breakdown = cost.get("breakdown", {})
        self._key_value("Concrete", f"BDT {breakdown.get('concrete', 0):,.0f}")
        self._key_value("Rebar", f"BDT {breakdown.get('rebar', 0):,.0f}")
        self._key_value("Formwork", f"BDT {breakdown.get('formwork', 0):,.0f}")
        self._key_value("Labor & Overhead", f"BDT {breakdown.get('labor_and_overhead', 0):,.0f}")
        self.y_cursor -= 6
        self.c.setFont("Helvetica-Bold", 11)
        self._key_value("TOTAL ESTIMATED COST", f"BDT {cost.get('total_estimated_cost', 0):,.0f}")
        self.c.setFont("Helvetica", 10)
        self.y_cursor -= 10

    def _section_disclaimer(self):
        """Section 10: Disclaimer."""
        self._check_space(60)
        self.c.setFont("Helvetica-Oblique", 8)
        self.c.setFillColor(colors.grey)
        disclaimer = (
            "DISCLAIMER: This report is generated by DesignBook for preliminary structural "
            "assessment only. All designs must be reviewed and approved by a licensed "
            "Professional Engineer (PE) before construction. The developers assume no liability."
        )
        # Word-wrap the disclaimer
        words = disclaimer.split()
        line = ""
        for word in words:
            test = line + " " + word if line else word
            if self.c.stringWidth(test, "Helvetica-Oblique", 8) < (self.PAGE_WIDTH - 100):
                line = test
            else:
                self.c.drawString(self.MARGIN_LEFT, self.y_cursor, line)
                self.y_cursor -= 12
                line = word
        if line:
            self.c.drawString(self.MARGIN_LEFT, self.y_cursor, line)
            self.y_cursor -= 12
        self.c.setFillColor(colors.black)

    # ── Public API ────────────────────────────────────────────────────

    def generate(self, project_data: Dict[str, Any]) -> str:
        """Generate the full professional report.

        Args:
            project_data: Dict with keys: project, materials, loads,
                          analysis, members, drifts, qto, cost
        Returns:
            The output file path.
        """
        self._start()

        # §1 Title
        self._section_title_page(project_data.get("project", {}))

        # §2 Materials
        self._section_materials(project_data.get("materials", {}))

        # §3 Loads
        self._section_loads(project_data.get("loads", {}))

        # §4 Analysis
        if project_data.get("analysis"):
            self._section_analysis(project_data["analysis"])

        # §5 Member Design
        if project_data.get("members"):
            self._section_member_design(project_data["members"])

        # §6 Drift Checks
        if project_data.get("drifts"):
            self._section_drift(project_data["drifts"])

        # §7 Quantity Takeoff
        if project_data.get("qto"):
            self._section_quantities(project_data["qto"])

        # §8 Cost
        if project_data.get("cost"):
            self._section_cost(project_data["cost"])

        # §10 Disclaimer
        self._section_disclaimer()

        # Finalize
        self._draw_footer()
        self.c.save()
        logger.info(f"Report generated: {self.output_path} ({self.page_num} pages)")
        return self.output_path


# ── Legacy compatibility wrapper ──────────────────────────────────────

class pdf_generator:
    """Legacy wrapper — delegates to PDFReportGenerator."""

    @staticmethod
    def generate_project_report(project_data: dict, output_path: str) -> str:
        gen = PDFReportGenerator(output_path)
        return gen.generate(project_data)
