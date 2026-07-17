from datetime import datetime, timezone

from sqlmodel import Session, update

from data import database
from data.models import Dataset


def insert_created_at_to_dataset():
    print("Start...")
    with Session(database.engine) as session:
        print("Patching...")
        UPDATE = update(Dataset).values(created_at = datetime.now(tz=timezone.utc))
        session.exec(UPDATE)
        session.commit()
    print("Done...")

insert_created_at_to_dataset()