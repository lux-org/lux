import lux


class TestDebugUtils:
    def test_debug_info(self):

        versions = lux.debug_info(return_string=True)

        assert versions is not None

        assert "python" in versions
        assert "lux" in versions
        assert "pandas" in versions
        assert "luxwidget" in versions
        assert "matplotlib" in versions
        assert "altair" in versions


if __name__ == "__main__":
    TestDebugUtils().test_debug_info()
