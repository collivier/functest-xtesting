#!/usr/bin/env python

# Copyright (c) 2016 ZTE Corp and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""Define the parent classes of all Xtesting Features.

Feature is considered as TestCase offered by Third-party. It offers
helpers to run any python method or any bash command.
"""

import logging
import subprocess
import time

from xtesting.core import testcase

__author__ = ("Serena Feng <feng.xiaowei@zte.com.cn>, "
              "Cedric Ollivier <cedric.ollivier@orange.com>")


class Feature(testcase.TestCase):
    """Base model for single feature."""

    __logger = logging.getLogger(__name__)

    def execute(self, **kwargs):
        """Execute the Python method.

        The subclasses must override the default implementation which
        is false on purpose.

        The new implementation must return 0 if success or anything
        else if failure.

        Args:
            kwargs: Arbitrary keyword arguments.

        Returns:
            -1.
        """
        # pylint: disable=unused-argument,no-self-use
        return -1

    def run(self, **kwargs):
        """Run the feature.

        It allows executing any Python method by calling execute().

        It sets the following attributes required to push the results
        to DB:

            * result,
            * start_time,
            * stop_time.

        It doesn't fulfill details when pushing the results to the DB.

        Args:
            kwargs: Arbitrary keyword arguments.

        Returns:
            TestCase.EX_OK if execute() returns 0,
            TestCase.EX_RUN_ERROR otherwise.
        """
        self.start_time = time.time()
        exit_code = testcase.TestCase.EX_RUN_ERROR
        self.result = 0
        try:
            if self.execute(**kwargs) == 0:
                exit_code = testcase.TestCase.EX_OK
                self.result = 100
        except Exception:  # pylint: disable=broad-except
            self.__logger.exception("%s FAILED", self.project_name)
        self.stop_time = time.time()
        return exit_code


class BashFeature(Feature):
    """Class designed to run any bash command."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super(BashFeature, self).__init__(**kwargs)
        dir_results = "/var/lib/xtesting/results"
        self.result_file = "{}/{}.log".format(dir_results, self.case_name)

    def execute(self, **kwargs):
        """Execute the cmd passed as arg

        Args:
            kwargs: Arbitrary keyword arguments.

        Returns:
            0 if cmd returns 0,
            -1 otherwise.
        """
        ret = -1
        try:
            cmd = kwargs["cmd"]
            with open(self.result_file, 'w+') as f_stdout:
                proc = subprocess.Popen(cmd.split(), stdout=f_stdout,
                                        stderr=subprocess.STDOUT)
            ret = proc.wait()
            self.__logger.info(
                "Test result is stored in '%s'", self.result_file)
            if ret != 0:
                self.__logger.error("Execute command: %s failed", cmd)
        except KeyError:
            self.__logger.error("Please give cmd as arg. kwargs: %s", kwargs)
        return ret