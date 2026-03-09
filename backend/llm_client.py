"""
LLM Client for Amazon Bedrock Integration

This module provides an LLM client that interfaces with Amazon Bedrock
using boto3. It includes timeout handling, fallback mechanisms, and usage tracking.

Requirements:
- 13.1: Use Template_Response for simple greetings without Bedrock
- 13.2: Invoke Bedrock LLM for complex reasoning
- 13.3: Use boto3 with Bedrock runtime
- 13.4: Use meta.llama3-8b-instruct-v1:0 model
- 13.5: Set 3-second timeout for LLM calls
- 13.6: Cancel request and use fallback on timeout
- 13.7: Log timeout events
"""

import asyncio
import logging
import json
from typing import Optional
import boto3

logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM Client for Amazon Bedrock integration.
    
    Provides async interface to Bedrock LLM with timeout handling,
    fallback mechanisms, and usage tracking.
    """
    
    def __init__(
        self,
        aws_access_key: str,
        aws_secret_key: str,
        region: str = "us-east-1",
        model: str = "meta.llama3-8b-instruct-v1:0",
        timeout: int = 3
    ):
        """
        Initialize LLM Client.
        
        Args:
            aws_access_key: AWS access key ID
            aws_secret_key: AWS secret access key
            region: AWS region (default: us-east-1)
            model: Model ID (default: meta.llama3-8b-instruct-v1:0)
            timeout: Timeout in seconds (default: 3)
        """
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        self.model = model
        self.timeout = timeout
        self.call_count = 0
        self.timeout_count = 0
        
        logger.info(f"LLM Client initialized with model: {model}, timeout: {timeout}s")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate response from LLM with timeout handling.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (default: 0.7)
            
        Returns:
            Generated response text, or None if timeout occurs
        """
        try:
            # Build prompt (Llama 3 chat format)
            if system_prompt:
                full_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            else:
                full_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            
            # Prepare request body
            body = json.dumps({
                "prompt": full_prompt,
                "max_gen_len": 256,  # Reduced for concise responses
                "temperature": temperature,
                "top_p": 0.9
            })
            
            # Log invocation
            self.call_count += 1
            logger.info(f"[LLM Agent] invoking bedrock (call #{self.call_count})")
            
            # Define sync function to call
            def _invoke():
                return self.client.invoke_model(
                    modelId=self.model,
                    body=body
                )
            
            # Call LLM with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(_invoke),
                timeout=self.timeout
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            if 'generation' not in response_body:
                logger.error(f"[LLM Agent] error: No generation in response: {response_body}")
                return None
            
            result = response_body['generation'].strip()
            
            if not result:
                logger.error("[LLM Agent] error: Empty generation")
                return None
            
            logger.info(f"[LLM Agent] response received ({len(result)} chars)")
            return result
            
        except asyncio.TimeoutError:
            self.timeout_count += 1
            logger.warning(
                f"[LLM Agent] timeout after {self.timeout}s "
                f"(timeout #{self.timeout_count})"
            )
            return None
            
        except Exception as e:
            logger.error(f"[LLM Agent] error: {e}")
            return None
    
    def get_usage_stats(self) -> dict:
        """
        Get LLM usage statistics.
        
        Returns:
            Dictionary with usage statistics
        """
        return {
            "total_calls": self.call_count,
            "timeouts": self.timeout_count,
            "success_rate": (
                (self.call_count - self.timeout_count) / self.call_count * 100
                if self.call_count > 0 else 0
            )
        }
    
    def log_usage_stats(self) -> None:
        """Log usage statistics to terminal."""
        stats = self.get_usage_stats()
        logger.info(
            f"[LLM Agent] Usage Stats - "
            f"Calls: {stats['total_calls']}, "
            f"Timeouts: {stats['timeouts']}, "
            f"Success Rate: {stats['success_rate']:.1f}%"
        )
