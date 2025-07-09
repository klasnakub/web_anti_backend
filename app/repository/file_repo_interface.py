from abc import ABC, abstractmethod
from typing import Optional

class IGCSFileRepository(ABC):
    @abstractmethod
    def upload_file(self, file_content: bytes, unique_file_name: str, content_type: str, prefix: str) -> dict:
        pass

    @abstractmethod
    def delete_file(self, file_name: str, prefix: str) -> bool:
        pass
    
    @abstractmethod
    def get_file_url(self, file_name: str, prefix: str) -> Optional[str]:
        pass
