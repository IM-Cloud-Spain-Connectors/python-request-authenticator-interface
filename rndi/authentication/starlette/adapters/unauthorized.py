#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from logging import LoggerAdapter

from starlette.exceptions import HTTPException
from starlette.requests import Request
from rndi.authentication.starlette.contract import CredentialsRepository, RequestAuthenticator


def provide_unauthorized_request_authenticator(
        _: dict,
        logger: LoggerAdapter,
        __: CredentialsRepository,
) -> RequestAuthenticator:
    return UnauthorizedRequestAuthenticatorAdapter(
        logger=logger,
    )


class UnauthorizedRequestAuthenticatorAdapter(RequestAuthenticator):
    DRIVER = 'unauthorized'

    def __init__(self, logger: LoggerAdapter):
        self.__logger = logger

    def authenticate(self, request: Request):
        self.__logger.warning("UnauthorizedRequestAuthenticatorAdapter: Unauthorized request with {driver}.".format(
            driver=self.DRIVER,
        ))
        raise HTTPException(status_code=401, detail="Unauthenticated.")
