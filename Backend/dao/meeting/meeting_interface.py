from abc import ABC, abstractmethod

class MeetingDAOInterface(ABC):
    @abstractmethod
    async def create_meeting(self, meeting):
        pass

    @abstractmethod
    async def find_by_id(self, meeting_id: str):
        pass

    @abstractmethod
    async def add_user_to_meeting(self, meeting_id: str, user_id: str):
        pass

    @abstractmethod
    async def remove_user_from_meeting(self, meeting_id: str, user_id: str):
        pass

    @abstractmethod
    async def get_meeting_participants(self, meeting_id: str):
        pass