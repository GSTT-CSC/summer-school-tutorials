"""
Fake HandOsteo pipeline — realistic stubs for students to write unit tests against.

The real system would load a DICOM hand X-ray, classify the view, measure the
second metacarpal, and return a DICOM encapsulated PDF report to PACS.
These stubs reproduce that interface without a trained model.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pydicom
import numpy as np

from src.constants import (
    ALLOWED_MODALITIES,
    SUPPORTED_VIEWS,
    MCP_NORMAL_THRESHOLD,
    MCP_OSTEOPENIA_THRESHOLD,
)


def _classify_mcp(mcp: float) -> str:
    """Return a clinical classification string for a given MCP percentage."""
    if mcp >= MCP_NORMAL_THRESHOLD:
        return "NORMAL"
    elif mcp >= MCP_OSTEOPENIA_THRESHOLD:
        return "OSTEOPENIA"
    return "OSTEOPOROSIS"


class DicomLoader:
    """Load and validate hand X-ray DICOM files."""

    def load(self, path: str) -> pydicom.Dataset:
        """Return a pydicom Dataset for the file at *path*."""

        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")
        try:
            ds = pydicom.dcmread(str(p))
        except Exception as exc:
            raise ValueError(f"Not a valid DICOM file: {p}") from exc

        modality = getattr(ds, "Modality", None)
        if modality not in ALLOWED_MODALITIES:
            #raise ValueError(
            #    f"Unsupported modality '{modality}'. "
            #    f"HandOsteo requires one of {ALLOWED_MODALITIES}."
            #)
            return ds  # <-- BUG: should raise error instead of returning invalid dataset
        return ds


class ViewClassifier:
    """Classify a hand X-ray view."""

    def classify(self, dataset: pydicom.Dataset) -> str:
        """Return ``'AP'`` or ``'PA'`` for a supported view."""

        view = getattr(dataset, "ViewPosition", "").strip().upper()
        if view in SUPPORTED_VIEWS:
            return view
        if view:
            #raise ValueError(
            #    f"View '{view}' is not supported. "
            #    "HandOsteo only processes AP or PA hand X-rays."
            #)
            return view  # <-- BUG: should raise error instead of returning unsupported view
        raise ValueError(
            "ViewPosition tag is missing or empty. Cannot classify view."
        )


class MCPMeasurer:
    """Measure Metacarpal Cortical Percentage."""

    @staticmethod
    def calculate_mcp(A: float, B: float) -> float:
        """Apply the MCP formula: ``((A - B) / A) * 100``."""

        if A <= 0:
            raise ValueError(f"A must be > 0, got {A}")
        if not (0 <= B < A):
            raise ValueError(f"B must be in [0, A), got B={B}, A={A}")
        return ((A - B) / A) * 100.0

    def measure(self, dataset: pydicom.Dataset) -> dict:
        """Return ``{'A': float, 'B': float, 'MCP': float}`` for *dataset*.

        Measurements are simulated. The medullary canal fraction (B/A) is drawn
        from a range appropriate for any ground truth stored in PatientComments:

          - contains 'osteoporosis' → MCP ~50–64 %
          - contains 'osteopenia'   → MCP ~65–74 %
          - contains 'normal'       → MCP ~75–85 %
          - otherwise               → full range  ~50–85 %

        Results are deterministic per DICOM instance (seeded on SOPInstanceUID).
        """

        try:
            arr = dataset.pixel_array
        except Exception as exc:
            raise ValueError("Cannot read pixel data from dataset.") from exc

        uid = str(getattr(dataset, "SOPInstanceUID", "")).encode()
        seed = int(hashlib.sha256(uid).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)

        comments = str(getattr(dataset, "PatientComments", "")).lower()
        if "osteoporosis" in comments:
            b_ratio = rng.uniform(0.36, 0.50)  # MCP ≈ 50–64 %
        elif "osteopenia" in comments:
            b_ratio = rng.uniform(0.26, 0.35)  # MCP ≈ 65–74 %
        elif "normal" in comments:
            b_ratio = rng.uniform(0.15, 0.25)  # MCP ≈ 75–85 %
        else:
            b_ratio = rng.uniform(0.15, 0.50)  # MCP ≈ 50–85 % (unknown)

        A = round(arr.shape[1] / rng.uniform(70, 100), 2)
        B = round(A * b_ratio, 2)
        mcp = self.calculate_mcp(A, B)
        return {"A": A, "B": B, "MCP": round(mcp, 2)}


class ReportGenerator:
    """Generate a DICOM encapsulated PDF report."""

    def generate(self, measurements: dict, status: str = "success") -> bytes:
        """Return report content as bytes.

        Parameters
        ----------
        measurements:
            Output from :meth:`MCPMeasurer.measure`, or a dict with a
            ``'reason'`` key for failure reports.
        status:
            ``'success'`` or ``'failure'`` (default ``'success'``).
        """

        if status not in ("success", "failure"):
            raise ValueError(f"status must be 'success' or 'failure', got '{status}'")

        if status == "failure":
            reason = measurements.get("reason", "unknown error")
            lines = ["HandOsteo Report", "Status: FAILED", f"Reason: {reason}"]
        else:
            mcp = measurements["MCP"]
            lines = [
                "HandOsteo Report",
                "Status: SUCCESS",
                f"A: {measurements['A']} mm",
                f"B: {measurements['B']} mm",
                f"MCP: {mcp:.1f}%",
                f"Classification: {_classify_mcp(mcp)}",
            ]
        return "\n".join(lines).encode("utf-8")
