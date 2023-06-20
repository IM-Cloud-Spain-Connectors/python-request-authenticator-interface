#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
import pytest
from starlette.exceptions import HTTPException
from rndi.authentication.starlette.adapters.oauth10a import OAuth10aRequestAuthenticatorAdapter


def test_oauth10a_request_authenticator_should_authenticate_given_request(
        make_credential_repository,
        make_logger,
        make_request,
):
    request = make_request('GET', 'https://cosmopolitan.aks.int.zone/aps/2/collections/service-plans', {
        'authorization': 'OAuth '
                         'oauth_consumer_key="wotAQOwTUXZrkZqfOMrpEAtTC362SJi8", '
                         'oauth_signature_method="HMAC-SHA1", '
                         'oauth_timestamp="1686919540", '
                         'oauth_nonce="RZQd4m3S0Iu", '
                         'oauth_version="1.0",'
                         'oauth_signature="XcvHhpsvfYz2%2F1PiI19axOJNe0E%3D"',
    })

    authenticator = OAuth10aRequestAuthenticatorAdapter(
        make_logger(),
        make_credential_repository({
            'get': lambda _: {
                'client_key': 'wotAQOwTUXZrkZqfOMrpEAtTC362SJi8',
                'client_secret': '4oV1gtQxZxjxkl0jYqfd0FukNADAu0NmTML9Xm6KCA0n1CcEOSEaGAUC9nca8Do2'
                                 'W6GocxO1RYJvbpDsFbZ5pvxZIISlycvbIE2F6OLRNMQld8uJE9eVNNxKu72xxrTI',
                'resource_owner_secret': '',
            },
        }),
    )

    assert authenticator.authenticate(request) is None


def test_oauth10a_request_authenticator_should_authenticate_given_request_with_x_forwarded_headers(
        make_credential_repository,
        make_logger,
        make_request,
):
    request = make_request('GET', 'https://load.balance.conn.rocks/aps/2/collections/service-plans', {
        'authorization': 'OAuth '
                         'oauth_consumer_key="wotAQOwTUXZrkZqfOMrpEAtTC362SJi8",'
                         'oauth_signature_method="HMAC-SHA1",'
                         'oauth_timestamp="1686919540",'
                         'oauth_nonce="RZQd4m3S0Iu",'
                         'oauth_version="1.0",'
                         'oauth_signature="XcvHhpsvfYz2%2F1PiI19axOJNe0E%3D"',
        'x-forwarded-proto': 'https',
        'x-forwarded-host': 'cosmopolitan.aks.int.zone',
    })

    authenticator = OAuth10aRequestAuthenticatorAdapter(
        make_logger(),
        make_credential_repository({
            'get': lambda _: {
                'client_key': 'wotAQOwTUXZrkZqfOMrpEAtTC362SJi8',
                'client_secret': '4oV1gtQxZxjxkl0jYqfd0FukNADAu0NmTML9Xm6KCA0n1CcEOSEaGAUC9nca8Do2'
                                 'W6GocxO1RYJvbpDsFbZ5pvxZIISlycvbIE2F6OLRNMQld8uJE9eVNNxKu72xxrTI',
                'resource_owner_secret': '',
            },
        }),
    )

    assert authenticator.authenticate(request) is None


def test_oauth10a_request_authenticator_should_throw_exception_for_unauthorized_request(
        make_credential_repository,
        make_logger,
        make_request,
):
    request = make_request('GET', 'https://cosmopolitan.aks.int.zone/aps/2/collections/service-plans', {
        'authorization': 'OAuth '
                         'oauth_consumer_key="wotAQOwTUXZrkZqfOMrpEAtTC362SJi8",'
                         'oauth_signature_method="HMAC-SHA1",'
                         'oauth_timestamp="1686919540",'
                         'oauth_nonce="RZQd4m3S0Iu",'
                         'oauth_version="1.0",'
                         'oauth_signature="XcvHhpsvfYz2%2F1PiI19axOJNe0E%33"',
    })

    authenticator = OAuth10aRequestAuthenticatorAdapter(
        make_logger(),
        make_credential_repository({
            'get': lambda _: {
                'client_key': 'wotAQOwTUXZrkZqfOMrpEAtTC362SJi8',
                'client_secret': '4oV1gtQxZxjxkl0jYqfd0FukNADAu0NmTML9Xm6KCA0n1CcEOSEaGAUC9nca8Do2'
                                 'W6GocxO1RYJvbpDsFbZ5pvxZIISlycvbIE2F6OLRNMQld8uJE9eVNNxKu72xxrTI',
                'resource_owner_secret': '',
            },
        }),
    )

    with pytest.raises(HTTPException):
        authenticator.authenticate(request)


def test_oauth10a_request_authenticator_should_throw_exception_on_missing_authorization_header(
        make_credential_repository,
        make_logger,
        make_request,
):
    request = make_request('GET', 'https://cosmopolitan.aks.int.zone/aps/2/collections/service-plans')

    authenticator = OAuth10aRequestAuthenticatorAdapter(
        make_logger(),
        make_credential_repository(),
    )

    with pytest.raises(HTTPException):
        authenticator.authenticate(request)


def test_oauth10a_request_authenticator_should_throw_exception_on_invalid_consumer_key(
        make_credential_repository,
        make_logger,
        make_request,
):
    request = make_request('GET', 'https://cosmopolitan.aks.int.zone/aps/2/collections/service-plans', {
        'authorization': 'OAuth '
                         'oauth_consumer_key="wotAQOwTUXZrkZqfOMrpEAtTC362SJi8",'
                         'oauth_signature_method="HMAC-SHA1",'
                         'oauth_timestamp="1686919540",'
                         'oauth_nonce="RZQd4m3S0Iu",'
                         'oauth_version="1.0",'
                         'oauth_signature="XcvHhpsvfYz2%2F1PiI19axOJNe0E%3D"',
    })

    authenticator = OAuth10aRequestAuthenticatorAdapter(
        make_logger(),
        make_credential_repository(),
    )

    with pytest.raises(HTTPException):
        authenticator.authenticate(request)


def test_oauth10a_request_authenticator_should_throw_exception_on_malformed_signature(
        make_credential_repository,
        make_logger,
        make_request,
):
    request = make_request('GET', 'https://cosmopolitan.aks.int.zone/aps/2/collections/service-plans', {
        'authorization': 'OAuth '
                         'oauth_consumer="wotAQOwTUXZrkZqfOMrpEAtTC362SJi8",'
                         'oauth_signature_method="HMAC-SHA1",'
                         'oauth_timestamp="1686919540",'
                         'oauth_nonce="RZQd4m3S0Iu",'
                         'oauth_version="1.0",'
                         'oauth_signature="XcvHhpsvfYz2%2F1PiI19axOJNe0E%3D"',
    })

    authenticator = OAuth10aRequestAuthenticatorAdapter(
        make_logger(),
        make_credential_repository(),
    )

    with pytest.raises(HTTPException):
        authenticator.authenticate(request)
