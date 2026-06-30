"""
Presentation helpers for the Day 2 QMS notebooks.

These functions hide the boring boilerplate — YAML pretty-printing, DICOM
plotting, the stub-behaviour table and rendered-document display — so the
notebook cells attendees read stay focused on the QMS concepts.

Each function does its own display()/plt.show(), so a notebook cell is one line.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pydicom
import yaml
from IPython.display import SVG, Markdown, display

# Colours used to mark accepted (green) vs rejected (red) inputs.
ACCEPT_COLOUR = "#1a7f1a"
REJECT_COLOUR = "#c0392b"


class MyDumper(yaml.Dumper):
    """YAML dumper that indents list items under their key for readability."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def _dump(data):
    """Pretty-print a Python object as YAML using the tutorial's house style."""
    return yaml.dump(data, Dumper=MyDumper, default_flow_style=False, sort_keys=False)


def show_yaml(path):
    """Load a YAML data file and pretty-print its contents."""
    with open(path) as stream:
        data = yaml.safe_load(stream)
    print(_dump(data))


def show_design_specs(path="day2_data/data/requirements.yml",
                      ids=("SDS-001", "SDS-002")):
    """Print only the named system design specs (sys_des_spec) from a requirements file."""
    with open(path) as stream:
        reqs = yaml.safe_load(stream)
    targets = set(ids)
    focus = [item for item in reqs.get("sys_des_spec", []) if item["id"] in targets]
    print(_dump({"sys_des_spec": focus}))


def show_care_diagram():
    """Render the HandOsteo care process diagram as an inline SVG."""
    from src.care_process_diagram import build_diagram

    display(SVG(data=build_diagram()))


def plot_dicom_inputs(xray_dir="day2_data/xray/dicom"):
    """Plot the seven synthetic hand X-rays, green-bordered if they should be accepted."""
    xray_dir = Path(xray_dir)
    files = {
        "AP hand 1": xray_dir / "AP_1.dcm",
        "AP hand 2": xray_dir / "AP_2.dcm",
        "AP hand 3": xray_dir / "AP_3.dcm",
        "Oblique hand 1": xray_dir / "Ob_1.dcm",
        "Oblique hand 2": xray_dir / "Ob_2.dcm",
        "Wrong modality (CT)": xray_dir / "CT_1.dcm",
        "Wrong modality (MR)": xray_dir / "MR_1.dcm",
    }

    fig, axes = plt.subplots(1, len(files), figsize=(23, 6))
    for ax, (title, path) in zip(axes, files.items()):
        ds = pydicom.dcmread(str(path))
        accepted = path.name.startswith("AP_")
        border = ACCEPT_COLOUR if accepted else REJECT_COLOUR
        ax.imshow(ds.pixel_array, cmap="gray", aspect="equal")
        ax.set_title(title, fontsize=10, color=border, fontweight="bold")
        ax.axis("off")
        for spine in ax.spines.values():
            spine.set_edgecolor(border)
            spine.set_linewidth(3)
            spine.set_visible(True)

    fig.suptitle(
        "HandOsteo inputs — only AP CR/DX views (green ✓) should be processed; "
        "obliques and wrong-modality CT/MR (red ✗) should be rejected",
        fontsize=16, y=1.02,
    )
    plt.tight_layout()
    plt.show()


def render_behaviour_table(rows):
    """Render the stub-pipeline results collected in the notebook as a table.

    The notebook sets up the pipeline classes and runs them over each DICOM,
    building ``rows`` (one dict per file). This helper just makes a nice table
    out of them so that cell stays focused on *how the pipeline runs*.

    The stub ships with two deliberate bugs, so several rows are wrongly
    ACCEPTED — this table makes the bugs the verification tests must catch
    visible.
    """
    df = pd.DataFrame(rows)
    display(df)
    print("\nNote how Ob_1, Ob_2, CT_1 and MR_1 are wrongly ACCEPTED — "
          "the bugs your tests must catch.")


def show_doc(path):
    """Display a rendered QMS release document (release/*.md) as Markdown."""
    if Path(path).exists():
        display(Markdown(Path(path).read_text(encoding="utf-8")))
    else:
        print("Run the make cell above first to generate", path)


def show_unit_test_record(path="day2_data/release/unit_test_record.md"):
    """Display the auto-generated unit-test traceability record as Markdown."""
    if Path(path).exists():
        display(Markdown(Path(path).read_text(encoding="utf-8")))
    else:
        print("Run the unit-test cell above first to generate", path)


# ── Diagrams ──────────────────────────────────────────────────────────────────

# Palette shared by both diagrams.
_BOX_FILL = "#eef3fb"
_BOX_EDGE = "#2c5aa0"
_VERIFY_FILL = "#e8f5e9"
_VERIFY_EDGE = "#1a7f1a"
_VALIDATE_FILL = "#fff3e0"
_VALIDATE_EDGE = "#e67e22"


def _flow_box(ax, x, y, w, h, text, fill, edge, fontsize=10, weight="bold"):
    """Draw a single rounded box with centred wrapped text."""
    from matplotlib.patches import FancyBboxPatch

    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.6, edgecolor=edge, facecolor=fill, mutation_aspect=1,
    ))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight, color="#1b2a41", wrap=True)


