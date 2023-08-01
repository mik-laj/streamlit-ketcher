#!/usr/bin/env python

import argparse
import os
import shlex
import shutil
import subprocess
from pathlib import Path

THIS_DIRECTORY = Path(__file__).parent.absolute()
FRONTEND_DIRECTORY = THIS_DIRECTORY / "frontend"
VENV_DIRECTORY = THIS_DIRECTORY / "venv"
PYTHON_BIN = VENV_DIRECTORY / "bin" / "python"


def run_verbose(cmd_args, *args, **kwargs):
    kwargs.setdefault("check", True)

    print(f"$ {shlex.join(cmd_args)}", flush=True)
    subprocess.run(cmd_args, *args, **kwargs)


def ensure_environment():
    try:
        subprocess.check_call(
            ["python", "-m", "venv", "--help"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        raise SystemExit("'venv' python module is not installed")

    if not PYTHON_BIN.exists():
        shell_cmd = shlex.join([str(__file__), "py-create-venv"])
        raise SystemExit(
            "The virtual environment is not exists.\n"
            "To create environment run:"
            f"   $ {shell_cmd}"
        )

    try:
        subprocess.check_call(
            ["node", "--version"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        raise SystemExit("'node' is not installed")

    try:
        subprocess.check_call(
            ["yarn", "--version"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        raise SystemExit("'yarn' is not installed")


def ensure_js_modules_installed():
    run_verbose(["yarn", "install"], cwd=FRONTEND_DIRECTORY)


def cmd_py_create_venv(args):
    run_verbose(["python", "-m", "venv", str(VENV_DIRECTORY)], cwd=THIS_DIRECTORY)
    run_verbose(
        [
            str(PYTHON_BIN),
            "-m",
            "pip",
            "install",
            "-r",
            str(THIS_DIRECTORY / "dev-requirements.txt"),
        ],
        cwd=THIS_DIRECTORY,
    )
    run_verbose(
        [
            str(PYTHON_BIN),
            "-m",
            "pip",
            "install",
            "--editable",
            ".",
        ],
        cwd=THIS_DIRECTORY,
    )


def cmd_py_build(args):
    shutil.rmtree((THIS_DIRECTORY / "dist"), ignore_errors=True)
    run_verbose(
        [str(PYTHON_BIN), "-m", "pip", "install", "--upgrade", "build"],
        cwd=THIS_DIRECTORY,
    )
    run_verbose(
        [str(PYTHON_BIN), "-m", "build"],
        cwd=THIS_DIRECTORY,
    )


def cmd_py_distribute(args):
    run_verbose(
        [str(PYTHON_BIN), "-m", "pip", "install", "--upgrade", "twine"],
        cwd=THIS_DIRECTORY,
    )

    run_verbose(
        [
            str(PYTHON_BIN),
            "-m",
            "twine",
            "upload",
            "--repository",
            args.repository,
            "dist/*",
        ],
        cwd=THIS_DIRECTORY,
    )


def cmd_py_test(args):
    app_frontend = THIS_DIRECTORY / "streamlit_ketcher" / "frontend"
    if not app_frontend.exists():
        app_frontend.mkdir()

    run_verbose([str(PYTHON_BIN), "-m", "pytest", "tests"], cwd=THIS_DIRECTORY)


def cmd_js_format(args):
    files = [
        str(Path(filepath).absolute().relative_to(FRONTEND_DIRECTORY))
        for filepath in args.files
    ]
    run_verbose(["yarn", "prettier", "--write", *files], cwd=FRONTEND_DIRECTORY)


def cmd_js_build(args):
    run_verbose(["yarn", "build"], cwd=FRONTEND_DIRECTORY)


def cmd_package(args):
    cmd_js_build(args)
    cmd_py_build(args)


def cmd_e2e_build_image(args):
    image_tag = (
        f"streamlit-ketcher:py-{args.python_version}-st-{args.streamlit_version}"
    )
    run_verbose(
        [
            "docker",
            "build",
            ".",
            f"--build-arg=STREAMLIT_VERSION={args.streamlit_version}",
            f"--build-arg=PYTHON_VERSION={args.python_version}",
            f"--tag={image_tag}",
            "--progress=plain",
        ],
        env={**os.environ, "DOCKER_BUILDKIT": "1"},
    )


def cmd_e2e_run(args):
    image_tag = (
        f"streamlit-ketcher:py-{args.python_version}-st-{args.streamlit_version}"
    )
    run_verbose(
        [
            "docker",
            "run",
            "--tty",
            "--volume",
            f"{THIS_DIRECTORY}/:/app/",
            # "--volume",
            # f"{THIS_DIRECTORY}/e2e:/app/e2e",
            # "--volume",
            # f"{THIS_DIRECTORY}/streamlit_app.py:/app/streamlit_app.py",
            image_tag,
            "pytest",
            "e2e",
            *args.rest,
        ]
    )


def get_parser():
    parser = argparse.ArgumentParser(prog=__file__)
    subparsers = parser.add_subparsers(dest="subcommand", metavar="COMMAND")
    subparsers.required = True
    # Command: py-create-venv
    subparsers.add_parser(
        "py-create-venv", help="Create virtual environment for Python."
    ).set_defaults(func=cmd_py_create_venv)
    # Command: py-build
    subparsers.add_parser(
        "py-build", help="Create Python distribution files in dist/."
    ).set_defaults(func=cmd_py_build)
    # Command: py-distribute
    py_distribute_parser = subparsers.add_parser(
        "py-distribute", help="Upload our package to PyPI"
    )
    py_distribute_parser.add_argument(
        "-r",
        "--repository",
        help=(
            "The repository (package index) to upload the package to. "
            "Should be a section in the config file (default: testpypi)."
        ),
        default="testpypi",
    )
    py_distribute_parser.set_defaults(func=cmd_py_distribute)
    # Command: py-test
    subparsers.add_parser("py-test", help="Run unit tests for python.").set_defaults(
        func=cmd_py_test
    )
    # Command: js-build
    subparsers.add_parser("js-build", help="Build frontend.").set_defaults(
        func=cmd_js_build
    )
    # Command: js-format
    js_lint_parser = subparsers.add_parser("js-format", help="Format frontend files")
    js_lint_parser.add_argument(
        "files", nargs=argparse.REMAINDER, help="Files to check"
    )
    js_lint_parser.set_defaults(func=cmd_js_format)
    # Command: js-test
    subparsers.add_parser("js-test", help="Run unit tests for frontend.").set_defaults(
        func=lambda _: run_verbose(["yarn", "test"], cwd=FRONTEND_DIRECTORY)
    )
    # Command: package
    subparsers.add_parser(
        "package", help='Build frontend and then create a WHL pacakge".'
    ).set_defaults(func=cmd_package)
    # Command: e2e-build-image
    e2e_build_image_parser = subparsers.add_parser(
        "e2e-build-image", help="Build docker image for E2E tests."
    )
    e2e_image_arguments(e2e_build_image_parser)
    e2e_build_image_parser.set_defaults(func=cmd_e2e_build_image)
    # Command: e2e-run-tests
    e2e_run_tests_parser = subparsers.add_parser(
        "e2e-run-tests", help="Run E2E tests in the docker."
    )
    e2e_image_arguments(e2e_run_tests_parser)
    e2e_run_tests_parser.add_argument("rest", nargs="*")
    e2e_run_tests_parser.set_defaults(func=cmd_e2e_run)

    return parser


def e2e_image_arguments(e2e_build_image):
    python_version = os.environ.get("PYTHON_VERSION", "3.10")

    e2e_build_image.add_argument(
        "--streamlit-version",
        default="latest",
        help="Streamlit version for which tests will be run.",
    )
    e2e_build_image.add_argument(
        "--python-version",
        default=python_version,
        help="Python version for which tests will be run.",
    )


def main():
    parser = get_parser()
    args = parser.parse_args()

    if not (args.subcommand == "py-create-venv" or args.subcommand.startswith("e2e-")):
        ensure_environment()
    if args.subcommand == "package" or args.subcommand.startswith("js-"):
        ensure_js_modules_installed()
    args.func(args)


if __name__ == "__main__":
    main()
