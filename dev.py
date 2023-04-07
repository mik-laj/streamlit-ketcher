#!/usr/bin/env python

import argparse
import shlex
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


def cmd_py_distribute(args):
    run_verbose(
        [str(PYTHON_BIN), "setup.py", "bdist_wheel", "--universal", "sdist"],
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
    cmd_py_distribute(args)


def get_parser():
    parser = argparse.ArgumentParser(prog=__file__)
    subparsers = parser.add_subparsers(dest="subcommand", metavar="COMMAND")
    subparsers.required = True
    subparsers.add_parser(
        "py-create-venv", help="Create virtual environment for Python."
    ).set_defaults(func=cmd_py_create_venv)
    subparsers.add_parser(
        "py-distribution", help="Create Python distribution files in dist/."
    ).set_defaults(func=cmd_py_distribute)
    subparsers.add_parser("py-test", help="Run unit tests for python.").set_defaults(
        func=cmd_py_test
    )
    subparsers.add_parser("js-build", help="Build frontend.").set_defaults(
        func=cmd_js_build
    )
    js_lint_parser = subparsers.add_parser("js-format", help="Format frontend files")
    js_lint_parser.add_argument(
        "files", nargs=argparse.REMAINDER, help="Files to check"
    )
    js_lint_parser.set_defaults(func=cmd_js_format)
    subparsers.add_parser("js-test", help="Run unit tests for frontend.").set_defaults(
        func=lambda _: run_verbose(["yarn", "test"], cwd=FRONTEND_DIRECTORY)
    )
    subparsers.add_parser(
        "package", help='Build frontend and then run "py-distribution".'
    ).set_defaults(func=cmd_package)
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.subcommand != "py-create-venv":
        ensure_environment()
    if args.subcommand == "package" or args.subcommand.startswith("js-"):
        ensure_js_modules_installed()
    args.func(args)


if __name__ == "__main__":
    main()
