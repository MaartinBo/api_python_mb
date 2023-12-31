import logging as logger
import os

import pymysql

from mbtest.src.configs.host_config import DB_HOST
from mbtest.src.utilities.credentialsUtility import CredentialsUtility


class DBUtility(object):

    def __init__(self):
        creds_helper = CredentialsUtility()
        self.creds = creds_helper.get_db_credentials()

        self.machine = os.environ.get("MACHINE")
        assert self.machine, f'Environment variable "Machine" must be set.'

        self.wp_host = os.environ.get('WP_HOST')
        assert self.wp_host, f'Environment variable "WP_HOST" must be set.'

        if self.machine == 'docker' and self.wp_host == 'local':
            raise Exception(f"Can't run test in docker if WP_HOST=local")

        self.env = os.environ.get('ENV', 'test')

        self.host = DB_HOST[self.machine][self.env]['host']
        self.socket = DB_HOST[self.machine][self.env]['socket']
        self.port = DB_HOST[self.machine][self.env]['port']
        self.database = DB_HOST[self.machine][self.env]['database']
        self.table_prefix = DB_HOST[self.machine][self.env]['table_prefix']

    def create_connection(self, timeout=30):
        if self.wp_host == 'local':
            # local for mac use socket instead of port, so if you use windows local change socket to port
            connection = pymysql.connect(host=self.host, user=self.creds['db_user'], password=self.creds['db_password'],
                                         unix_socket=self.socket, connect_timeout=timeout)
        elif self.wp_host == 'mamp':
            connection = pymysql.connect(host=self.host, user=self.creds['db_user'], password=self.creds['db_password'],
                                         port=self.port, connect_timeout=timeout)
        else:
            raise Exception("Unknown  WP_HOST.")
        return connection

    def execute_select(self, sql):
        conn = self.create_connection()

        try:
            logger.debug(f"Executing sql: {sql}")
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(sql)
            rs_dict = cur.fetchall()
            cur.close()
        except Exception as e:
            raise Exception(f"Failed runnning sql: {sql} \n Error: {str(e)}")
        finally:
            conn.close()

        return rs_dict

    def execute_sql(self, sql):
        pass
