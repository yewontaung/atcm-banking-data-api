from sqlmodel import Session, delete

from app.data import database
from app.data.models import Dataset, DatasetIntent, DatasetIntentNer


def delete_all_dataset_and_related_data():
    print("Pathch start....")
    print("Pathch name : patch_02_add_specific_pk_to_datasetintent_and_datasetintentner")
    with Session(bind=database.engine) as session:
        session.exec(delete(DatasetIntentNer))
        session.exec(delete(DatasetIntent))
        session.exec(delete(Dataset))
        session.commit()
    print("Pathch end...")

delete_all_dataset_and_related_data()