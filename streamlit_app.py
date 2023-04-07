import streamlit as st

from streamlit_ketcher import st_ketcher

st.set_page_config(layout="wide")
st.title("`streamlit-ketcher`")

st.header("Component with user input")
DEFAULT_MOL = (
    r"C[N+]1=CC=C(/C2=C3\C=CC(=N3)/C(C3=CC=CC(C(N)=O)=C3)=C3/C=C/C(=C(\C4=CC=[N+]"
    "(C)C=C4)C4=N/C(=C(/C5=CC=CC(C(N)=O)=C5)C5=CC=C2N5)C=C4)N3)C=C1"
)
with st.echo():
    molecule = st.text_input("Molecule", DEFAULT_MOL)
    smile_code = st_ketcher(molecule)
    st.markdown(f"Smile code: ``{smile_code}``")

st.write("---")

st.header("Components with custom height")
with st.echo():
    st_ketcher("CCO", height=400)
    st_ketcher("CCO", height=800)

st.header("Component with `molfile` format")
with st.echo():
    molfile = st_ketcher(molecule_format="MOLFILE")
    st.markdown("molfile:")
    st.code(molfile)
