from fastapi import Request, HTTPException, status


def get_current_user_id(request: Request) -> str:
    """
    Extract the authenticated user's unique ID (Cognito 'sub' claim)
    from the request. API Gateway's Cognito Authorizer validates the
    JWT and attaches its claims to the request context before Lambda
    ever runs - by the time we get here, the token is already verified.
    """
    try:
        claims = request.scope["aws.event"]["requestContext"]["authorizer"]["claims"]
        return claims["sub"]
    except (KeyError, TypeError):
        # This should be unreachable in production, since API Gateway
        # rejects unauthenticated requests before Lambda runs. It's a
        # safety net for local testing without the authorizer in front.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication",
        )
