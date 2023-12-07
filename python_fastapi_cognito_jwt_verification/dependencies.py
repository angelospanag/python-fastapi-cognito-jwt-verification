from enum import Enum
from typing import Annotated

import jwt
from fastapi import Header, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from python_fastapi_cognito_jwt_verification.config import get_settings

jwks_client = jwt.PyJWKClient(
    f"https://cognito-idp.{get_settings().aws_default_region}.amazonaws.com/{get_settings().cognito_user_pool_id}/.well-known/jwks.json"
)


class CognitoTokenUse(Enum):
    ID = "id"
    ACCESS = "access"


class CognitoJWTAuthorizer:
    def __init__(
            self,
            required_token_use: CognitoTokenUse,
            aws_default_region: str,
            cognito_user_pool_id: str,
            cognito_app_client_id: str,
            jwks_client: jwt.PyJWKClient,
    ) -> None:
        """Verify an incoming JWT using official AWS guidelines.

        https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html#amazon-cognito-user-pools-using-tokens-manually-inspect

        Args:
            required_token_use (CognitoTokenUse): Required Cognito token type
            aws_default_region (str): AWS region
            cognito_user_pool_id (str): Cognito User Pool ID
            cognito_app_client_id (str): Cognito App Pool ID
            jwks_client (jwt.PyJWKClient): An instance of a JWKS client that has
                                           retrieved the public Cognito JWKS

        Raises:
            fastapi.HTTPException: Raised if a verification check of the incoming
                                     JWT fails
        """
        self.required_token_use = required_token_use
        self.aws_default_region = aws_default_region
        self.cognito_user_pool_id = cognito_user_pool_id
        self.cognito_app_client_id = cognito_app_client_id
        self.jwks_client = jwks_client

    def __call__(self, authorization: Annotated[str | None, Header()] = None):
        """Verify an embedded Cognito JWT token in the 'Authorization' header.

        Args:
            authorization (str | None): 'Authorization' header of a FastAPI endpoint
        """
        if not authorization:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        split_authorization_tokens: list[str] = authorization.split("Bearer ")

        if len(split_authorization_tokens) < 2:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )

        token: str = split_authorization_tokens[1]

        # Attempt to retrieve the signature of the incoming JWT
        try:
            signing_key: jwt.PyJWK = self.jwks_client.get_signing_key_from_jwt(token)
        except jwt.exceptions.InvalidTokenError as e:
            raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                ) from e

        try:
            """
            * Verify the signature of the JWT
            * Verify that the algorithm used is RS256
            * Verification of audience 'aud' is taken care later when we examine if the
              token is 'id' or 'access'
            * Verify that the token hasn't expired. Decode the token and compare the 
              'exp' claim to the current time.
            * The issuer (iss) claim should match your user pool. For example, a user
              pool created in the eu-west-2 region
              will have the following iss value: https://cognito-idp.us-east-1.amazonaws.com/<userpoolID>.
            * Require the existence of claims: 'token_use', 'exp', 'iss', 'sub'
            """
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=f"https://cognito-idp.{self.aws_default_region}.amazonaws.com/{self.cognito_user_pool_id}",
                options={
                    "verify_aud": False,
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                    "require": ["token_use", "exp", "iss", "sub"],
                },
            )
        except jwt.exceptions.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            ) from e
        except jwt.exceptions.InvalidTokenError as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            ) from e

        """
        Check the token_use claim
        * If you are only accepting the access token in your web API operations,
          its value must be access.
        * If you are only using the ID token, its value must be id.
        * If you are using both ID and access tokens,
          the token_use claim must be either id or access.
        """
        if self.required_token_use.value != claims["token_use"]:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )

        """
        The "aud" claim in an ID token and the "client_id" claim in an access token 
        should match the app client ID that was created in the Amazon Cognito user pool.
        """
        if self.required_token_use == CognitoTokenUse.ID:
            if "aud" not in claims:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            if claims["aud"] != self.cognito_app_client_id:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
        elif self.required_token_use == CognitoTokenUse.ACCESS:
            if "client_id" not in claims:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            if claims["client_id"] != self.cognito_app_client_id:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
        else:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )


cognito_jwt_authorizer_access_token = CognitoJWTAuthorizer(
    CognitoTokenUse.ACCESS,
    get_settings().aws_default_region,
    get_settings().cognito_user_pool_id,
    get_settings().cognito_app_client_id,
    jwks_client,
)

cognito_jwt_authorizer_id_token = CognitoJWTAuthorizer(
    CognitoTokenUse.ID,
    get_settings().aws_default_region,
    get_settings().cognito_user_pool_id,
    get_settings().cognito_app_client_id,
    jwks_client,
)
