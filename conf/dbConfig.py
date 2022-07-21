from database.database_helper import DatabaseHelper

class AuthConfig(DatabaseHelper):

    def __init__(self, uri, schema_name, namespace, pool_size, access:bool=False):
        """
        :param uri: postgres connection URI to connect database
        :param schema_name: postgres schema Name
        :param namespace: namespace Name
        :param pool_size: multithreading pool size
        :param access: bool: True or False
        """
        self.schema_name = schema_name
        self.NAMESPACE = namespace
        self.URI = uri
        # invoking the __init__ of the parent class
        if access == True:
            super().__init__(uri, pool_size, schema_name)
            self.helper = DatabaseHelper(self.URI, pool_size, self.schema_name)


    def print_namespcae(self):
        print('Namespace:', self.NAMESPACE)
