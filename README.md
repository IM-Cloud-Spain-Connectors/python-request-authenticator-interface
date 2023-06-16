# Python Request Authentication Interface

[![Test](https://github.com/IM-Cloud-Spain-Connectors/python-request-authenticator-interface/actions/workflows/test.yml/badge.svg)](https://github.com/IM-Cloud-Spain-Connectors/python-request-authenticator-interface/actions/workflows/test.yml)

Simple and clean request Authenticator interface for Starlette python projects.

## Installation

The easiest way to install the Request Authentication Interface library is to get the latest version from PyPI:

```bash
# using poetry
poetry add rndi-request-authenticator-interface
# using pip
pip install rndi-request-authenticator-interface
```

## The Contract

This package provides the following contracts or interfaces:

```python
class RequestAuthenticator(ABC):
    @abstractmethod
    def authenticate(self, request: Request):
        """
        Authenticate the given request.

        :param request: The Starlette Request Object.
        :return: None if the request is successfully authenticated, raise HTTPException otherwise.
        """
```

This interface or contract is meant to be used to create Request Authenticators for Frameworks based
in https://www.starlette.io/ like https://fastapi.tiangolo.com/.

```python
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

```

The `CredentialsRepository` contract provides simple way to retrieve the credentials that will be used by the different
adapters to authenticate the incoming requests. The implementation of the concrete `CredentialsRepository` may depend on
the project as the credentials used to authenticate can be stored in different places as environment variables or even
in a database.

## The Adapters

This package provides the following adapters:

| Name           | Description                                                    |
|----------------|----------------------------------------------------------------|
| `oauth10a`     | Authenticator for OAuth 1.0a.                                  |
| `unauthorized` | Deny all the access by returning always HTTP 401 Unauthorized. |

## Service Provider

To provide a request authenticator adapter, you should use the `provide_request_authenticator` function, which accepts
the following arguments:

| name                     | description                         | type                                                                         |
|--------------------------|-------------------------------------|:-----------------------------------------------------------------------------|
| `config`                 | The adapter configuration.          | Dict[str, str]                                                               |
| `logger`                 | A logger instance.                  | LoggerAdapter                                                                |
| `credentials_repository` | The credentials repository adapter. | CredentialsRepository                                                        |
| `drivers`                | Additional drivers.                 | Callable[[dict, LoggerAdapter, CredentialsRepository], RequestAuthenticator] |

The `config` argument is a dictionary that must have the following entries:

| name                | description                                      |
|---------------------|--------------------------------------------------|
| REQUEST_AUTH_DRIVER | The driver to use, by default is `unauthorized`. |

# Usage

First, instantiate the adapter:

```python
request_authenticator = provide_request_authenticator(config, logger, credentials_repository, drivers)
```

Next, execute the authenticate function with the incoming request as parameter:

```python
request_authenticator.authenticate(request)
```

The adapter will do nothing on authenticated request, raising an `401 HTTPException` otherwise.
