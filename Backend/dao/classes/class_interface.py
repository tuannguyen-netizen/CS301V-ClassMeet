from abc import ABC, abstractmethod

class ClassDAOInterface(ABC):
    @abstractmethod
    async def create_class(self, class_obj):
        pass

    @abstractmethod
    async def find_by_id(self, class_id: str):
        pass

    @abstractmethod
    async def find_by_class_code(self, class_code: str):
        pass

    @abstractmethod
    async def add_user_to_class(self, class_id: str, user_id: str):
        pass

    @abstractmethod
    async def get_class_members(self, class_id: str):
        pass

    @abstractmethod
    async def get_user_memberships(self, user_id: str):
        pass

    @abstractmethod
    async def remove_user_from_class(self, class_id: str, user_id: str):
        pass

    @abstractmethod
    async def delete_class(self, class_id: str):
        pass