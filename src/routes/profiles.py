from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_jwt_auth_manager, get_s3_storage_client
from database import get_db, UserModel, UserProfileModel
from exceptions import BaseSecurityError
from schemas.profiles import UserProfileSchema
from security.http import get_token
from security.interfaces import JWTAuthManagerInterface
from storages.interfaces import S3StorageInterface

from validation import (
    validate_name,
    validate_image,
    validate_gender,
    validate_birth_date,
)

router = APIRouter()


@router.post(
    "/users/{user_id}/profile/",
    response_model=UserProfileSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_profile(
    user_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    gender: str = Form(...),
    date_of_birth: date = Form(...),
    info: str = Form(""),
    avatar: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_token),
    jwt_manager: JWTAuthManagerInterface = Depends(get_jwt_auth_manager),
    storage: S3StorageInterface = Depends(get_s3_storage_client),
) -> UserProfileSchema:
    """
    Endpoint for creating a user profile.

    Validates the authorization token, ensures the requester has permission to create
    the profile, checks for an existing profile, validates all submitted fields, uploads
    the avatar to S3 storage (if provided), and stores the profile in the database.

    Args:
        user_id (int): The ID of the user for whom the profile is being created.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        gender (str): The user's gender.
        date_of_birth (date): The user's date of birth.
        info (str): Additional profile information.
        avatar (UploadFile | None): The avatar image file.
        db (AsyncSession): The asynchronous database session.
        token (str): The extracted Bearer token.
        jwt_manager (JWTAuthManagerInterface): The JWT authentication manager.
        storage (S3StorageInterface): The S3-compatible storage client.

    Returns:
        UserProfileSchema: The newly created user profile.

    Raises:
        HTTPException:
            - 401 Unauthorized if the token is missing, invalid, or expired, or the user is not found/active.
            - 403 Forbidden if the requester does not have permission to create this profile.
            - 400 Bad Request if the user already has a profile.
            - 422 Unprocessable Entity if validation fails.
            - 500 Internal Server Error if the avatar upload fails.
    """
    try:
        decoded_token = jwt_manager.decode_access_token(token)
        token_user_id = decoded_token.get("user_id")
    except BaseSecurityError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )

    if not token_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    current_user_result = await db.execute(
        select(UserModel).where(UserModel.id == token_user_id)
    )
    current_user = current_user_result.scalars().first()

    if not current_user or not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or not active.",
        )

    target_user_result = await db.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    target_user = target_user_result.scalars().first()

    if not target_user or not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or not active.",
        )

    is_admin = current_user.group_id == 3

    if current_user.id != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this profile.",
        )

    if info is not None and not info.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Info field cannot be empty or contain only spaces.",
        )

    existing_profile_result = await db.execute(
        select(UserProfileModel).where(UserProfileModel.user_id == user_id)
    )
    existing_profile = existing_profile_result.scalars().first()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a profile.",
        )

    try:
        validate_name(first_name)
        validate_name(last_name)
        validate_gender(gender)
        validate_birth_date(date_of_birth)

        avatar_url = None
        avatar_key = None

        if avatar is not None:
            validate_image(avatar)

            avatar_key = f"avatars/{user_id}_avatar.jpg"
            avatar_data = await avatar.read()

            await storage.upload_file(
                avatar_key,
                avatar_data,
            )

            avatar_url = await storage.get_file_url(avatar_key)

        profile = UserProfileModel(
            first_name=first_name.lower(),
            last_name=last_name.lower(),
            gender=gender,
            date_of_birth=date_of_birth,
            info=info,
            avatar=avatar_key,
            user_id=user_id,
        )

        db.add(profile)
        await db.commit()
        await db.refresh(profile)

        return UserProfileSchema(
            id=profile.id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            gender=profile.gender,
            date_of_birth=profile.date_of_birth,
            info=profile.info,
            avatar=avatar_url,
        )

    except ValueError as error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )

    except HTTPException:
        await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload avatar. Please try again later.",
        )
