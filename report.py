import os
import shutil
import tempfile
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)

styles = getSampleStyleSheet()
title_style = styles["Title"]
heading_style = styles["Heading1"]
body_style = styles["BodyText"]
caption_style = ParagraphStyle(
    "Caption", parent=styles["BodyText"], fontSize=8, textColor=colors.grey
)


def _fig_path(tmpdir, name):
    return os.path.join(tmpdir, name)


def _save(fig, path):
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _table(data, col_widths=None):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(19 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def _header(column, opt, design_warnings):
    elems = []
    elems.append(Paragraph(
        f"{column.light.name}-{column.heavy.name} Distillation Column Design",
        title_style
    ))
    elems.append(Paragraph(
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        body_style
    ))
    elems.append(Spacer(1, 0.4 * cm))

    data = [
        ["Parameter", "Value"],
        ["System", f"{column.light.name} / {column.heavy.name}"],
        ["F", f"{column.F:.2f} kmol/h"],
        ["zF", f"{column.zF:.2f} mol/mol"],
        ["xD", f"{column.xD:.2f} mol/mol"],
        ["xB", f"{column.xB:.2f} mol/mol"],
        ["P", f"{column.P:.2f} atm"],
        ["q", f"{column.q:.2f}"],
        ["T", f"{column.T:.2f} °C"],
        ["α", f"{column.alfa:.4f}"],
        ["Eo", f"{column.Eo:.2f}"],
        ["Tray spacing", f"{column.tray_spacing:.2f} m"],
        ["Rmin", f"{column.Rmin:.4f}"],
        ["R (optimum)", f"{opt['R']:.4f}"],
    ]

    elems.append(
        _table(
            data,
            col_widths=[6 * cm, 7 * cm]
        )
    )

    if design_warnings:
        elems.append(Spacer(1, 0.3 * cm))
        for w in design_warnings:
            elems.append(Paragraph(f"- {w}", body_style))

    return elems


def _equations(column, opt):
    elems = [Paragraph("Operating Lines", heading_style)]
    elems.append(Paragraph(
        f"Rectifying line: y = {opt['m_rec']:.4f}x + {opt['b_rec']:.4f}", body_style
    ))
    elems.append(Paragraph(f"q-line: x = {column.zF}", body_style))
    elems.append(Paragraph(
        f"Stripping line: y = {opt['m_strip']:.4f}x + {opt['b_strip']:.4f}", body_style
    ))
    elems.append(Spacer(1, 0.3 * cm))
    elems.append(Paragraph(f"N_theoretical: {opt['N_theoretical']} stages", body_style))
    elems.append(Paragraph(f"N_actual: {opt['N_actual']:.0f} trays", body_style))
    return elems


def _stage_table(opt):
    x_list, y_list = opt["x_list"], opt["y_list"]
    elems = [Paragraph("Stage-by-Stage Compositions", heading_style)]
    rows = [["Stage", "x [mol/mol]", "y [mol/mol]"]]
    rows.append(["0", f"{x_list[0]:.6f}", f"{y_list[0]:.6f} (starting point)"])
    for i in range(1, len(x_list)):
        rows.append([str(i), f"{x_list[i]:.6f}", f"{y_list[i]:.6f}"])
    elems.append(_table(rows, col_widths=[2.5 * cm, 5 * cm, 6.5 * cm]))
    return elems


def _sizing_table(opt):
    elems = [Paragraph("Column Sizing", heading_style)]
    data = [
        ["Parameter", "Value"],
        ["Column height H_vessel", f"{opt['H_vessel']:.2f} m"],
        ["Vapor flow V", f"{opt['V']:.2f} kmol/h"],
        ["Column diameter Dc", f"{opt['Dc']:.3f} m"],
        ["Column cross-sectional area A_col", f"{opt['A_col']:.3f} m²"],
    ]
    elems.append(_table(data, col_widths=[9 * cm, 5 * cm]))
    return elems


def _energy_table(opt):
    elems = [Paragraph("Energy Duties", heading_style)]
    data = [
        ["Parameter", "Value"],
        ["Condenser duty Qc", f"{opt['Qc']:.3e} kJ/h"],
        ["Reboiler duty Qr", f"{opt['Qr']:.3e} kJ/h"],
    ]
    elems.append(_table(data, col_widths=[9 * cm, 5 * cm]))
    return elems


def _cost_table(opt):
    elems = [Paragraph("Costs", heading_style)]
    data = [
        ["Parameter", "Value"],
        ["Steam cost", f"${opt['SteamYear']:,.0f} / year"],
        ["Cooling cost", f"${opt['CoolingYear']:,.0f} / year"],
        ["Shell cost", f"${opt['ShellCost']:,.0f}"],
        ["Tray cost", f"${opt['TrayCost']:,.0f}"],
        ["Condenser cost", f"${opt['CondenserCost']:,.0f}"],
        ["Reboiler cost", f"${opt['ReboilerCost']:,.0f}"],
        ["Total purchase cost", f"${opt['PurchaseCost']:,.0f}"],
        ["Capital recovery factor (CRF)", f"{opt['CRF']:.5f} 1/year"],
        ["Annualized capital cost", f"${opt['AnnualCapital']:,.0f} / year"],
        ["Total annual cost (TAC)", f"${opt['TAC']:,.0f} / year"],
    ]
    elems.append(_table(data, col_widths=[9 * cm, 5 * cm]))
    return elems


def _mccabe_thiele_figure(column, opt, tmpdir):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(opt["x"], opt["y_eqcurve"], color="red", label="eq curve")
    ax.plot(opt["x"], opt["y_d"], color="blue", label="diagonal")
    ax.plot(opt["x"], opt["y_rec"], color="orange", label="rec line")
    ax.plot(opt["x"], opt["y_strip"], color="black", label="strip line")
    ax.plot(opt["x_q"], opt["y_q"], color="green", label="q-line")

    x_list, y_list = opt["x_list"], opt["y_list"]
    for i in range(1, len(x_list)):
        ax.plot([x_list[i - 1], x_list[i]], [y_list[i - 1], y_list[i - 1]], color="grey", linewidth=0.8)
        ax.plot([x_list[i], x_list[i]], [y_list[i - 1], y_list[i]], color="grey", linewidth=0.8)

    ax.axvline(column.xB, color="black", linestyle="--")
    ax.axvline(column.xD, color="black", linestyle="--")
    ax.set_title("McCabe\u2013Thiele")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    path = _fig_path(tmpdir, "mccabe_thiele.png")
    _save(fig, path)

    elems = [Paragraph("McCabe-Thiele Diagram", heading_style)]
    elems.append(Image(path, width=11 * cm, height=11 * cm))
    return elems


def _tac_vs_r_figure(column, tmpdir):
    R_values = column.R_values
    TACs = column.TACs
    idx_opt = column.idx_opt

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(R_values, TACs, color="#4C72B0")
    ax.scatter([R_values[idx_opt]], [TACs[idx_opt]], color="red", zorder=5)
    ax.annotate("Ropt", (R_values[idx_opt], TACs[idx_opt]), textcoords="offset points", xytext=(5, 5))
    ax.set_xlabel("R")
    ax.set_ylabel("TAC")
    path = _fig_path(tmpdir, "tac_vs_r.png")
    _save(fig, path)

    elems = [Paragraph("TAC vs Reflux Ratio", heading_style)]
    elems.append(Image(path, width=13 * cm, height=8.7 * cm))
    return elems


def _cost_breakdown_figures(opt, tmpdir):
    elems = [Paragraph("Economic Breakdown", heading_style)]

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    ax.bar(
        ["Annualized\ncapital", "Steam", "Cooling\nwater"],
        [opt["AnnualCapital"], opt["SteamYear"], opt["CoolingYear"]],
        color=["#55A868", "#DD8452", "#64B5CD"],
    )
    ax.set_ylabel("Annual cost [$/yr]")
    ax.set_title("TAC split: capital vs utilities")
    path = _fig_path(tmpdir, "tac_split.png")
    _save(fig, path)
    elems.append(Image(path, width=12 * cm, height=7.6 * cm))

    fig2, ax2 = plt.subplots(figsize=(5.5, 3.5))
    ax2.bar(
        ["Shell", "Trays", "Condenser", "Reboiler"],
        [opt["ShellCost"], opt["TrayCost"], opt["CondenserCost"], opt["ReboilerCost"]],
        color="#4C72B0",
    )
    ax2.set_ylabel("Purchase cost [$]")
    ax2.set_title("Equipment cost breakdown")
    path2 = _fig_path(tmpdir, "equipment_split.png")
    _save(fig2, path2)
    elems.append(Spacer(1, 0.4 * cm))
    elems.append(Image(path2, width=12 * cm, height=7.6 * cm))

    return elems


def generate_report(column, output_path, design_warnings=None):
    if design_warnings is None:
        design_warnings = []

    opt = column.optimum
    tmpdir = tempfile.mkdtemp()

    try:
        story = []
        story += _header(column, opt, design_warnings)
        story.append(Spacer(1, 0.4 * cm))
        story += _equations(column, opt)
        story.append(PageBreak())
        story += _stage_table(opt)
        story.append(PageBreak())
        story += _sizing_table(opt)
        story.append(Spacer(1, 0.4 * cm))
        story += _energy_table(opt)
        story.append(Spacer(1, 0.4 * cm))
        story += _cost_table(opt)
        story.append(PageBreak())
        story += _mccabe_thiele_figure(column, opt, tmpdir)
        story.append(PageBreak())
        story += _tac_vs_r_figure(column, tmpdir)
        story.append(PageBreak())
        story += _cost_breakdown_figures(opt, tmpdir)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
        )
        doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return output_path