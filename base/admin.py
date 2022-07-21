from conf.dbConfig import AuthConfig
from configparser import ConfigParser

class CLAUSE_OPERATOR(object):
    LIKE = "LIKE"
    EQUALS = "="
    NOT_EQUAL = "!="
    IN = "in"
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="
    BETWEEN = "BETWEEN"
    SINCE = ">="

class AdminDB(AuthConfig):

    def __init__(self, uri, schema_name, namespace, pool_size, section='postgresql'):
        super().__init__(uri, schema_name, namespace, pool_size)
        parser = ConfigParser()
        # read config file
        parser.read(uri)
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, uri))
        # AuthConfig initialize
        self.admin_engine = AuthConfig(db['uri'], schema_name, namespace, pool_size, access=True)


    def get_table_records(self, tablename):
        with self.admin_engine.connection():
            self.records = self.admin_engine.get_all_rows(tablename)
        return self.records

    def insert_table_records(self, tablename, payload):
        with self.admin_engine.connection():
            self.insert_records = self.admin_engine.insert(tablename, payload)
        return self.insert_records


    def update_admin_table(self, tablename, session_id, kwargs):
        with self.admin_engine.connection():
            self.update_records = self.admin_engine.update_table(tablename, [('id', CLAUSE_OPERATOR.EQUALS,session_id)],
                                                               kwargs )
        return self.update_records

    def get_filtered_table_records(self, tablename, **kwargs):
        args = []
        offset = None

        for k, v in kwargs.items():
            f_ele = None
            if k == "start_time":
                f_ele = ("created_date", CLAUSE_OPERATOR.GREATER_THAN_OR_EQUAL, v)
            elif k == "end_time":
                f_ele = ("created_date", CLAUSE_OPERATOR.LESS_THAN_OR_EQUAL, v)
            elif k == "namespace_name":
                f_ele = ("session_namespace", CLAUSE_OPERATOR.LIKE, v)
            elif k == "user_name":
                f_ele = ("created_by_user", CLAUSE_OPERATOR.LIKE, v)
            if f_ele:
                args.append(f_ele)
            if "page" in kwargs and "size" in kwargs:
                offset = (kwargs["page"] - 1) * kwargs["size"] if kwargs["page"] > 1 else 0
        with self.admin_engine.connection():
            self.records = self.admin_engine.get_filtered_rows(tablename, args, offset, kwargs["size"])
        return self.records
