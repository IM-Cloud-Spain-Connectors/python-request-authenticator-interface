#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from starlette.requests import Request
from rndi.authentication.starlette.adapters.oauth10a import OAuth10aRequestAuthenticatorAdapter
from rndi.authentication.starlette.adapters.unauthorized import UnauthorizedRequestAuthenticatorAdapter
from rndi.authentication.starlette.contract import RequestAuthenticator
from rndi.authentication.starlette.provider import provide_request_authenticator, REQUEST_AUTH_DRIVER


def test_provider_should_return_unauthorized_request_authenticator_by_driver(
        make_credential_repository,
        make_logger,
):
    config = {}
    authenticator = provide_request_authenticator(config, make_logger(), make_credential_repository())

    assert isinstance(authenticator, UnauthorizedRequestAuthenticatorAdapter)


def test_provider_should_return_correct_request_authenticator_by_driver(
        make_credential_repository,
        make_logger,
):
    config = {REQUEST_AUTH_DRIVER: 'oauth10a'}
    authenticator = provide_request_authenticator(config, make_logger(), make_credential_repository())

    assert isinstance(authenticator, OAuth10aRequestAuthenticatorAdapter)


def test_provider_should_return_unauthorized_request_authenticator_on_error(
        make_credential_repository,
        make_logger,
):
    config = {REQUEST_AUTH_DRIVER: 'this-driver-does-not-exists'}
    authenticator = provide_request_authenticator(config, make_logger(), make_credential_repository())

    assert isinstance(authenticator, UnauthorizedRequestAuthenticatorAdapter)


def test_provider_should_return_request_authenticator_from_extra_drivers(
        make_credential_repository,
        make_logger,
):
    class CustomRequestAuthenticator(RequestAuthenticator):
        DRIVER = 'custom'

        def authenticate(self, _: Request):
            """ just for test """

    def provide_custom_authenticator(_, __, ___) -> RequestAuthenticator:
        return CustomRequestAuthenticator()

    config = {REQUEST_AUTH_DRIVER: 'custom'}
    authenticator = provide_request_authenticator(config, make_logger(), make_credential_repository(), {
        CustomRequestAuthenticator.DRIVER: provide_custom_authenticator,
    })

    assert isinstance(authenticator, CustomRequestAuthenticator)
