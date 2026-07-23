from sqlmodel import Session

from app.configs import evm
from app.data import database
from app.dtos.events import DatasetModificationEvent


@evm.listen(DatasetModificationEvent)
def handle_dataset_modification_event(event:DatasetModificationEvent):
    log = event.model()
    with Session(database.engine) as session:
        session.add(log)
        session.commit()

