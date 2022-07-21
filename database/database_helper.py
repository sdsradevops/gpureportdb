from sqlalchemy import *
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.reflection import Inspector
import time
from contextlib import contextmanager


class FILTER_OPERATOR(object):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class Database(object):

    def __init__(self):
        self.engine = None
        self.metadata = None
        self.inspector = None
        self.initialized = False


    def print_search_path(self, engine):
        """
        :param engine: SQLAlchemy engine to connect the database
        :return: print the schema and connection
        """
        self.engine = engine
        print("search path: {}".format(self.engine.execute('show search_path').fetchall()[0][0]))

    
    def read_marker(self, engine):
        """
        :param engine: SQLAlchemy engine to connect the database
        :return: if marker table found or not.
        """
        self.engine = engine
        self.found = False
        try:
            self.print_search_path(self.engine)
            rc = engine.execute('select * from sbrain_schema.marker;')

            if not rc:
                return self.found

            for row in rc:
                if row['schema_version'] == '1.0':
                    self.found = True
                    break

            return self.found

        except SQLAlchemyError as e:
            print(e)
            return self.found


    def setup_db_access(self, conn_str, pool_size, schema_name):
        """
        :param conn_str: postgres URI connection string
        :param pool_size: multithreading pool size
        :param schema_name: schema name of database
        :return:
        """
        self.schema_name = schema_name
        while True:
            try:
                if self.initialized:
                    break
                # retry the database engine, connection, metadata init
                if self.engine is not None:
                    self.engine.dispose()

                self.engine = create_engine(conn_str, pool_size=pool_size, max_overflow=0, echo=False,
                                    echo_pool=False, pool_pre_ping=True)
                self.metadata = MetaData(bind=self.engine, schema= self.schema_name)
                MetaData.reflect(self.metadata)
                self.inspector = Inspector.from_engine(self.engine)
                
                if not self.initialized:
                    self.initialized = self.read_marker(self.engine)
                
                if self.initialized:
                    return self.engine, self.metadata, self.inspector

                time.sleep(10)

            except Exception as ex:
                self.setup_db_access_exception(self.engine, ex)

        if not self.initialized:
            # giving up after many retries
            if not self.initialized:
                raise Exception('Database not started.')


    def setup_db_access_exception(self, engine, ex):
        """
        :param engine: SQLAlchemy engine to connect the database
        :param ex: if error comes raise error
        :return:
        """
        self.engine = engine
        if ex.args is not None and 'psycopg2.ProgrammingError' in ex.args[0]:
            if "access denied" in ex.args[0]:
                raise ex
            elif "Unknown database" in ex.args[0]:
                import time
                for i in range(60):
                    time.sleep(10)
                    try:
                        self.metadata = MetaData(bind=self.engine, reflect=True)
                        self.inspector = Inspector.from_engine(self.engine)
                        break
                    except Exception as e:
                        if ex.args is not None and 'psycopg2.ProgrammingError' in ex.args[0] and "Unknown database" in ex.args[0]:
                            print('Trial {} to connect to db...".format(i)')
        else:
            raise ex


    def release_db(self):
        """
        :return: realse the connection db
        """
        if self.engine is not None:
            self.engine.dispose()


