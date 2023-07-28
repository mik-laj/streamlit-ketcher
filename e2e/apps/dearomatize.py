import streamlit as st
from streamlit_ketcher import st_ketcher

molecule = st.text_input("Molecule")
smile_code = st_ketcher(molecule, dearomatize_on_load=True)
st.markdown(f"Smile code: ``{smile_code}``")
