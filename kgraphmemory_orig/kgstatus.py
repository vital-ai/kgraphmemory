from enum import Enum


class KGStatusErrorType(Enum):
    OK = 'kg_status_ok'
    DATA_ERROR = 'kg_status_data_error'
    DATABASE_ERROR = 'kg_status_database_error'


class KGStatus:
    status: bool = True
    error_type: KGStatusErrorType = KGStatusErrorType.OK
    message: str = 'Ok'



