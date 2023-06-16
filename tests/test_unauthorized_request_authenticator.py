#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
import pytest
from starlette.exceptions import HTTPException
from starlette.requests import Request
from rndi.authentication.starlette.adapters.unauthorized import UnauthorizedRequestAuthenticatorAdapter


def test_unauthorized_request_authenticator_should_authenticate_given_request(make_logger):
    request = Request({
        'type': 'http',
    })

    authenticator = UnauthorizedRequestAuthenticatorAdapter(make_logger())

    with pytest.raises(HTTPException):
        authenticator.authenticate(request)
