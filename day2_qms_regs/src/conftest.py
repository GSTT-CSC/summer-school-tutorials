"""
Auto-propagate @pytest.mark.req("SDS-XXX") into JUnit XML properties
so that rdm can trace tests back to design-specification items.
"""

import pytest


@pytest.fixture(autouse=True)
def _record_req_mark(request, record_property):
    marker = request.node.get_closest_marker("req")
    if marker:
        for req_id in marker.args:
            record_property("REQ", req_id)
