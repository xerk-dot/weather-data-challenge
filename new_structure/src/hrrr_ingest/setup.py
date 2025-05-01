from setuptools import setup, find_packages

setup(
    name="hrrr-ingest",
    version="0.1.0",
    packages=find_packages(include=['hrrr_ingest', 'hrrr_ingest.*']),
    install_requires=[
        "click>=8.0.0",
        "duckdb>=0.9.0",
        "boto3>=1.26.0",
        "xarray>=2023.1.0",
        "cfgrib>=0.9.10.4",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        'console_scripts': [
            'hrrr-ingest=hrrr_ingest.cli:main',
        ],
    },
) 