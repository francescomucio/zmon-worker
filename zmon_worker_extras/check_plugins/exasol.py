#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Query Exasol
"""

from zmon_worker_monitor.adapters.ifunctionfactory_plugin import IFunctionFactoryPlugin, propartial
from turbodbc import connect

EXASOL_DRIVER_LOCATION = '/var/lib/zmon/exasol/cd gitlibexaodbc.so'

class ExaplusFactory(IFunctionFactoryPlugin):
    def __init__(self):
        super(ExaplusFactory, self).__init__()
        # fields from config
        self._exasol_user = None
        self._exasol_pass = None

    def configure(self, conf):
        """
        Called after plugin is loaded to pass the [configuration] section in their plugin info file
        :param conf: configuration dictionary
        """
        self._exasol_user = conf['exasol_user']
        self._exasol_pass = conf['exasol_pass']

    def create(self, factory_ctx):
        """
        Automatically called to create the check function's object
        :param factory_ctx: (dict) names available for Function instantiation
        :return: an object that implements a check function
        """
        return propartial(ExaplusWrapper, cluster=factory_ctx.get('cluster'), password=self._exasol_pass,
                          user=self._exasol_user, schema=factory_ctx.get('schema'))


class ExaplusWrapper(object):
    def __init__(self, cluster, user='', password='', schema=''):
        self._err = None
        self._out = None
        self.user = user
        self.__password = password
        self.cluster = cluster
        self.schema = schema
        self.__driver = EXASOL_DRIVER_LOCATION

    def query(self, query):
        connection = connect(
            driver=self.__driver,
            EXAHOST=self.cluster,
            EXASCHEMA=self.schema,
            EXAUID=self.user,
            EXAPWD=self.__password
        )

        cursor = connection.cursor()
        cursor.execute(query)

        columns = []
        values = []

        if cursor:
            # get_headers
            for col in cursor.description:
                columns.append(col[0])

            # get_values
            value = {}

            for row in cursor:
                for i, col in enumerate(columns):
                    value[col] = row[i]
                values.append(value)

        return values
