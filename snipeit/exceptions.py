"""Custom exception hierarchy for the snipeit client.

These exceptions model HTTP and API-layer errors returned by Snipe-IT.

Examples:
    Catch a specific error type:

        from snipeit.exceptions import SnipeITNotFoundError

        try:
            api.assets.get(999999)
        except SnipeITNotFoundError as err:
            print("Asset not found:", err)
"""

class SnipeITException(Exception):
    """Base exception for all library-specific errors.

    This is the parent for all custom exceptions raised by this library.
    """
    pass


class SnipeITTimeoutError(SnipeITException):
    """Raised when a request to the Snipe-IT API times out.

    Raises:
        SnipeITTimeoutError: Always represents a timeout condition.

    Examples:
        Handle timeouts gracefully:

            try:
                api.assets.list()
            except SnipeITTimeoutError:
                print("The API request timed out.")
    """
    pass


class SnipeITApiError(SnipeITException):
    """Base exception for all errors returned by the Snipe-IT API.

    Args:
        message (str): Human-readable error message.
        response: The HTTP response associated with the error, if any
            (a ``httpx.Response``). Attached as ``self.response`` so
            callers can inspect status code, headers, and body.

    Attributes:
        response: The HTTP response associated with the error.
        status_code (int | None): The HTTP status code, if available.

    Examples:
        Inspect response details when available::

            try:
                api.assets.get(0)
            except SnipeITApiError as e:
                print(e.status_code)
                if e.response is not None:
                    print(e.response.text)
    """
    def __init__(self, message: str, response=None):
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code if response is not None else None


class SnipeITAuthenticationError(SnipeITApiError):
    """Raised for 401 Unauthorized errors.

    Raises:
        SnipeITAuthenticationError: Always represents a 401 Unauthorized.
    """
    pass


class SnipeITNotFoundError(SnipeITApiError):
    """Raised for 404 Not Found errors.

    Raises:
        SnipeITNotFoundError: Always represents a 404 Not Found.
    """
    pass


class SnipeITValidationError(SnipeITApiError):
    """Raised for 422 Unprocessable Entity errors (validation problems).

    Args:
        message (str): Human-readable error message.
        response: The HTTP response, if any.

    Attributes:
        errors (dict | None): Parsed validation errors from the API response,
            if available.

    Examples:
        Access validation details::

            try:
                api.assets.create(status_id=1, model_id=1, asset_tag="")
            except SnipeITValidationError as e:
                print(e.errors)
    """
    def __init__(self, message: str, response=None):
        super().__init__(message, response=response)
        self.errors = None
        try:
            if response is not None:
                body = response.json()
                self.errors = body.get("errors")
        except Exception as exc:
            import logging
            logging.getLogger("snipeit").warning(
                "SnipeITValidationError: failed to parse error body: %s", exc
            )


class SnipeITClientError(SnipeITApiError):
    """Raised for other 4xx client-side errors.

    Raises:
        SnipeITClientError: Represents generic 4xx client-side failures.
    """
    pass


class SnipeITServerError(SnipeITApiError):
    """Raised for 5xx server-side errors.

    Raises:
        SnipeITServerError: Represents generic 5xx server-side failures.
    """
    pass


class SnipeITConnectionError(SnipeITException):
    """Raised when a network-level error prevents the request from completing.

    Covers DNS failures, connection refused, SSL errors, and other transport
    errors that occur before a response is received.

    Raises:
        SnipeITConnectionError: Always represents a transport/connection failure.

    Examples:
        Handle connection failures::

            try:
                api.assets.list()
            except SnipeITConnectionError as e:
                print("Could not reach Snipe-IT:", e)
    """
    pass


class SnipeITStateError(SnipeITException):
    """Raised when an operation cannot proceed due to invalid object state.

    For example, attempting to save staged custom fields when the asset's
    ``custom_fields`` mapping is no longer available.

    Raises:
        SnipeITStateError: Always represents an invalid in-memory state.

    Examples:
        Handle state errors::

            try:
                asset.save()
            except SnipeITStateError:
                asset.refresh()
                asset.save()
    """
    pass

