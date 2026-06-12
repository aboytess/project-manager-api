from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {"message": "Operation completed successfully"}
        }
    }


# --- Error responses (one model per HTTP status code) ---


class BadRequestResponse(BaseModel):
    error: str
    message: str
    status_code: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "status_code": 400,
            }
        }
    }


class UnauthorizedResponse(BaseModel):
    error: str
    message: str
    status_code: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "Unauthorized",
                "message": "Request does not contain an access token",
                "status_code": 401,
            }
        }
    }


class NotFoundResponse(BaseModel):
    error: str
    message: str
    status_code: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "NotFoundError",
                "message": "Resource not found",
                "status_code": 404,
            }
        }
    }


class ConflictResponse(BaseModel):
    error: str
    message: str
    status_code: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ConflictError",
                "message": "Resource already exists",
                "status_code": 409,
            }
        }
    }


class UnprocessableResponse(BaseModel):
    error: str
    message: str
    status_code: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "message": "field_name: value is not a valid string",
                "status_code": 422,
            }
        }
    }
