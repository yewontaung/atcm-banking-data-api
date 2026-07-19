from datetime import date, datetime, time, timedelta

from sqlmodel import Session, and_, func, select

from data.enums import DatasetType
from data.models import NER, Account, Dataset, Intent
from dtos.outputs import CollectRate, DashboardAnalysis, DatasetAnalysis, DatasetMeta


def analysis(session:Session) -> DashboardAnalysis:

    INTENTS = select(func.count(Intent.intent_id))
    NAMED_ENTITIES = select(func.count(NER.ner_id))

    DATASETS = select(
        Dataset.dataset_type,
        func.count(Dataset.dataset_id)
    ).where(Dataset.deleted == False).group_by(Dataset.dataset_type)

    yesterday = date.today() - timedelta(days=1)
    yesterday_start = datetime.combine(yesterday, time.min)
    yesterday_end = datetime.combine(yesterday, time.max)

    today = date.today()
    today_start = datetime.combine(today, time.min)
    today_end = datetime.combine(today, time.max)

    COLLECT_RATE = (
        CollectRate.select().select_from(Account)
    )

    YESTERDAY_RATE = COLLECT_RATE.join(Dataset, and_(
        Dataset.member_id == Account.account_id,
        Dataset.created_at >= yesterday_start, 
        Dataset.created_at <= yesterday_end,
        Dataset.deleted == False,
    ), isouter=True)

    TODAY_RATE = COLLECT_RATE.join(Dataset, and_(
        Dataset.member_id == Account.account_id,
        Dataset.created_at >= today_start, 
        Dataset.created_at <= today_end,
        Dataset.deleted == False,
    ), isouter=True)
    
    intents = session.exec(INTENTS).one_or_none() or 0
    ners = session.exec(NAMED_ENTITIES).one_or_none() or 0

    datasets = session.exec(DATASETS).all()
    training_datasets = 0
    validate_datasets = 0
    testing_datasets = 0

    for dataset_type, dataset_count in datasets:
        match dataset_type:
            case DatasetType.Training: training_datasets += dataset_count
            case DatasetType.Validation:validate_datasets += dataset_count
            case DatasetType.Testing:testing_datasets += dataset_count
    
    total_datasets = training_datasets + validate_datasets + testing_datasets


    yesterday_result = session.exec(YESTERDAY_RATE).all()
    today_result = session.exec(TODAY_RATE).all()

    yesterday_rate = [CollectRate(
       member_id=member_id,
       member_name=member_name,
       member_profile=member_profile,
       collected_data=collected_data or 0,
    ) for
      member_id, 
      member_name, 
      member_profile, 
      collected_data 
    in yesterday_result]

    today_rate = [CollectRate(
       member_id=member_id,
       member_name=member_name,
       member_profile=member_profile,
       collected_data=collected_data or 0,
    ) for
      member_id, 
      member_name, 
      member_profile, 
      collected_data 
    in today_result]


    return DashboardAnalysis(
        dataset_meta=DatasetMeta(
            total_datasets=total_datasets,
            total_intents=intents,
            total_ners=ners,
        ),
        dataset_analysis=DatasetAnalysis(
            training_datasets=training_datasets,
            validation_datasets=validate_datasets,
            testing_datasets=testing_datasets,
        ),
        today_collect_rate=today_rate,
        yesterday_collect_rate=yesterday_rate,
    )