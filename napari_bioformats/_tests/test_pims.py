from pathlib import Path

import napari_bioformats
import numpy as np
import pytest
from napari_bioformats import napari_get_reader
from ome_types import OME

root = Path(napari_bioformats.__file__).parent.parent
data = root / "sample_data"


@pytest.mark.parametrize("fname", data.iterdir(), ids=lambda x: x.stem)
def test_reader(fname):
    reader = napari_get_reader(str(fname))
    assert callable(reader)
    ((data, meta),) = reader(fname)
    assert isinstance(data, np.ndarray)
    assert isinstance(meta["metadata"](), OME)
