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
    import pandas as pd
    import lux
    import luxwidget
    import matplotlib
    import altair
    import platform

    df = pd.DataFrame(
        [
            ("python", platform.python_version()),
            ("lux", lux.__version__),
            ("pandas", pd.__version__),
            ("luxwidget", luxwidget.__version__),
            ("matplotlib", matplotlib.__version__),
            ("altair", altair.__version__),
        ],
        columns=["", "Version"],
    )

    str_rep = df.to_string(index=False)

    if return_string:
        return str_rep
    else:
        print(str_rep)


if __name__ == "__main__":
    show_versions()