def show_qms_process_flow():
    """Draw the QMS traceability chain: risk → requirements → design → V&V.

    Mirrors the GSTT-CSC QMS-Template flow — every risk control and requirement
    is implemented by a design spec, then verified by unit tests and validated by
    manual tests.
    """
    stages = [
        ("Risk Control\n(Hazard Log)", _BOX_FILL, _BOX_EDGE, None),
        ("Requirements\n(SRS)", _BOX_FILL, _BOX_EDGE, None),
        ("System Design\nSpec (SDS)", _BOX_FILL, _BOX_EDGE, None),
        ("Unit Tests", _VERIFY_FILL, _VERIFY_EDGE, "Verification\n(built it right?)"),
        ("Manual Tests", _VALIDATE_FILL, _VALIDATE_EDGE, "Validation\n(built the right thing?)"),
    ]

    n = len(stages)
    box_w, box_h, gap = 1.7, 1.0, 0.55
    pitch = box_w + gap
    fig, ax = plt.subplots(figsize=(2.0 * n, 2.6))

    for i, (label, fill, edge, sublabel) in enumerate(stages):
        x = i * pitch
        y = 0.9
        _flow_box(ax, x, y, box_w, box_h, label, fill, edge)
        if sublabel:
            ax.text(x + box_w / 2, y - 0.32, sublabel, ha="center", va="top",
                    fontsize=8.5, style="italic", color=edge)
        if i < n - 1:
            ax.annotate("", xy=(x + box_w + gap, y + box_h / 2),
                        xytext=(x + box_w, y + box_h / 2),
                        arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.8))

    ax.set_xlim(-0.3, (n - 1) * pitch + box_w + 0.3)
    ax.set_ylim(-0.5, 2.3)
    ax.axis("off")
    ax.set_title("QMS traceability chain — requirement → design → verification → validation",
                 fontsize=12, fontweight="bold", pad=10)
    plt.tight_layout()
    plt.show()


def _show_stage_image(ax, path):
    """imshow a PNG (or a placeholder) into *ax* on a black panel."""
    ax.set_facecolor("black")
    if Path(path).exists():
        import matplotlib.image as mpimg

        ax.imshow(mpimg.imread(str(path)))
    else:
        ax.text(0.5, 0.5, "(image\nunavailable)", ha="center", va="center",
                fontsize=9, color="#999", transform=ax.transAxes)
    ax.set_xticks([])
    ax.set_yticks([])


def show_handosteo_pipeline(xray_dir="day2_data/xray/dicom"):
    """Draw the four-stage HandOsteo pipeline with the real X-ray images.

    Each panel is labelled with the pipeline class that produces it:
    DicomLoader → ViewClassifier (AP accepted ✓) → MCPMeasurer (2nd metacarpal
    A/B) → ReportGenerator (a screening report).
    """
    xray_dir = Path(xray_dir)
    fig, axes = plt.subplots(1, 4, figsize=(20, 5.6))

    # 1. DicomLoader — load and validate the DICOM.
    _show_stage_image(axes[0], xray_dir / "image.png")
    axes[0].set_title("DicomLoader", fontsize=15, fontweight="bold", color="#1b2a41")
    axes[0].set_xlabel("Load & validate DICOM (CR/DX)", fontsize=11)

    # 2. ViewClassifier — confirm the view; big green tick = AP accepted.
    _show_stage_image(axes[1], xray_dir / "image.png")
    axes[1].text(0.62, 0.60, "✓", ha="center", va="center", fontsize=130,
                 fontweight="bold", color="#3ec13e", transform=axes[1].transAxes)
    axes[1].set_title("ViewClassifier", fontsize=15, fontweight="bold", color="#1b2a41")
    axes[1].set_xlabel("AP view accepted ✓  (oblique ✗)", fontsize=11)

    # 3. MCPMeasurer — circle on the 2nd metacarpal with A/B measurement lines.
    _show_stage_image(axes[2], xray_dir / "image_measured.png")
    axes[2].set_title("MCPMeasurer", fontsize=15, fontweight="bold", color="#1b2a41")
    axes[2].set_xlabel("Measure 2nd metacarpal A, B → MCP %", fontsize=11)

    # 4. ReportGenerator — a clean screening report card.
    axes[3].set_facecolor("white")
    axes[3].set_xticks([])
    axes[3].set_yticks([])
    for spine in axes[3].spines.values():
        spine.set_edgecolor("#cccccc")
    axes[3].text(0.5, 0.74, "REPORT", ha="center", va="center", fontsize=30,
                 fontweight="bold", color="#1b2a41", transform=axes[3].transAxes)
    axes[3].text(0.5, 0.50, "MCP: 40 %", ha="center", va="center", fontsize=20,
                 color="#1b2a41", transform=axes[3].transAxes)
    axes[3].text(0.5, 0.36, "Osteoporosis", ha="center", va="center", fontsize=20,
                 color=REJECT_COLOUR, transform=axes[3].transAxes)
    axes[3].set_title("ReportGenerator", fontsize=15, fontweight="bold", color="#1b2a41")
    axes[3].set_xlabel("Screening report → PACS", fontsize=11)

    # Black arrows between the four stages, drawn in figure coordinates.
    from matplotlib.patches import FancyArrowPatch

    for left, right in zip(axes[:-1], axes[1:]):
        x0 = left.get_position().x1
        x1 = right.get_position().x0
        y = (left.get_position().y0 + left.get_position().y1) / 2
        fig.patches.append(FancyArrowPatch(
            (x0 + 0.004, y), (x1 - 0.004, y), transform=fig.transFigure,
            arrowstyle="-|>", mutation_scale=26, color="#333", lw=2.4,
        ))

    fig.suptitle("HandOsteo pipeline — DICOM in, osteoporosis-screening report out",
                 fontsize=16, fontweight="bold", y=1.04)
    plt.show()
