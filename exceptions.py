class RequestError(Exception):
    """Custom request exception."""

    def __init__(self, code_status):
        """Custom init."""
        self.code_status = code_status
        super().__init__(f'Code API-request: {code_status}')


class ApiError(Exception):
    """Custom API-error exception."""

    def __init__(self):
        """Custom init."""
        super().__init__('No access to API.')


class AnotherError(Exception):
    """Any error exception."""
    pass
