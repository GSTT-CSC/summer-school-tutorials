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
