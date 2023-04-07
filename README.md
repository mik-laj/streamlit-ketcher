# 🧪 Streamlit Ketcher


## Installation

```shell
pip install streamlit-ketcher
```

## Getting started

```python
import streamlit as st

from streamlit_ketcher import st_ketcher

molecule = st.text_input("Molecule", "CCO")
smile_code = st_ketcher(molecule)
st.markdown(f"Smile code: ``{smile_code}``")
```
