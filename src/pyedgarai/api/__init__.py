"""
PyEdgarAI API Package

This package contains the Flask-OpenAPI3 web API for PyEdgarAI.

Modules:
- server: Main Flask application with all endpoints
- schemas: Pydantic models for request/response validation
"""

from .server import app

__all__ = ['app']
