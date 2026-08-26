import open_local_ai


def test_package_exposes_development_version() -> None:
    assert open_local_ai.__version__ == "0.1.0.dev0"
