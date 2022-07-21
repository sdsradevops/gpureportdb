from typing import Optional

from pydantic import BaseModel


class Namespace(BaseModel):
    namespace_name: str
    sql_conn_str: str
    schema_name: str


class ReportModel(BaseModel):
    namespace_name: Optional[str] = None
    user_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    page: Optional[int] = 1
    size: Optional[int] = 2