class DatabaseHelper(Database):

    def __init__(self, conn_uri, pool_size, schema_name):
        """
        :param conn_uri: postgresql connection URI
        :param pool_size: multithreading pool size
        :param schema_name: schema name
        """
        # if self.engine is None or self.metadata is None or self.inspector is None:
        #     raise RuntimeError("Database access setup not completed. "
        #                        "\nPlease make sure the database access is setup for the application correctly.")

        super().__init__()
        self.conn = None
        self.schema_prefix = schema_name + '.'
        self.engine, self.metadata, self.inspector = Database().setup_db_access(conn_uri, pool_size, schema_name=schema_name)

    @contextmanager
    def connection(self):
        self.conn = self.engine.connect()
        try:
            yield self.conn
        except:
            raise
        finally:
            # log.debug("closing connection")
            self.conn.close()

    @contextmanager
    def connection_with_transaction(self):
        self.conn = self.engine.connect()
        trans = self.conn.begin()
        try:
            # log.debug("returning new connection")
            yield self.conn
            # log.debug("commiting transaction..")
            trans.commit()
        except:
            # log.debug("rolling back transaction..")
            trans.rollback()
            raise
        finally:
            # log.debug("closing connection")
            self.conn.close()

    def table(self, tablename):
        """
        :param tablename: Table name
        :return: return if table exists
        """
        self.tablename = self.schema_prefix + tablename
        if self.tablename in self.metadata.tables:
            return self.metadata.tables[self.tablename]
        elif self.tablename in self.inspector.get_view_names():
            return self.table(tablename)


    def get_last_rows(self, tablename, last_record):
        """
        :param tablename: table name
        :param last_record: fetch records after the passed int.
        :return: records found.
        """
        tbl = self.table(tablename)
        statement = select([tbl]).where(tbl.c.session_id > last_record)
        result = self.__execute_statement(tablename, statement, fetch_all=True)
        if result is None:
            return []
        else:
            result_set = []
            for row in result:
                result_set.append(dict(row))
            return result_set


    def get_all_rows(self, tablename):
        """
        :param tablename: table name
        :return: records found.
        """
        tbl = self.table(tablename)
        statement = select([tbl])
        result = self.__execute_statement(tablename, statement, fetch_all=True)
        if result is None:
            return []
        else:
            result_set = []
            for row in result:
                result_set.append(dict(row))
            return result_set

    def insert(self, table_name, kwargs):
        """
        :param table_name: table name
        :param kwargs: args
        :return:
        """
        table = self.table(table_name)
        # self.log.debug("creating a new row in table - [%s]" % table_name)
        # self.log.debug("insert parameters are - ")
        # self.log.debug(kwargs)
        ## regex for parsign unique key exception - (.* Duplicate entry )(.*)( for key)(.*)
        statement = table.insert().values(**kwargs)
        try:
            result = self.conn.execute(statement)
        except SQLAlchemyError as e:
            raise e
        list_rows = result.inserted_primary_key

        # return value is the integer primary key
        #self.log.debug("created a new row in table - [%s]" % table_name)
        return int(list_rows[0])

    def update_table(self, tablename, filters, kwargs):
        """
        :param tablename: table name
        :param filters: for Where clause
        :param kwargs: args
        :return:
        """
        # self.log.debug("updating table - [%s]" % tablename)
        # self.log.debug("update parameters are - ")
        # self.log.debug(kwargs)
        # self.table(tablename)
        query = "update sbrain_schema.%s SET " % tablename
        values = []
        params = {}
        for k, v in kwargs.items():
            values.append("%s = :%s" % (k, k))
            params[k] = v

        query = "%s %s" % (query, ",".join(values))

        where_clauses, where_params = self.__generate_where_clauses(filters)

        params.update(where_params)

        query = "%s %s" % (query, where_clauses)

        statement = text(query)
        result = self.conn.execute(statement, **params)

        assert result.rowcount >= 1

        if result is not None and result.rowcount >= 1:
            return True
        else:
            return False

    def __execute_statement(self, tablename, statement, fetch_all=False, **bind_parameters):
        """
        :param tablename: table name
        :param statement: SQL query
        :param fetch_all: bool
        :param bind_parameters:
        :return:
        """
        result = None

        #self.log.debug("retrieving row(s) from table - [%s]" % tablename)
        if fetch_all is True:
            if bind_parameters is None:
                result = self.conn.execute(statement)
                #self.log.debug("retrieved all row from table - [%s]" % tablename)
            else:
                # binding parameters in a dynamic sql query prevents SQL Injection
                result = self.conn.execute(statement, **bind_parameters)
                #self.log.debug("retrieved all row from table - [%s]" % tablename)

        else:
            if bind_parameters is None:
                result = self.conn.execute(statement).fetchone()
                #self.log.debug("retrieved one row from table - [%s]" % tablename)
            else:
                result = self.conn.execute(statement, **bind_parameters).fetchone()
                #self.log.debug("retrieved one row from table - [%s]" % tablename)

        return result

    def __generate_where_clauses(self, filters):
        """
        :param filters: WHERE clasuse
        :return: str of WHERE clause, dict of parameters
        """

        if not filters:
            return "", {}

        where_clauses = "where "

        params = {}
        count = len(filters)

        for i in range(count):
            column, operation, val = filters[i]

            if operation == 'equals':
                where_clauses += " %s = :%s " % (column, column)
                params[column] = val
            elif operation == "in":
                if isinstance(val, list):
                    in_vals = ["'{}'".format(x) for x in val]
                    in_vals = ",".join(in_vals)
                    where_clauses += " %s in (%s) " % (column, in_vals)
                else:
                    where_clauses += " %s in (%s) " % (column, val)
            else:
                where_clauses += " %s %s :%s " % (column, operation, column)
                params[column] = val

            if i != (count - 1):
                where_clauses = " %s %s " % (where_clauses, FILTER_OPERATOR.AND)
        return where_clauses, params

    def get_filtered_rows(self, tablename, filters, offset, size):
        """
        :param tablename: table name
        :param filters: for Where clause
        :param offset: offset value
        :param size: page size
        :return:
        """
        query = "select * from sbrain_schema.%s " % tablename
        params = {}

        where_clauses, where_params = self.__generate_where_clauses(filters)

        params.update(where_params)

        query = "%s %s" % (query, where_clauses)
        if offset is not None:
            query = "%s OFFSET %s LIMIT %s" % (query, str(offset), str(size))

        statement = text(query)
        result = self.conn.execute(statement, **params)

        if result is None:
            return []
        else:
            result_set = []
            for row in result:
                result_set.append(dict(row))
            return result_set

