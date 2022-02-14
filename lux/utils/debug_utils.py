import json
from pathlib import Path
import re
import subprocess
import typing as tp

import re
import subprocess
from typing import Optional


def show_versions(return_string: bool = False) -> Optional[str]:
    """
    Prints the versions of the principal packages used by Lux for debugging purposes.
    Parameters
    ----------
    return_string: Whether to return the versions as a string or print them.
    Returns
    -------
    If return_string is True, returns a string with the versions else the versions
    are printed and None is returned.
    """
    import platform

    import altair
    import lux
    import luxwidget
    import matplotlib
    import pandas as pd

    header = "Package Versions\n----------------\n"
    jupyter_versions_str = subprocess.check_output(["jupyter", "--version"])
    jupyter_versions = re.findall(r"(\S+)\s+: (.+)\S*", jupyter_versions_str.decode("utf-8"))
    df = pd.DataFrame(
        [
            ("python", platform.python_version()),
            ("lux", lux.__version__),
            ("pandas", pd.__version__),
            ("luxwidget", luxwidget.__version__),
            ("matplotlib", matplotlib.__version__),
            ("altair", altair.__version__),
        ]
        + jupyter_versions,
        columns=["", "Version"],
    )

    str_rep = header + df.to_string(index=False, justify="left")

    if return_string:
        return str_rep
    else:
        print(str_rep)


def debug_info(return_string: bool = False) -> Optional[str]:
    """
    Prints all the informatation that could be useful for debugging purposes.
    Currently, this includes:

    * The versions of the packages used by Lux
    * Info about the current state of luxwidget

    Parameters
    ----------
    return_string: Whether to return the versions as a string or print them.

    Returns
    -------
    If return_string is True, returns a string with the debug info else the
    string will be printed and None is returned.
    """
    str_rep = show_versions(return_string=True)
    luxwidget_msg = check_luxwidget_enabled(return_string=True)

    assert str_rep is not None
    assert luxwidget_msg is not None
    header = "Widget Setup\n-------------\n"
    str_rep += "\n\n" + header + luxwidget_msg + "\n"

    if return_string:
        return str_rep
    else:
        print(str_rep)


def notebook_enabled() -> tp.Tuple[bool, str]:
    status, nbextension_list = subprocess.getstatusoutput("jupyter nbextension list")

    if status != 0:
        return False, "❌ Failed to run 'jupyter nbextension list'\n"

    match = re.findall(r"config dir:(.*)\n", nbextension_list)

    if match:
        config_dir = match[0].strip()
    else:
        return False, "❌ No 'config dir' found in 'jupyter nbextension list'\n"

    notebook_json = Path(config_dir) / "notebook.json"

    if not notebook_json.exists():
        return False, f"'{notebook_json}' does not exist\n"

    extensions = json.loads(notebook_json.read_text())

    if "load_extensions" not in extensions:
        return False, "❌ 'load_extensions' not in 'notebook.json'\n"
    elif "luxwidget/extension" not in extensions["load_extensions"]:
        return False, "❌ 'luxwidget/extension' not in 'load_extensions'\n"

    extension_enabled = extensions["load_extensions"]["luxwidget/extension"]

    if not extension_enabled:
        return False, "❌ luxwidget is installed but not enabled\n"

    return True, ""


def lab_enabled() -> tp.Tuple[bool, str]:
    status_str, lab_list = subprocess.getstatusoutput("jupyter labextension list")

    if status_str != 0:
        return (
            False,
            "❌ Failed to run 'jupyter labextension list'. Do you have Jupyter Lab installed in this environment?",
        )

    match = re.findall(r"luxwidget (\S+) (\S+) (\S+)", lab_list)

    if match:
        version_str, enabled_str, status_str = (_strip_ansi(s) for s in match[0])
    else:
        return False, "❌ 'luxwidget' not found in 'jupyter labextension list'\n"

    if enabled_str != "enabled":
        enabled_str = re.sub(r"\033\[(\d|;)+?m", "", enabled_str)
        return False, f"❌ luxwidget is installed but currently '{enabled_str}'\n"

    if status_str != "OK":
        return False, f"❌ luxwidget is installed but currently '{status_str}'\n"

    return True, ""


def is_lab_notebook():
    import re
    import psutil

    cmd = psutil.Process().parent().cmdline()

    return any(re.search("jupyter-lab", x) for x in cmd)


def check_luxwidget_enabled(return_string: bool = False) -> Optional[str]:
    # get the ipython shell
    import IPython

    ip = IPython.get_ipython()

    # return if the shell is not available
    if ip is None:
        return "❌ IPython shell note available.\nPlease note that Lux must be used within a notebook interface (e.g., Jupyter notebook, Jupyter Lab, JupyterHub, or VSCode)\n"
    is_lab = is_lab_notebook()

    if is_lab:
        msg = "✅ Jupyter Lab Running\n"
        enabled, emsg = lab_enabled()
        msg = msg + emsg
        if not enabled:
            msg += f"❌ WARNING: luxwidget is not enabled in Jupyter Lab."
            msg += "You may need to run the following code in your command line:\n"
            msg += "  jupyter labextension install @jupyter-widgets/jupyterlab-manager\n"
            msg += "  jupyter labextension install luxwidget"
        else:
            msg += "✅ luxwidget is enabled"

    else:
        msg = "✅ Jupyter Notebook Running\n"
        enabled, emsg = notebook_enabled()
        msg = msg + emsg
        if not enabled:
            msg += "❌ WARNING: luxwidget is not enabled in Jupyter Notebook.\n"
            msg += "You may need to run the following code in your command line:\n"
            msg += "  jupyter nbextension install --py luxwidget\n"
            msg += "  jupyter nbextension enable --py luxwidget"
        else:
            msg += "✅ luxwidget is enabled"

    if return_string:
        return msg


def _strip_ansi(source):
    return re.sub(r"\033\[(\d|;)+?m", "", source)


if __name__ == "__main__":
    check_luxwidget_enabled()
