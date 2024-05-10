from fastapi import HTTPException, status


COLOR_REQUIRED_FOR_WILDCARDS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="To play a Wildcard or Take Four Wildcard, you must specify a color.",
)
