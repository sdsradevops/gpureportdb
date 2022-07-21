import os
from datetime import datetime
from base.admin import AdminDB


class Report(object):

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.admin_db = AdminDB(base_dir + r'\conf\database.ini', 'sbrain_schema', 'namespace', 1)

    @staticmethod
    def filter_params(params):
        params = {k: v for k, v in params.items() if v}
        return params

    @staticmethod
    def convert_json_dates(records):
        for idx, record in enumerate(records):
            up_record = {k: v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v
                         for k, v in record.items()}
            records[idx] = up_record
        return records

    def get_terminal_report(self, report_model: dict):
        table_name = 'terminal_sessions'
        report_model = self.filter_params(report_model)
        result = self.admin_db.get_filtered_table_records(table_name, **report_model)
        result = self.convert_json_dates(result)
        return result

    def get_env_report(self, report_model: dict):
        table_name = 'environment_sessions'
        report_model = self.filter_params(report_model)
        result = self.admin_db.get_filtered_table_records(table_name, **report_model)
        result = self.convert_json_dates(result)
        return result
