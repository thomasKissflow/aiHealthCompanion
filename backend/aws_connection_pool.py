"""
AWS Connection Pool
Manages reusable boto3 clients for AWS services
"""
import boto3
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class AWSConnectionPool:
    """
    Connection pool for AWS services (Transcribe, Polly, Bedrock)
    Implements client reuse and failure recovery
    """
    
    def __init__(
        self,
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
        region: Optional[str] = None
    ):
        """
        Initialize AWS Connection Pool
        
        Args:
            aws_access_key: AWS access key (defaults to env var)
            aws_secret_key: AWS secret key (defaults to env var)
            region: AWS region (defaults to env var)
        """
        self.aws_access_key = aws_access_key or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = aws_secret_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        
        # Client storage
        self._transcribe_client = None
        self._polly_client = None
        self._bedrock_runtime_client = None
        self._s3_client = None
        
        logger.info(f"AWS Connection Pool initialized for region: {self.region}")
    
    def get_transcribe_client(self):
        """
        Get or create Amazon Transcribe client
        
        Returns:
            boto3 Transcribe client
        """
        if self._transcribe_client is None:
            try:
                self._transcribe_client = boto3.client(
                    'transcribe',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.region
                )
                logger.info("Created new Transcribe client")
            except Exception as e:
                logger.error(f"Failed to create Transcribe client: {e}")
                raise
        
        return self._transcribe_client
    
    def get_polly_client(self):
        """
        Get or create Amazon Polly client
        
        Returns:
            boto3 Polly client
        """
        if self._polly_client is None:
            try:
                self._polly_client = boto3.client(
                    'polly',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.region
                )
                logger.info("Created new Polly client")
            except Exception as e:
                logger.error(f"Failed to create Polly client: {e}")
                raise
        
        return self._polly_client
    
    def get_bedrock_runtime_client(self):
        """
        Get or create Amazon Bedrock Runtime client
        
        Returns:
            boto3 Bedrock Runtime client
        """
        if self._bedrock_runtime_client is None:
            try:
                self._bedrock_runtime_client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.region
                )
                logger.info("Created new Bedrock Runtime client")
            except Exception as e:
                logger.error(f"Failed to create Bedrock Runtime client: {e}")
                raise
        
        return self._bedrock_runtime_client
    
    def _get_s3_client(self):
        """
        Get or create Amazon S3 client (for Transcribe)
        
        Returns:
            boto3 S3 client
        """
        if self._s3_client is None:
            try:
                self._s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.region
                )
                logger.info("Created new S3 client")
            except Exception as e:
                logger.error(f"Failed to create S3 client: {e}")
                raise
        
        return self._s3_client
    
    def recreate_client(self, service_name: str):
        """
        Recreate a client on failure
        
        Args:
            service_name: Name of the service ('transcribe', 'polly', 'bedrock-runtime', 's3')
        """
        logger.warning(f"Recreating {service_name} client due to failure")
        
        if service_name == 'transcribe':
            self._transcribe_client = None
            return self.get_transcribe_client()
        elif service_name == 'polly':
            self._polly_client = None
            return self.get_polly_client()
        elif service_name == 'bedrock-runtime':
            self._bedrock_runtime_client = None
            return self.get_bedrock_runtime_client()
        elif service_name == 's3':
            self._s3_client = None
            return self._get_s3_client()
        else:
            raise ValueError(f"Unknown service: {service_name}")
    
    def close_all(self):
        """Close all client connections"""
        self._transcribe_client = None
        self._polly_client = None
        self._bedrock_runtime_client = None
        self._s3_client = None
        logger.info("All AWS clients closed")


# Global connection pool instance
_connection_pool: Optional[AWSConnectionPool] = None


def get_connection_pool() -> AWSConnectionPool:
    """
    Get the global AWS connection pool instance
    
    Returns:
        AWSConnectionPool instance
    """
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = AWSConnectionPool()
    return _connection_pool
