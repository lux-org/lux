import lux


class TestDebugUtils:
    def test_show_info(self):

        versions = lux.show_versions(return_string=True)

        assert versions is not None

        assert "python" in versions
        assert "lux" in versions
        assert "pandas" in versions
        assert "luxwidget" in versions
        assert "matplotlib" in versions
        assert "altair" in versions


if __name__ == "__main__":
    TestDebugUtils().test_show_info()
