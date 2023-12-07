from fastapi import Depends, FastAPI

from python_fastapi_cognito_jwt_verification.dependencies import (
    cognito_jwt_authorizer_access_token,
    cognito_jwt_authorizer_id_token,
)

app = FastAPI()


@app.get("/protected-with-access-token", dependencies=[Depends(cognito_jwt_authorizer_access_token)])
def protected_with_access_token():
    return {"Hello": "World"}


@app.get("/protected-with-id-token", dependencies=[Depends(cognito_jwt_authorizer_id_token)])
def protected_with_id_token():
    return {"Hello": "World"}
