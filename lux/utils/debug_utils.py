import json
from pathlib import Path
import re
import subprocess
import typing as tp


def show_versions():
    """
    Prints the versions of the principal packages used by Lux for debugging purposes.
    """
    import pandas as pd
    import lux
    import luxwidget
    import matplotlib
    import altair

    df = pd.DataFrame(
        [
            ("lux", lux.__version__),
            ("pandas", pd.__version__),
            ("luxwidget", luxwidget.__version__),
            ("matplotlib", matplotlib.__version__),
            ("altair", altair.__version__),
        ],
        columns=["Package", "Version"],
    )

    print(df.to_string(index=False))


def notebook_enabled() -> tp.Tuple[bool, str]:
    status, nbextension_list = subprocess.getstatusoutput("jupyter nbextension list")

    if status != 0:
        return False, "Failed to run 'jupyter nbextension list'"

    match = re.findall(r"config dir:(.*)\n", nbextension_list)

    if match:
        config_dir = match[0].strip()
    else:
        return False, "No 'config dir' found in 'jupyter nbextension list'"

    notebook_json = Path(config_dir) / "notebook.json"

    if not notebook_json.exists():
        return False, f"'{notebook_json}' does not exist"

    extensions = json.loads(notebook_json.read_text())

    if "load_extensions" not in extensions:
        return False, "'load_extensions' not in 'notebook.json'"
    elif "luxwidget/extension" not in extensions["load_extensions"]:
        return False, "'luxwidget/extension' not in 'load_extensions'"

    extension_enabled = extensions["load_extensions"]["luxwidget/extension"]

    if not extension_enabled:
        return False, "luxwidget is installed but not enabled"

    return True, ""


def lab_enabled() -> tp.Tuple[bool, str]:
    status_str, lab_list = subprocess.getstatusoutput("jupyter labextension list")

    if status_str != 0:
        return False, "Failed to run 'jupyter labextension list'"

    match = re.findall(r"luxwidget (\S+) (\S+) (\S+)", lab_list)

    if match:
        version_str, enabled_str, status_str = (_strip_ansi(s) for s in match[0])
    else:
        return False, "'luxwidget' not found in 'jupyter labextension list'"

    if enabled_str != "enabled":
        enabled_str = re.sub(r"\033\[(\d|;)+?m", "", enabled_str)
        return False, f"luxwidget is installed but currently '{enabled_str}'"

    if status_str != "OK":
        return False, f"luxwidget is installed but currently '{status_str}'"

    return True, ""


def is_lab_notebook():
    import re
    import psutil

    cmd = psutil.Process().parent().cmdline()

    return any(re.search("jupyter-lab", x) for x in cmd)


def check_luxwidget_enabled():

    # get the ipython shell
    import IPython

    ip = IPython.get_ipython()

    # return if the shell is not available
    if ip is None:
        return

    if is_lab_notebook():
        enabled, msg = lab_enabled()
    else:
        enabled, msg = notebook_enabled()

    if not enabled:
        print(f"WARNING: luxwidget is not enabled. Got: {msg}")


def _strip_ansi(source):
    return re.sub(r"\033\[(\d|;)+?m", "", source)


if __name__ == "__main__":
    check_luxwidget_enabled()
