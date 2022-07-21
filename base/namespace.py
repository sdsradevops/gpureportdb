from conf.dbConfig import AuthConfig

class Namespace(AuthConfig):

    def __init__(self, uri, schema_name, namespace, pool_size, access=True):
        super().__init__(uri, schema_name, namespace, pool_size, access)
        self.namespace_engine = AuthConfig(uri, schema_name, namespace, pool_size, access=True)

    def get_namespace_records(self,tablename, last_record):
        with self.namespace_engine.connection():
            self.total_rows = self.namespace_engine.get_last_rows(tablename, last_record)
        self.namespace_engine.release_db()  # close the connection of db.
        return self.total_rows