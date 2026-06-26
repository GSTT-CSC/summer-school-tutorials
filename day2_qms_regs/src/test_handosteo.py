"""
HandOsteo unit tests — worked solution (SDS-001 and SDS-002 only).

Focused on the two design specs the testing tutorial targets:
  - SDS-001: DICOM input/modality validation  (DicomLoader)
  - SDS-002: image view classifier            (ViewClassifier)

Mixes in-memory mocked datasets (pure unit tests) with the real fake DICOMs in
day2_data/xray/dicom/ (lightweight integration tests).

Run with:
    pytest src/test_handosteo.py -v
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pydicom
import pydicom.uid
import pytest
from pydicom.dataset import FileMetaDataset

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.constants import ALLOWED_MODALITIES, SUPPORTED_VIEWS
from src.handosteo import DicomLoader, ViewClassifier

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


# ── SDS-001: DICOM input/modality validation ─────────────────────────────────


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

    def test_load_non_dicom_file_raises_value_error(self, tmp_path):
        """A plain text file is rejected with ValueError."""
        bad_file = tmp_path / "not_a_dicom.txt"
        bad_file.write_text("hello world")
        loader = DicomLoader()
        with pytest.raises(ValueError, match="Not a valid DICOM"):
            loader.load(str(bad_file))

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

    def test_wrong_modality_file_rejected(self):
        """Real wrong-modality (CT) DICOM file is rejected with ValueError."""
        loader = DicomLoader()
        with pytest.raises(ValueError):
            loader.load(str(DICOM_DIR / "CT_1.dcm"))


# ── SDS-002: view classifier ──────────────────────────────────────────────────


@pytest.mark.req("SDS-002")
class TestViewClassifier:
    """SDS-002 — only process AP or PA images; reject oblique views."""

    @pytest.mark.parametrize("view", list(SUPPORTED_VIEWS))
    def test_supported_view_is_accepted(self, view):
        """AP and PA views are accepted and returned as-is."""
        clf = ViewClassifier()
        ds = _make_dataset(view=view)
        assert clf.classify(ds) == view

    @pytest.mark.parametrize("view", ["OBL", "OBLIQUE", "LL", "RL", "LAT"])
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
        """Real oblique DICOM (ViewPosition OBL) is rejected with ValueError."""
        clf = ViewClassifier()
        ds = pydicom.dcmread(str(DICOM_DIR / "Ob_1.dcm"))
        with pytest.raises(ValueError):
            clf.classify(ds)
