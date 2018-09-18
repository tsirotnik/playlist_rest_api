"""
custom exceptions
"""



class DBException (Exception):
    """
    Exception for database errors
    """
    pass


class APIAuthException(Exception):
    """
    Exception for authorization errors
    """
    pass


class APIException(Exception):
    """
    Exception for API errors
    """
    pass
