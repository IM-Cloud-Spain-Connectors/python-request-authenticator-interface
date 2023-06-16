#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from dataclasses import dataclass
from logging import LoggerAdapter
from urllib import parse

from starlette.exceptions import HTTPException
from starlette.requests import Request
from oauthlib.oauth1.rfc5849 import signature as oauth
from rndi.authentication.starlette.contract import CredentialsRepository, RequestAuthenticator


def provide_oauth10a_request_authenticator_adapter(
        _: dict,
        logger: LoggerAdapter,
        credentials_repository: CredentialsRepository,
) -> RequestAuthenticator:
    return OAuth10aRequestAuthenticatorAdapter(
        logger=logger,
        credentials_repository=credentials_repository,
    )


@dataclass
class Credential:
    client_key: str
    client_secret: str
    resource_owner_secret: str


@dataclass
class OAuth10aParameters:
    oauth_consumer_key: str
    oauth_signature_method: str
    oauth_timestamp: str
    oauth_nonce: str
    oauth_version: str
    oauth_signature: str


X_FORWARDED_PROTO = 'X-Forwarded-Proto'
X_FORWARDED_HOST = 'X-Forwarded-Host'

MSG_UNAUTHENTICATED = 'Unauthenticated, {detail}.'


class OAuth10aRequestAuthenticatorAdapter(RequestAuthenticator):
    DRIVER = 'oauth10a'

    def __init__(self, logger: LoggerAdapter, credentials_repository: CredentialsRepository):
        self.__logger = logger
        self.__credential_repository = credentials_repository

    def authenticate(self, request: Request):
        self.__logger.debug("OAuth10aRequestAuthenticatorAdapter: authenticating request with {driver} driver.".format(
            driver=self.DRIVER,
        ))

        header = request.headers.get('authorization')
        if header is None:
            raise HTTPException(
                status_code=401,
                detail=MSG_UNAUTHENTICATED.format(detail='missing oauth 1.0a signature'),
            )

        try:
            authorization = {}
            for parameter in header.split(' ', 2)[1].replace('"', '').split(','):
                key_value = parameter.split('=')
                authorization[key_value[0].strip()] = key_value[1].strip()

            authorization = OAuth10aParameters(**authorization)
            self.__logger.debug(f"OAuth10aRequestAuthenticatorAdapter: {authorization}")
        except (IndexError, TypeError) as e:
            self.__logger.debug(f'OAuth10aRequestAuthenticatorAdapter: unable to parse OAuth 1.0a header {header}'
                                f' due to {e}.')
            raise HTTPException(
                status_code=401,
                detail=MSG_UNAUTHENTICATED.format(detail='malformed oauth 1.0a signature'),
            )

        try:
            credentials = Credential(**self.__credential_repository.get(authorization.oauth_consumer_key))
        except TypeError as e:
            self.__logger.debug(f'OAuth10aRequestAuthenticatorAdapter: unable to retrieve OAuth 1.0a '
                                f'credentials for client_key {authorization.oauth_consumer_key} due to {e}.')
            raise HTTPException(
                status_code=401,
                detail=MSG_UNAUTHENTICATED.format(detail='invalid client/consumer key'),
            )

        method = str(request.method)
        url = str(request.url)
        query_string = str(request.query_params)

        self.__logger.debug(f"OAuth10aRequestAuthenticatorAdapter: method: {method}")
        self.__logger.debug(f"OAuth10aRequestAuthenticatorAdapter: url: {url}")
        self.__logger.debug(f"OAuth10aRequestAuthenticatorAdapter: query string: {query_string}")

        # extract the headers from the request
        headers = request.headers.mutablecopy()

        # connect uses a load balancer to handle the requests. this changes the
        # url of the request. the real url can be computed from the X-Forwarded-Proto
        # and X-Forwarded-Host headers.
        if X_FORWARDED_PROTO in request.headers and X_FORWARDED_HOST in request.headers:
            url = '{proto}://{host}{path}'.format(
                proto=headers[X_FORWARDED_PROTO],
                host=headers[X_FORWARDED_HOST],
                path=request.url.path,
            )
            self.__logger.debug(f"OAuth10aRequestAuthenticatorAdapter: computed url from forwarded headers: {url}")

            # replace the host with the real one computed from headers.
            headers.update({'host': url})

        parameters = oauth.normalize_parameters(oauth.collect_parameters(
            uri_query=query_string,
            body=request.body,
            headers=headers,
        ))

        self.__logger.debug(f"OAuth10aRequestAuthenticatorAdapter: parameters: {parameters}")

        signature_generated = parse.quote(
            string=oauth.sign_hmac_sha1_with_client(
                sig_base_str=oauth.signature_base_string(method, url, parameters),
                client=credentials,
            ),
            safe="",
        )

        self.__logger.debug(f"OAuth10aRequestAuthenticatorAdapter: generated signature: {signature_generated}")
        self.__logger.debug(f"OAuth10aRequestAuthenticatorAdapter: received signature: {authorization.oauth_signature}")

        if authorization.oauth_signature != signature_generated:
            raise HTTPException(
                status_code=401,
                detail=MSG_UNAUTHENTICATED.format(detail='the provided signature is not valid'),
            )
