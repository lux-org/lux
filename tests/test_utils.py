from lux.utils.utils import patch
import pandas as pd


class TestUtils:
    def test_patch(self):
        N = 0
        DataFrame = pd.DataFrame

        @patch(DataFrame)
        @property
        def _constructor(self):
            def new_constructor(*args, **kwargs):
                nonlocal N
                N += 1
                return DataFrame(*args, **kwargs)

            return new_constructor

        df = pd.DataFrame()._constructor({"a": [1, 2, 3]})

        assert N == 1
        assert hasattr(df, "a")
        assert df.a.tolist() == [1, 2, 3]


if __name__ == "__main__":
    TestUtils().test_patch()
