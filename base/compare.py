from base.admin import AdminDB
from base.namespace import Namespace
import os

# env_record_dict = {'session_id', 'environment_id', 'env_description', 'notebook_id',
#                        'session_namespace', 'session_nodeport_url', 'session_description',
#                        'created_by_user', 'created_date', 'updated_date', 'updated_timestamp', 'status',
#                        'htb_start_time', 'htb_stop_time'}
#
# terminal_record_dict = {'session_id', 'terminal_image_id', 'env_description', 'terminal_id',
#                         'session_namespace', 'session_nodeport_url', 'session_description',
#                         'created_by_user', 'num_of_terminals', 'num_of_gpu_per_terminal',
#                         'num_of_cpu_per_terminal', 'status', 'retries', 'shutdown_requested',
#                         'auto_clean', 'message', 'created_date', 'updated_date', 'updated_timestamp',
#                         'htb_start_time', 'htb_stop_time'}

env_record_dict = {'session_id', 'environment_id', 'env_description', 'notebook_id',
                       'session_namespace', 'session_nodeport_url', 'session_description',
                       'created_by_user', 'created_date', 'updated_date', 'updated_timestamp', 'status'}

terminal_record_dict = {'session_id', 'terminal_image_id', 'env_description', 'terminal_id',
                        'session_namespace', 'session_nodeport_url', 'session_description',
                        'created_by_user', 'num_of_terminals', 'num_of_gpu_per_terminal',
                        'num_of_cpu_per_terminal', 'status', 'retries', 'shutdown_requested',
                        'auto_clean', 'message', 'created_date', 'updated_date', 'updated_timestamp'}

class Compare(object):

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.admin_db = AdminDB(BASE_DIR + '\conf\database.ini', 'sbrain_schema', 'namespace', 1)
        self.admin_records = self.admin_db.get_table_records('namespaces')
        self.admin_table = 'namespaces'
        self.env_table = 'environment_sessions'
        self.terminal_table = 'terminal_sessions'

    def compare_admin_with_namespace(self, tablename):
        if len(self.admin_records) == 0:
            return f"No Records Found."

        for row in self.admin_records:
            self.admin_id = row['id']
            self.recorded_pk = row['terminal_recoreded_pk'] if tablename == self.terminal_table else row['env_recorded_pk']
            self.schema_name = row['schema_name']
            self.namespace_name = row['namespace_name']
            self.conn_uri = row['sql_conn_str']
            self.tablename = tablename
            self.pool_size = 1

            self.namespace = Namespace(self.conn_uri, self.schema_name, self.namespace_name, self.pool_size, access=True)
            self.namespace_table_records = self.namespace.get_namespace_records(self.tablename, self.recorded_pk)

            if len(self.namespace_table_records) == 0:
                return f"No records found on table {self.tablename}"

            self.insert, self.update = self.compare_records_insert_update(self.namespace_table_records, self.tablename)
            self.message = f"Namespace Name: {self.namespace_name}, Table Name: {self.tablename}, " \
                           f"No. of Inserte Records: {self.insert}, Updated Column: recorded_pk"
            print(self.message)
            self.admin_db.admin_engine.release_db()
        return True

    def compare_records_insert_update(self,records:list, tablename):
        self.session_ids = []
        record_to_insert = {}
        count = 0
        table_dict_check = terminal_record_dict if tablename == 'terminal_sessions' else env_record_dict
        for record in records:
            if 'session_id' in record:
                self.session_ids.append(record['session_id'])
            for item in table_dict_check:
                if item in record:
                    record_to_insert[item] = record[item]
            count += 1
            # insert record..
            self.insert_result = self.admin_db.insert_table_records(tablename, record_to_insert)

        self.session_ids.sort(reverse=True)
        self.update_payload = {}
        if tablename == 'terminal_sessions':
            self.update_payload['terminal_recoreded_pk'] = self.session_ids[0]
        elif tablename == 'environment_sessions':
            self.update_payload['env_recorded_pk'] = self.session_ids[0]
        self.update_result = self.admin_db.update_admin_table(self.admin_table, self.admin_id, self.update_payload)

        return self.insert_result, self.update_result