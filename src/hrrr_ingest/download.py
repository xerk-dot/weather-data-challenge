"""HRRR data download from AWS S3."""

import boto3
import botocore
import tempfile
from pathlib import Path
from typing import Optional
import logging

from config import HRRR_BUCKET

logger = logging.getLogger(__name__)

def get_s3_client():
    """Get an anonymous S3 client."""
    return boto3.client('s3', config=botocore.config.Config(signature_version=botocore.UNSIGNED))

def check_file_exists(date: str, forecast_hour: int) -> bool:
    """Check if HRRR file exists in S3."""
    s3 = get_s3_client()
    s3_key = f"hrrr.{date}/conus/hrrr.t06z.wrfsfcf{forecast_hour:02d}.grib2"
    logger.info(f"Checking for file: s3://{HRRR_BUCKET}/{s3_key}")
    
    try:
        s3.head_object(Bucket=HRRR_BUCKET, Key=s3_key)
        return True
    except Exception as e:
        logger.info(f"File not found: {str(e)}")
        return False

def download_grib_file(date: str, forecast_hour: int) -> Optional[Path]:
    """Download HRRR GRIB2 file from S3 to a temporary file."""
    s3 = get_s3_client()
    s3_key = f"hrrr.{date}/conus/hrrr.t06z.wrfsfcf{forecast_hour:02d}.grib2"
    logger.info(f"Attempting to download: s3://{HRRR_BUCKET}/{s3_key}")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.grib2') as tmp:
            # Download file
            s3.download_file(HRRR_BUCKET, s3_key, tmp.name)
            logger.info(f"Successfully downloaded {s3_key}")
            return Path(tmp.name)
    except Exception as e:
        logger.error(f"Failed to download {s3_key}: {str(e)}")
        return None 