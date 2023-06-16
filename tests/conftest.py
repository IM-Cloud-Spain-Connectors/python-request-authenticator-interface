#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from logging import LoggerAdapter
from typing import Callable, Dict, Optional
from unittest.mock import patch

import pytest
from starlette.datastructures import Headers, URL
from starlette.requests import Request
from rndi.authentication.starlette.contract import CredentialsRepository


@pytest.fixture
def make_credential_repository():
    def __(override: Optional[Dict[str, Callable]] = None) -> CredentialsRepository:
        default_methods = {}
        if override is not None:
            default_methods.update(override)

        with patch('rndi.authentication.starlette.contract.CredentialsRepository') as repository:
            repository.get = default_methods.get('get', lambda key: None)
        return repository

    return __


@pytest.fixture
def make_logger():
    def __(overrides: Optional[Dict[str, Callable[[str], None]]] = None) -> LoggerAdapter:
        default_methods = {}
        if overrides is not None:
            default_methods.update(overrides)

        with patch('logging.LoggerAdapter') as logger:
            logger.info = default_methods.get('info', print)
            logger.warning = default_methods.get('warning', print)
            logger.error = default_methods.get('error', print)
            logger.debug = default_methods.get('debug', print)
            logger.exception = default_methods.get('exception', print)
        return logger

    return __


@pytest.fixture
def make_request():
    def __(method: str, location: str, headers: Optional[Dict[str, str]] = None, _: Optional[any] = None) -> Request:
        url = URL(location)

        default_headers = {
            'host': url.hostname,
            'accept': '*/*',
        }
        if headers is not None:
            default_headers.update(headers)
        headers = Headers(headers)

        # https://www.encode.io/articles/working-with-http-requests-in-asgi
        return Request({
            "type": "http",
            "http_version": "1.1",
            "method": method,
            "scheme": url.scheme,
            "path": url.path,
            "query_string": url.query,
            "headers": headers.raw,
            "server": (url.hostname, 443 if url.scheme == 'https' else 80),
        })

    return __
