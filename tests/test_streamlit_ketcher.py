import re
import unittest.mock

from streamlit_ketcher import st_ketcher
import pytest


# adding the dearomatize parameter to the tests is probably excessive
# wanted to be sure I didn't break anything somehow

@unittest.mock.patch("streamlit_ketcher._render_component")
@pytest.mark.parametrize("dearomatize_on_load", [True, False])
def test_render_empty(mock_render_component, dearomatize_on_load):
    st_ketcher(dearomatize_on_load=dearomatize_on_load)
    mock_render_component.assert_called_once_with(
        molecule="", height=500, molecule_format="SMILES", key=None, default="", dearomatize_on_load=dearomatize_on_load
    )


@unittest.mock.patch("streamlit_ketcher._render_component")
@pytest.mark.parametrize("dearomatize_on_load", [True, False])
def test_render_all_parameters(mock_render_component, dearomatize_on_load):
    st_ketcher(value="CCO", height=600, molecule_format="SMILES", key="key", dearomatize_on_load=dearomatize_on_load)
    mock_render_component.assert_called_once_with(
        molecule="CCO", height=600, molecule_format="SMILES", key="key", default="CCO", dearomatize_on_load=dearomatize_on_load
    )


@unittest.mock.patch("streamlit_ketcher._render_component")
@pytest.mark.parametrize("molecule_format", ["SMILES", "MOLFILE"])
@pytest.mark.parametrize("dearomatize_on_load", [True, False])
def test_render_molecule_format(mock_render_component, molecule_format, dearomatize_on_load):
    st_ketcher(molecule_format=molecule_format, dearomatize_on_load=dearomatize_on_load)
    mock_render_component.assert_called_once_with(
        molecule="", height=500, molecule_format=molecule_format, key=None, default="", dearomatize_on_load=dearomatize_on_load
    )


@unittest.mock.patch("streamlit_ketcher._render_component")
def test_invalid_molecule_format(mock_render_component):
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Unsupported value for molecule format: 'INVALID'. "
            "Supported values: SMILES, MOLFILE"
        ),
    ):
        st_ketcher(molecule_format="INVALID")
