import os

from base.admin import AdminDB


class Register(object):

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.admin_db = AdminDB(base_dir + r'\conf\database.ini', 'sbrain_schema', 'namespace', 1)

    def register_new_namespace(self, namespace: dict):
        table_name = 'namespaces'
        namespace.update({"terminal_recoreded_pk": 0, "env_recorded_pk": 0})
        self.admin_db.insert_table_records(table_name, namespace)


