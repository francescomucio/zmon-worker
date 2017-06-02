#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Query Exasol
"""

import tempfile
import subprocess
import os

from zmon_worker_monitor.adapters.ifunctionfactory_plugin import IFunctionFactoryPlugin, propartial
from turbodbc import connect


class ExaplusFactory(IFunctionFactoryPlugin):
    def __init__(self):
        super(ExaplusFactory, self).__init__()
        # fields from config
        self._exasol_user = None
        self._exasol_pass = None
        self._exasol_driver = None

    def configure(self, conf):
        """
        Called after plugin is loaded to pass the [configuration] section in their plugin info file
        :param conf: configuration dictionary
        """
        self._exasol_user = conf['exasol_user']
        self._exasol_pass = conf['exasol_pass']
        self._exasol_driver = conf['exasol_driver']

    def create(self, factory_ctx):
        """
        Automatically called to create the check function's object
        :param factory_ctx: (dict) names available for Function instantiation
        :return: an object that implements a check function
        """
        return propartial(ExaplusWrapper, cluster=factory_ctx['cluster'], password=self._exasol_pass,
                          user=self._exasol_user, schema=factory_ctx['schema'],
                          driver=self._exasol_driver)


class ExaplusWrapper(object):
    def __init__(self, cluster, user='', password='', schema='', driver=''):
        self._err = None
        self._out = None
        self.user = user
        self.__password = password
        self.cluster = cluster
        self.schema = schema
        self.driver = driver

    def query(self, query):
        try:
            connection = connect(
                driver=self.driver,
                EXAHOST=self.cluster,
                EXASCHEMA=self.schema,
                EXAUID=self.user,
                EXAPWD=self.__password)
            cursor = connection.cursor()

            cursor.execute(query)
            self._out = cursor

        except Exception as err:
            self._err = err

        return self

    def result(self):
        columns = []
        values = []

        if self._out:
            # get_headers
            for col in self._out.description:
                columns.append(col[0])

            # get_values
            value = {}

            for row in self._out:
                for i, col in enumerate(columns):
                    value[col] = row[i]
                values.append(value)

        return values, self._err
