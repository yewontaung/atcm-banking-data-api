from datetime import datetime
from typing import Generic, Type, TypeVar

import sqlalchemy
from sqlalchemy.orm import selectinload
from sqlmodel import and_, col, desc, distinct, func, select

from data.enums import DatasetType, MemberRole
from data.models import NER, Account, Dataset, DatasetIntent, DatasetIntentNer, Intent, NerIntentLink
from utils.basedto import BaseDto


class MemberListItem(BaseDto):
    member_id:int
    member_profile:str | None
    member_name:str
    member_email:str
    role:MemberRole
    datasets:int

    @classmethod
    def select(cls, DATASET:Type[Dataset]):
        return sqlalchemy.select(
            col(Account.account_id).label("member_id"),
            col(Account.profile_url).label("member_profile"),
            col(Account.name).label("member_name"),
            col(Account.account_email).label("member_email"),
            col(Account.role).label("role"),
            func.count(DATASET.dataset_id).label("datasets")
        ).group_by(Account.account_id, Account.name, Account.account_email, Account.role)

class NerListItem(BaseDto):
    ner_id:int
    label:str
    last_updated:datetime | None
    intents:int

    @classmethod
    def select(cls):
        return (
            select(
                NER,
                func.count(col(NerIntentLink.intent_id))
            ).select_from(NER)
            .outerjoin(NerIntentLink, NER.ner_id == NerIntentLink.ner_id)
            .group_by(NER.ner_id)
        )

class IntentListItem(BaseDto):
    intent_id:int
    label:str
    description:str
    dataset:int
    last_updated:datetime

    class NerInfo(BaseDto):
        ner_id:int
        label:str

    ners:list[NerInfo]

    @classmethod
    def select(cls):
        return (select(
            Intent,
            func.count(col(DatasetIntent.dataset_id))
        )
        .options(
            selectinload(Intent.ners)
        )
        .select_from(Intent)
        .outerjoin(DatasetIntent, Intent.intent_id == DatasetIntent.intent_id)
        .group_by(Intent.intent_id, Intent.label))

class DatasetListItem(BaseDto):
    dataset_id:int
    command:str
    dataset_type:DatasetType
    approved:bool
    member_id:int
    member_name:str
    last_updated:datetime
    deleted:bool

    @classmethod
    def select(cls):
        return (
            select(Dataset, Account.name)
            .select_from(Dataset)
            .join(Account, Account.account_id == Dataset.member_id)
            .order_by(desc(Dataset.dataset_id))
        )

    @classmethod
    def count(cls):
        return (
            select(func.count(Dataset.dataset_id))
            .select_from(Dataset)
            .join(Account, Account.account_id == Dataset.member_id)
        )

ID = TypeVar("ID")

class ModificationResult(BaseDto, Generic[ID]):
    result_data:ID

class AuthProfile(BaseDto):
    account_id:int
    account_name:str
    account_email:str
    account_role:str
    profile_url:str | None

class AuthResult(BaseDto):
    profile:AuthProfile
    access_token:str
    access_type:str = "Bearer"

class Profile(BaseDto):
    account_id:int
    account_name:str
    account_email:str
    account_role:str
    profile_url:str | None

    training_dataset:int
    validation_dataset:int
    testing_dataset:int

class ProfileUploadResult(BaseDto):
    image_url:str

class DatasetIntentNerAlignment(BaseDto):
    ner_id:int
    label:str
    start_index:int
    end_index:int
    intent_id:int

    @staticmethod
    def from_(ner:DatasetIntentNer) -> DatasetIntentNerAlignment:
        return DatasetIntentNerAlignment(
            ner_id=ner.ner_id,
            label=ner.ner.label,
            start_index=ner.start_index,
            end_index=ner.end_index,
            intent_id=ner.intent_id,
        )

class DatasetDetailIntent(BaseDto):
    intent_id:int
    label:str
    start_index:int
    end_index:int

    @staticmethod
    def from_(intent:DatasetIntent) -> DatasetDetailIntent:
        return DatasetDetailIntent(
            intent_id=intent.intent_id,
            label=intent.intent.label,
            start_index=intent.start_index,
            end_index=intent.end_index,
        )

class DatasetInfo(BaseDto):
    dataset_id:int
    member_id:int
    member_name:str
    member_role:MemberRole
    dataset_type:DatasetType
    approved:bool
    deleted:bool
    last_updated:datetime

class DatasetDetail(BaseDto):
    dataset_id:int
    command:str
    intents:list[DatasetDetailIntent]
    alignments:list[DatasetIntentNerAlignment]

class DatasetDetailResult(BaseDto):
    info:DatasetInfo
    dataset:DatasetDetail


class DatasetMeta(BaseDto):
    total_datasets:int
    total_intents:int
    total_ners:int

class DatasetAnalysis(BaseDto):
    training_datasets:int
    validation_datasets:int
    testing_datasets:int

class CollectRate(BaseDto):
    member_id:int
    member_name:str
    member_profile:str | None
    collected_data:int

    @staticmethod
    def select():
        return select(
            Account.account_id,
            Account.name,
            Account.profile_url,
            func.count(Dataset.dataset_id)
        ).group_by(
            Account.account_id,
            Account.name,
            Account.profile_url
        )

class DashboardAnalysis(BaseDto):
    dataset_meta:DatasetMeta
    dataset_analysis:DatasetAnalysis
    today_collect_rate:list[CollectRate]
    yesterday_collect_rate:list[CollectRate]
