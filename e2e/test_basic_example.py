from pathlib import Path

import pytest

from playwright.sync_api import Page, expect

from e2e.e2e_utils import StreamlitRunner

ROOT_DIRECTORY = Path(__file__).parent.parent.absolute()
BASIC_EXAMPLE_FILE = ROOT_DIRECTORY / "e2e" / "apps" / "basic_example.py"


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(BASIC_EXAMPLE_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


def test_should_return_user_input(page: Page, assert_snapshot):
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


def test_should_render_user_input(page: Page, assert_snapshot):
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
