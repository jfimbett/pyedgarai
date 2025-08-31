"""Pytest configuration and fixtures."""
import pytest
import warnings


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their names and modules."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if "large_dataset" in item.name or "performance" in item.name:
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
def suppress_warnings():
    """Suppress common warnings during testing."""
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
    warnings.filterwarnings("ignore", message=".*requests.*")


@pytest.fixture
def apple_cik():
    """Apple Inc. CIK for testing."""
    return 320193


@pytest.fixture
def microsoft_cik():
    """Microsoft Corporation CIK for testing."""
    return 789019


@pytest.fixture
def sample_ciks():
    """List of sample CIKs for testing."""
    return [320193, 789019, 1652044]  # Apple, Microsoft, Alphabet


@pytest.fixture
def test_date_range():
    """Safe date range for testing."""
    return ('2023-01-01', '2023-01-31')
