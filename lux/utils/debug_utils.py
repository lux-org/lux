def show_versions():
    """
    Prints the versions of the principal packages used by Lux for debugging purposes.
    """
    import pandas as pd
    import lux
    import luxwidget
    import matplotlib
    import altair
import platform

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


if __name__ == "__main__":
    show_versions()
