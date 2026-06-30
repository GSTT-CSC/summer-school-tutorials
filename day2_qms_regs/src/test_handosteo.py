"""
HandOsteo unit tests — worked solution (SDS-001 and SDS-002 only).

The completed version of the template in QMS_testing_and_validation.ipynb: the
same four tests and the same make_dataset() mock, but with the two placeholders
filled in with real assertions. Each test is linked to the System Design Spec it
verifies with @pytest.mark.sds(...), which feeds the unit-test traceability
record (day2_data/release/unit_test_record.md).

  - SDS-001: DICOM input/modality validation  (DicomLoader)
  - SDS-002: image view classifier            (ViewClassifier)

The two rejection tests FAIL against the buggy stub on purpose — that is
verification catching the deliberate bugs in src/handosteo.py.

Run with:
    pytest src/test_handosteo.py -v
"""

from __future__ import annotations

import os
import sys

import pydicom
import pydicom.uid
import pytest
from pydicom.dataset import FileMetaDataset

try:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
except NameError:
    # Running inside a notebook (e.g. %load): __file__ is undefined; the
    # notebook's working directory is already the project root.
    project_root = os.path.abspath(".")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.handosteo import DicomLoader, ViewClassifier


def make_dataset(modality="CR", view="AP"):
    """Build a minimal in-memory DICOM to use as a mock pipeline input."""
    fm = FileMetaDataset()
    fm.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    fm.MediaStorageSOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
    fm.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    ds = pydicom.FileDataset("", {}, file_meta=fm, preamble=b"\0" * 128)
    ds.Modality = modality
    ds.ViewPosition = view
    return ds


def save_mock(ds, tmp_path):
    """Write a mock dataset to a temp .dcm and return its path (for DicomLoader)."""
    path = tmp_path / "mock.dcm"
    ds.save_as(path)
    return str(path)


class TestHandOsteo:
    # ── SDS-001: DicomLoader accepts supported modalities, rejects the rest ──
    # load() reads from a path, so we save our mock to pytest's tmp_path first —
    # no dependency on any committed fixture file.
    @pytest.mark.sds("SDS-001")
    def test_supported_modality_accepted(self, tmp_path):
        path = save_mock(make_dataset(modality="CR"), tmp_path)
        ds = DicomLoader().load(path)
        assert ds.Modality in ("CR", "DX")

    @pytest.mark.sds("SDS-001")
    def test_wrong_modality_rejected(self, tmp_path):
        path = save_mock(make_dataset(modality="CT"), tmp_path)
        with pytest.raises(ValueError):
            DicomLoader().load(path)

    # ── SDS-002: ViewClassifier accepts AP/PA, rejects everything else ──
    # classify() takes a dataset directly, so the mock goes straight in.
    @pytest.mark.sds("SDS-002")
    def test_ap_view_accepted(self):
        ds = make_dataset(view="AP")
        assert ViewClassifier().classify(ds) in ("AP", "PA")

    @pytest.mark.sds("SDS-002")
    def test_oblique_view_rejected(self):
        ds = make_dataset(view="OBL")
        with pytest.raises(ValueError):
            ViewClassifier().classify(ds)


if __name__ == "__main__":
    import ipytest

    ipytest.run("-qq")
