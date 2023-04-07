import socket
import subprocess
import sys
from contextlib import closing
from pathlib import Path

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
    streamlit_app_path = ROOT_DIRECTORY / "e2e" / "apps" / "basic_example.py"
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


def test_should_return_user_input(page: Page, streamlit_app: str, assert_snapshot):
    page.goto(streamlit_app)

    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()
    frame_0 = page.frame_locator(
        'iframe[title="streamlit_ketcher\\.streamlit_ketcher"]'
    )

    # Wait to Ketcher to load
    frame_0.get_by_role("button", name="Rectangle Selection (Esc)").click()

    # Draw benzene
    frame_0.get_by_role("button", name="Benzene (T)").click()
    frame_0.locator("svg").filter(has_text="Created with Raphaël 2.3.0").click()
    frame_0.get_by_role("button", name="Rectangle Selection (Esc)").click()

    # Assert benzene is visible
    assert_snapshot(
        frame_0.locator("css=body").screenshot(), "test_should_return_user_input.png"
    )

    # Assert output contains benzen
    frame_0.get_by_role("button", name="Apply").click()
    expect(page.get_by_text("Smile code")).to_have_text("Smile code: C1C=CC=CC=1")


def test_should_render_user_input(page: Page, streamlit_app: str, assert_snapshot):
    page.goto(streamlit_app)

    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()
    page.get_by_role("textbox", name="Molecule").click()
    page.get_by_role("textbox", name="Molecule").fill("CCO")
    page.get_by_role("textbox", name="Molecule").press("Enter")

    frame_0 = page.frame_locator(
        'iframe[title="streamlit_ketcher\\.streamlit_ketcher"]'
    )

    # Wait to Ketcher to load
    frame_0.get_by_role("button", name="Rectangle Selection (Esc)").click()
    assert_snapshot(
        frame_0.locator("css=body").screenshot(), "test_should_render_user_input.png"
    )

    # Assert output contains user input
    expect(page.get_by_text("Smile code")).to_have_text("Smile code: CCO")

    # Clear output
    frame_0.get_by_role("button", name="Reset").click()
    page.get_by_role("img", name="Running...").is_hidden()
    # Wait for the value to be set in Ketcher.
    frame_0.get_by_role("button", name="Rectangle Selection (Esc)").click()
    # Pass value to Streamlit
    frame_0.get_by_role("button", name="Apply").click()
    page.get_by_role("img", name="Running...").is_hidden()

    # Assert output is empty
    expect(page.get_by_text("Smile code")).to_have_text("Smile code: ````")
