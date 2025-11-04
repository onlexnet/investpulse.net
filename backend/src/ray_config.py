"""
Ray configuration for the ticker processing system.

This module provides configuration and initialization utilities for Ray
to set up the distributed processing environment.
"""

import ray
import os
from typing import Dict, Any, Optional


def get_ray_config() -> Dict[str, Any]:
    """
    Get Ray configuration based on environment variables and defaults.
    
    Returns:
        Dict[str, Any]: Ray configuration dictionary
    """
    config = {
        # Basic Ray configuration
        'address': os.getenv('RAY_ADDRESS', None),  # None for local cluster
        'namespace': os.getenv('RAY_NAMESPACE', 'ticker-processing'),
        
        # Resource configuration
        'num_cpus': int(os.getenv('RAY_NUM_CPUS', 0)),  # 0 = auto-detect
        'num_gpus': int(os.getenv('RAY_NUM_GPUS', 0)),
        'memory': int(os.getenv('RAY_MEMORY_MB', 0)) * 1024 * 1024 if os.getenv('RAY_MEMORY_MB') else None,
        
        # Logging configuration
        'log_to_driver': os.getenv('RAY_LOG_TO_DRIVER', 'true').lower() == 'true',
        'logging_level': os.getenv('RAY_LOGGING_LEVEL', 'INFO'),
        
        # Dashboard configuration
        'dashboard_host': os.getenv('RAY_DASHBOARD_HOST', '0.0.0.0'),
        'dashboard_port': int(os.getenv('RAY_DASHBOARD_PORT', 8265)),
        'include_dashboard': os.getenv('RAY_INCLUDE_DASHBOARD', 'true').lower() == 'true',
        
        # Object store configuration
        'object_store_memory': int(os.getenv('RAY_OBJECT_STORE_MEMORY_MB', 0)) * 1024 * 1024 if os.getenv('RAY_OBJECT_STORE_MEMORY_MB') else None,
        
        # Runtime environment
        'runtime_env': {
            'working_dir': os.getenv('RAY_WORKING_DIR', '.'),
            'pip': ['ray[default]', 'pandas', 'pyarrow'],
            'env_vars': {
                'PYTHONPATH': os.getenv('PYTHONPATH', ''),
            }
        }
    }
    
    # Remove None values
    return {k: v for k, v in config.items() if v is not None}


def initialize_ray(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Initialize Ray with the provided or default configuration.
    
    Args:
        config (Optional[Dict[str, Any]]): Ray configuration. If None, uses get_ray_config()
        
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    if config is None:
        config = get_ray_config()
    
    try:
        # Check if Ray is already initialized
        if ray.is_initialized():
            print("Ray is already initialized")
            return True
        
        # Initialize Ray
        ray.init(**config)
        
        print(f"Ray initialized successfully")
        print(f"Dashboard URL: http://{config.get('dashboard_host', 'localhost')}:{config.get('dashboard_port', 8265)}")
        print(f"Cluster resources: {ray.cluster_resources()}")
        
        return True
        
    except Exception as e:
        print(f"Failed to initialize Ray: {e}")
        return False


def shutdown_ray():
    """Shutdown Ray cluster gracefully."""
    try:
        if ray.is_initialized():
            ray.shutdown()
            print("Ray shutdown successfully")
        else:
            print("Ray was not initialized")
    except Exception as e:
        print(f"Error during Ray shutdown: {e}")


def get_cluster_info() -> Dict[str, Any]:
    """
    Get information about the current Ray cluster.
    
    Returns:
        Dict[str, Any]: Cluster information
    """
    if not ray.is_initialized():
        return {'error': 'Ray is not initialized'}
    
    try:
        return {
            'cluster_resources': ray.cluster_resources(),
            'available_resources': ray.available_resources(),
            'nodes': ray.nodes(),
            'namespace': ray.get_runtime_context().namespace,
            'node_id': ray.get_runtime_context().node_id.hex(),
        }
    except Exception as e:
        return {'error': f'Failed to get cluster info: {e}'}


# Default Ray configuration for development
DEVELOPMENT_CONFIG = {
    'num_cpus': 4,
    'num_gpus': 0,
    'log_to_driver': True,
    'logging_level': 'INFO',
    'include_dashboard': True,
    'dashboard_host': '0.0.0.0',
    'dashboard_port': 8265,
    'namespace': 'ticker-processing-dev'
}

# Default Ray configuration for production
PRODUCTION_CONFIG = {
    'log_to_driver': False,
    'logging_level': 'WARNING',
    'include_dashboard': True,
    'dashboard_host': '0.0.0.0',
    'dashboard_port': 8265,
    'namespace': 'ticker-processing-prod'
}