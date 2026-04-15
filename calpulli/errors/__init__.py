from typing import Any, Dict
from fastapi import HTTPException

class CalpulliError(Exception):
    """
    Base exception class for the API.

    Attributes:
        status_code (int): The HTTP status code associated with the error.
        detail (Any): Additional details or message about the error (will be propagated to the UI).
        metadata (Dict[str, str]): Optional headers or metadata.
    """
    def __init__(self, status_code: int, detail: Any = None, metadata: Dict[str, str] = None) -> None:
        self.status_code = status_code
        self.detail = detail
        self.metadata = metadata
    
    @staticmethod
    def from_exception(exc: Exception) -> 'CalpulliError':
        """
        Converts any exception into a CalpulliError with status code 500.
        """
        return CalpulliError(status_code=500, detail=str(exc))

    def to_http_exception(self) -> HTTPException:
        """
        Converts a CalpulliError into a FastAPI HTTP exception.
        """
        return HTTPException(
            status_code=self.status_code, 
            detail=self.detail, 
            headers=self.metadata
        )