#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from logging import LoggerAdapter
from typing import Dict, Optional

from rndi.authentication.starlette.adapters.unauthorized import (
    provide_unauthorized_request_authenticator,
    UnauthorizedRequestAuthenticatorAdapter,
)
from rndi.authentication.starlette.adapters.oauth10a import (
    OAuth10aRequestAuthenticatorAdapter,
    provide_oauth10a_request_authenticator_adapter,
)
from rndi.authentication.starlette.contract import (
    CredentialsRepository,
    RequestAuthenticator,
    RequestAuthenticatorDriverProvider,
)

REQUEST_AUTH_DRIVER = 'REQUEST_AUTH_DRIVER'


def provide_request_authenticator(
        config: dict,
        logger: LoggerAdapter,
        credentials_repository: CredentialsRepository,
        drivers: Optional[Dict[str, RequestAuthenticatorDriverProvider]] = None,
) -> RequestAuthenticator:
    supported: Dict[str, RequestAuthenticatorDriverProvider] = {
        OAuth10aRequestAuthenticatorAdapter.DRIVER: provide_oauth10a_request_authenticator_adapter,
        UnauthorizedRequestAuthenticatorAdapter.DRIVER: provide_unauthorized_request_authenticator,
    }

    if isinstance(drivers, dict):
        supported.update(drivers)

    # default value for the REQUEST_AUTH_DRIVER is 'oauth10a' as is the
    # authentication method used in CloudBlue Commerce for APS integrations.
    driver = config.get(REQUEST_AUTH_DRIVER, UnauthorizedRequestAuthenticatorAdapter.DRIVER)

    def _unsupported_driver(_, __, ___) -> RequestAuthenticator:
        raise ValueError(f"Unsupported request authenticator driver {driver}.")

    # get the provider for the requested driver, if the driver is not supported
    # use the '_unsupported_driver' provider, this will raise an Exception.
    provider = supported.get(driver, _unsupported_driver)

    try:
        adapter = provider(config, logger, credentials_repository)
        logger.debug(f"Request authentication service configured with {driver} driver.")
    except Exception as e:
        adapter = provide_unauthorized_request_authenticator(config, logger, credentials_repository)
        logger.error(
            f"Request authentication failure, unable to use driver {driver} due to: {e}, using "
            f"'unauthorized' driver, all request will been responded with 401 Unauthorized",
        )

    return adapter
