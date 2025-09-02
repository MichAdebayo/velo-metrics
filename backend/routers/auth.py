from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from ..utils.security import authenticate_user, create_access_token
import datetime

router = APIRouter(tags=["auth"])

@router.post("/token", operation_id="token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = datetime.timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user["user_name"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}