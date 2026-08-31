def pytest_configure(config) -> None:
    """Keep coverage enforcement on the complete default suite only."""
    if config.getoption("-m").strip() == "integration":
        coverage = config.pluginmanager.getplugin("_cov")
        if coverage is not None:
            coverage.options.cov_fail_under = 0
