#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from abc import ABC, abstractmethod
from logging import LoggerAdapter
from typing import Callable, Dict

from starlette.requests import Request


class RequestAuthenticator(ABC):
    @abstractmethod
    def authenticate(self, request: Request):
        """
        Authenticate the given request.

        :param request: The Starlette Request Object.
        :return: None if the request is successfully authenticated, raise HTTPException otherwise.
        """


class CredentialsRepository(ABC):
    @abstractmethod
    def get(self, key: str) -> Dict[str, str]:
        """
        Get the credentials for the given key or id.

        Example:
        {
            "client_id": "some-valid-client-id",
            "client_secret": "some-valid-client-secret",
        }

        The dictionary can have any amount of entries. Each RequestAuthenticator
        must recover the required entries to properly authenticate the request.

        If the credentials cannot be recovered by key, the service MUST return
        empty dictionary.

        :param key: str The given key or ir can be a consumer key or a client id.
        :return: Dict[str, str] A key-value dictionary with the credentials.
        """


RequestAuthenticatorDriverProvider = Callable[[dict, LoggerAdapter, CredentialsRepository], RequestAuthenticator]
