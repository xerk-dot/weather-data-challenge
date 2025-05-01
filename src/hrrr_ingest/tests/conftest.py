import pytest
import os
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    test_dir = Path(__file__).parent / "data"
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup after tests
    shutil.rmtree(test_dir)

@pytest.fixture
def sample_points_file(test_data_dir):
    """Create a sample points file for testing."""
    points_file = test_data_dir / "sample_points.txt"
    points_file.write_text("""31.006900,-88.010300
31.756900,-106.375000
32.583889,-86.283060
32.601700,-87.781100
32.618900,-86.254800
33.255300,-87.449500
33.425878,-86.337550
33.458665,-87.356820
33.784500,-86.052400""")
    return str(points_file)

@pytest.fixture
def mock_grib_file(test_data_dir):
    """Create a mock GRIB file for testing."""
    grib_file = test_data_dir / "mock.grib2"
    # Create an empty file for testing
    grib_file.touch()
    return str(grib_file) 