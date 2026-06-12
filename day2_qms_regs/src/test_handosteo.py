"""
HandOsteo unit tests — solution file.

Contains both mocking for pure unit tests and
the fake DICOM files in day2_data/xray/dicom/ for lightweight integration tests.

Run with:
    pytest src/unit_tests.py -v
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pydicom
import pydicom.uid
from pydicom.dataset import FileMetaDataset
import pytest

import sys
import os

if "src" not in sys.path:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.constants import ALLOWED_MODALITIES, SUPPORTED_VIEWS
from src.handosteo import (
    DicomLoader,
    ViewClassifier,
    MCPMeasurer,
    ReportGenerator,
)

DICOM_DIR = Path("day2_data/xray/dicom")


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_dataset(modality: str = "CR", view: str = "AP") -> pydicom.Dataset:
    """Return a minimal in-memory pydicom FileDataset with valid pixel data."""

    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.1")
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = pydicom.FileDataset("", {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.Modality = modality
    ds.ViewPosition = view

    # Some random pixel data to make it a valid image dataset
    ds.Rows = 100
    ds.Columns = 100
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelData = np.zeros((100, 100), dtype=np.uint8).tobytes()

    return ds


# ── SDS-001: DICOM input validation ──────────────────────────────────────────


@pytest.mark.req("SDS-001")
class TestDicomLoader:
    """SDS-001 — validate DICOM input modality before processing."""

    def test_load_cr_dicom_returns_dataset(self):
        """A CR-modality DICOM is loaded and returned as a Dataset."""
        loader = DicomLoader()
        ds = loader.load(str(DICOM_DIR / "AP_1.dcm"))
        assert isinstance(ds, pydicom.Dataset)

    def test_load_missing_file_raises_file_not_found(self):
        """A non-existent path raises FileNotFoundError."""
        loader = DicomLoader()
        with pytest.raises(FileNotFoundError):
            loader.load("does_not_exist.dcm")

    @pytest.mark.parametrize("modality", ["CT", "MG", "XA", "NM"])
    def test_unsupported_modality_raises_value_error(self, modality):
        """Non-CR/DX modalities are rejected with ValueError."""
        loader = DicomLoader()
        mock_ds = _make_dataset(modality=modality)
        with (
            patch("pydicom.dcmread", return_value=mock_ds),
            patch("pathlib.Path.exists", return_value=True),
        ):
            with pytest.raises(ValueError, match="Unsupported modality"):
                loader.load("fake.dcm")

    def test_load_non_dicom_file_raises_value_error(self, tmp_path):
        """A plain text file is rejected with ValueError."""
        bad_file = tmp_path / "not_a_dicom.txt"
        bad_file.write_text("hello world")
        loader = DicomLoader()
        with pytest.raises(ValueError, match="Not a valid DICOM"):
            loader.load(str(bad_file))

    @pytest.mark.parametrize("modality", list(ALLOWED_MODALITIES))
    def test_all_allowed_modalities_accepted(self, modality):
        """Every modality in ALLOWED_MODALITIES is accepted."""
        loader = DicomLoader()
        mock_ds = _make_dataset(modality=modality)
        with (
            patch("pydicom.dcmread", return_value=mock_ds),
            patch("pathlib.Path.exists", return_value=True),
        ):
            ds = loader.load("fake.dcm")
        assert ds.Modality == modality


# ── SDS-002: View classifier ──────────────────────────────────────────────────


@pytest.mark.req("SDS-002")
class TestViewClassifier:
    """SDS-002 — only process AP or PA images; reject oblique views."""

    @pytest.mark.parametrize("view", list(SUPPORTED_VIEWS))
    def test_supported_view_is_accepted(self, view):
        """AP and PA views are accepted and returned as-is."""
        clf = ViewClassifier()
        ds = _make_dataset(view=view)
        assert clf.classify(ds) == view

    @pytest.mark.parametrize("view", ["OBLIQUE", "LL", "RL", "LAT"])
    def test_unsupported_view_raises_value_error(self, view):
        """Non-AP/PA views raise ValueError (SRS-007)."""
        clf = ViewClassifier()
        ds = _make_dataset(view=view)
        with pytest.raises(ValueError, match="not supported"):
            clf.classify(ds)

    def test_ap_xray_file_classified_correctly(self):
        """Real AP DICOM file is classified without error."""
        clf = ViewClassifier()
        ds = pydicom.dcmread(str(DICOM_DIR / "AP_1.dcm"))
        result = clf.classify(ds)
        assert result in ("AP", "PA")

    def test_oblique_xray_file_rejected(self):
        """Real oblique DICOM is rejected."""
        clf = ViewClassifier()
        ds = pydicom.dcmread(str(DICOM_DIR / "Ob_1.dcm"))
        ds.ViewPosition = "OBLIQUE"
        with pytest.raises(ValueError):
            clf.classify(ds)


# ── SDS-003: MCP measurement formula ─────────────────────────────────────────


@pytest.mark.req("SDS-003")
class TestMCPMeasurer:
    """SDS-003 — MCP formula and measurement correctness."""

    def test_formula_known_values(self):
        """MCP formula gives correct result for known A and B."""
        result = MCPMeasurer.calculate_mcp(A=10.0, B=5.0)
        assert result == pytest.approx(50.0)

    def test_formula_full_cortex(self):
        """MCP = 100 when B = 0 (solid cortex, no medullary canal)."""
        result = MCPMeasurer.calculate_mcp(A=8.0, B=0.0)
        assert result == pytest.approx(100.0)

    def test_formula_rejects_zero_A(self):
        """A=0 raises ValueError."""
        with pytest.raises(ValueError, match="A must be"):
            MCPMeasurer.calculate_mcp(A=0.0, B=0.0)

    def test_formula_rejects_negative_A(self):
        """Negative A raises ValueError."""
        with pytest.raises(ValueError):
            MCPMeasurer.calculate_mcp(A=-5.0, B=2.0)

    def test_formula_rejects_B_equal_to_A(self):
        """B = A is physically impossible and raises ValueError."""
        with pytest.raises(ValueError):
            MCPMeasurer.calculate_mcp(A=10.0, B=10.0)

    def test_formula_rejects_B_greater_than_A(self):
        """B > A raises ValueError."""
        with pytest.raises(ValueError):
            MCPMeasurer.calculate_mcp(A=5.0, B=6.0)

    def test_measure_returns_required_keys(self):
        """measure() result contains A, B, and MCP keys."""
        measurer = MCPMeasurer()
        ds = _make_dataset()
        result = measurer.measure(ds)
        assert set(result.keys()) >= {"A", "B", "MCP"}

    def test_measure_mcp_consistent_with_formula(self):
        """MCP value from measure() matches the formula applied to A and B."""
        measurer = MCPMeasurer()
        ds = _make_dataset()
        result = measurer.measure(ds)
        expected = MCPMeasurer.calculate_mcp(result["A"], result["B"])
        assert result["MCP"] == pytest.approx(expected, abs=0.01)

    def test_measure_real_dicom(self):
        """measure() runs without error on a real AP DICOM file."""
        measurer = MCPMeasurer()
        ds = pydicom.dcmread(str(DICOM_DIR / "AP_1.dcm"))
        result = measurer.measure(ds)
        assert 0 < result["MCP"] <= 100


# ── SDS-005 / SDS-006: Report generation ─────────────────────────────────────


class TestReportGenerator:
    """SDS-005 and SDS-006 — report content for success and failure paths."""

    @pytest.mark.req("SDS-005")
    def test_success_report_returns_bytes(self):
        """A success report returns bytes."""
        gen = ReportGenerator()
        report = gen.generate({"A": 12.0, "B": 5.5, "MCP": 54.2})
        assert isinstance(report, bytes)

    @pytest.mark.req("SDS-005")
    def test_success_report_contains_mcp(self):
        """A success report includes the MCP value."""
        gen = ReportGenerator()
        report = gen.generate({"A": 12.0, "B": 5.5, "MCP": 54.2})
        assert b"MCP" in report
        assert b"SUCCESS" in report

    @pytest.mark.req("SDS-006")
    def test_failure_report_contains_reason(self):
        """A failure report includes the failure reason."""
        gen = ReportGenerator()
        report = gen.generate({"reason": "Oblique view detected"}, status="failure")
        assert b"FAILED" in report
        assert b"Oblique view detected" in report

    @pytest.mark.req("SDS-006")
    def test_invalid_status_raises_value_error(self):
        """An invalid status string raises ValueError."""
        gen = ReportGenerator()
        with pytest.raises(ValueError, match="status must be"):
            gen.generate({}, status="unknown")

    @pytest.mark.req("SDS-006")
    def test_failure_report_does_not_contain_mcp(self):
        """A failure report does not include an MCP value."""
        gen = ReportGenerator()
        report = gen.generate({"reason": "model error"}, status="failure")
        assert b"MCP:" not in report
