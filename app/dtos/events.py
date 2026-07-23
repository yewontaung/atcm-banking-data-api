from datetime import datetime, timezone

from sqlmodel import Session

from app.data.enums import ModificationType
from app.data.models import DatasetModificationLog
from app.utils.basedto import BaseDto


class DatasetModificationEvent(BaseDto):
    dataset_id:int
    account_id:int
    modification_type:ModificationType

    def model(self) -> DatasetModificationLog:
        return DatasetModificationLog(
            dataset_id=self.dataset_id,
            account_id=self.account_id,
            modification_type=self.modification_type,
            created_at=datetime.now(tz=timezone.utc)
        )