from pathlib import Path


ROOT_DIRECTORY = Path(__file__).parent.parent.absolute()


def pytest_sessionstart(session):
    (ROOT_DIRECTORY / "streamlit_ketcher" / "frontend").mkdir(exist_ok=True)
