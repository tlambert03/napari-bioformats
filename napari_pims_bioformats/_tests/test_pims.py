from napari_pims_bioformats import napari_get_reader


def test_get_reader_pass():
    reader = napari_get_reader("fake.file")
    assert reader is None
