import socket
import subprocess
import sys
from contextlib import closing
from pathlib import Path
from time import sleep

import pytest

from playwright.sync_api import Page, expect
import requests

from requests.adapters import HTTPAdapter, Retry

ROOT_DIRECTORY = Path(__file__).parent.parent.absolute()


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def create_http_session():
    s = requests.Session()

    retries = Retry(total=5, backoff_factor=0.1)
    s.mount("http://", HTTPAdapter(max_retries=retries))

    return s


@pytest.fixture(autouse=True, scope="session")
def streamlit_app():
    streamlit_app_path = ROOT_DIRECTORY / "e2e" / "apps" / "dearomatize.py"
    server_port = find_free_port()

    with subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(streamlit_app_path),
            f"--server.port={server_port}",
            "--server.headless=true",
        ]
    ) as process1:
        server_url = f"http://localhost:{server_port}"
        try:
            # Wait for webserver
            with create_http_session() as http_session:
                assert http_session.get(server_url + "/_stcore/health").text == "ok"
            yield server_url
        finally:
            process1.kill()

@pytest.mark.parametrize("arom_dearom", [("O=C(C)Oc1ccccc1C(=O)O", "O=C(OC1C(C(O)=O)=CC=CC=1)C")])
def test_should_dearomatize(page: Page, streamlit_app: str, assert_snapshot, arom_dearom):

    input_smi, output_smi = arom_dearom

    page.goto(streamlit_app)

    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()

    page.get_by_role("textbox", name="Molecule").click()
    page.get_by_role("textbox", name="Molecule").fill(input_smi)
    page.get_by_role("textbox", name="Molecule").press("Enter")

    frame_0 = page.frame_locator(
        'iframe[title="streamlit_ketcher\\.streamlit_ketcher"]'
    )

    # NOTE: there has to be a better way to wait for the image to render
    sleep(10)

    assert_snapshot(
        frame_0.locator("css=body").screenshot(), "test_should_dearomatize.png"
    )

    # trigger the dearomatization
    frame_0.get_by_role("button", name="Apply").click()
    page.get_by_role("img", name="Running...").is_hidden()

    # Assert output contains user input
    expect(page.get_by_text("Smile code")).to_have_text(f"Smile code: {output_smi}")