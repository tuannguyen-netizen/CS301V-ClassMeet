from abc import ABC, abstractmethod

class UserDAOInterface(ABC):
    @abstractmethod
    async def create_user(self, user):
        pass

    @abstractmethod
    async def find_by_id(self, user_id: str):
        pass

    @abstractmethod
    async def find_by_email(self, email: str):
        pass

    @abstractmethod
    async def find_by_username(self, username: str):
        pass