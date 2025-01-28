"""Hooks for pyinstaller."""

import shutil
from pathlib import Path

from poetry_pyinstaller_plugin.plugin import PyInstallerPluginHook


def pre_build(interface: PyInstallerPluginHook) -> None:
    """
    Pyinstaller pre build hook. Build local documentation.

    Parameters
    ----------
    interface : PyInstallerPluginHook
        Access to PyInstaller.
    """
    mkdoc_file = Path("mkdocs.yml")
    if not mkdoc_file.exists():
        interface.write_line("  - <b>No docs to build.</b>")
        return

    interface.write_line("  - <b>Building local docs</b>")

    test_group = interface.poetry.package._dependency_groups["docs"]  # noqa: SLF001
    for req in test_group.dependencies:
        pip_r = req.base_pep_508_name_resolved.replace(" (", "").replace(")", "")
        interface.write_line(f"    - Installing <c1>{req}</c1>")
        interface.run_pip(
            "install",
            "--disable-pip-version-check",
            "--ignore-installed",
            "--no-input",
            pip_r,
        )

    interface.run("poetry", "run", "mkdocs", "build", "--no-directory-urls")
    interface.write_line("    - <fg=green>Docs built</>")


def clean_dir(dir: str, interface: PyInstallerPluginHook) -> None:
    """
    Clean up directory and print message, but only if it exists.

    Parameters
    ----------
    dir : str
        Directory to clean up.
    interface : PyInstallerPluginHook
        Access to PyInstaller.
    """
    check = Path("dist", "pyinstaller", interface.platform, dir)
    if check.exists() and check.is_dir():
        shutil.rmtree(check)
        interface.write_line(f"    - Removed {check} directory")


def post_build(interface: PyInstallerPluginHook) -> None:
    """
    Pyinstaller post build hook. Remove generated folders.

    Parameters
    ----------
    interface : PyInstallerPluginHook
        Access to PyInstaller.
    """
    clean_dir("build", interface)
    clean_dir("site", interface)
