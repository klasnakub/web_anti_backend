from abc import ABC, abstractmethod
from typing import Optional

class IGCSFileRepository(ABC):
    @abstractmethod
    def upload_file(self, file_content: bytes, file_name: str, content_type: str) -> dict:
        pass

    @abstractmethod
    def delete_file(self, file_name: str) -> bool:
        pass
    
    @abstractmethod
    def get_file_url(self, file_name: str) -> Optional[str]:
        pass
