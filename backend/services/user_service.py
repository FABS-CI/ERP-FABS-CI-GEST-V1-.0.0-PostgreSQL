"""
User Service — User management, authentication-related operations
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import UserRepository
from .base_service import BaseService, ServiceException


class UserService(BaseService):
    """Service for user operations"""

    def __init__(self, session: AsyncSession, user_repo: UserRepository):
        super().__init__(session, user_repo)
        self.user_repo = user_repo

    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        first_name: str = None,
        last_name: str = None,
        role: str = "user"
    ) -> dict:
        """
        Create new user with validations
        
        Args:
            username: Unique username
            email: Unique email
            password_hash: Hashed password (pre-hashed by caller)
            first_name: Optional first name
            last_name: Optional last name
            role: User role (admin, editor, viewer, user)
            
        Returns:
            Created user dict
            
        Raises:
            ServiceException if validation fails
        """
        try:
            # Validate username unique
            await self.validate_unique("username", username, "User")

            # Validate email unique
            await self.validate_unique("email", email, "User")

            # Validate role
            valid_roles = ["admin", "editor", "viewer", "user"]
            self.validate_enum(role, valid_roles, "role")

            # Create user
            user = await self.user_repo.create({
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "actif": True
            })

            await self.session.flush()

            self.log_operation(
                "create_user",
                user.id,
                {"username": username, "email": email, "role": role}
            )

            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }

        except ServiceException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating user: {e}", exc_info=True)
            raise ServiceException(f"Failed to create user: {str(e)}")

    async def deactivate_user(self, user_id: UUID) -> bool:
        """
        Deactivate user
        
        Args:
            user_id: User UUID
            
        Returns:
            True if deactivated
            
        Raises:
            ServiceException if not found
        """
        # Validate user exists
        await self.validate_exists(user_id, "User")

        # Update user
        await self.user_repo.update(user_id, {"actif": False})

        await self.session.flush()

        self.log_operation("deactivate_user", user_id)

        return True

    async def change_user_role(self, user_id: UUID, new_role: str) -> dict:
        """
        Change user role
        
        Args:
            user_id: User UUID
            new_role: New role
            
        Returns:
            Updated user dict
            
        Raises:
            ServiceException if invalid
        """
        # Validate user exists
        await self.validate_exists(user_id, "User")

        # Validate role
        valid_roles = ["admin", "editor", "viewer", "user"]
        self.validate_enum(new_role, valid_roles, "role")

        # Update user
        user = await self.user_repo.update(user_id, {"role": new_role})

        await self.session.flush()

        self.log_operation(
            "change_user_role",
            user_id,
            {"new_role": new_role}
        )

        return {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }

    async def get_active_users(self) -> list:
        """
        Get all active users
        
        Returns:
            List of active users
        """
        return await self.user_repo.read_by(actif=True, is_deleted=False)
