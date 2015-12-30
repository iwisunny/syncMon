#!/usr/bin/env python
# _*_ coding: utf-8 _*_
__author__ = 'wangxi'
__doc__ = ''

import logging
import datetime
import os
import sys
import inspect

class Logger():
    log_file = ''.join(str(datetime.date.today()).split('-')) + '.log'
    debug_mode=True

    def __init__(self, log_label='uniboxSvc', log_dir=None):
        self.log_label = log_label
        self.log_file = Logger.log_file

        if log_dir is None:
            this_file_dir=os.path.dirname(inspect.getfile(inspect.currentframe()))
            log_dir = os.path.abspath(this_file_dir+os.sep+'..')
        if os.sep+'log' not in log_dir:
            log_dir += os.sep+'log'

        self.log_dir = log_dir

        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

        _logger = logging.getLogger(self.log_label)

        if Logger.debug_mode is True:
            _logger.setLevel(logging.DEBUG)
        else:
            _logger.setLevel(logging.INFO)

        """add handler to logger"""
        formatter = logging.Formatter("%(name)-5s %(asctime)-10s %(pathname)-10s \
        --line:%(lineno)2d %(levelname)5s --message:%(message)10s")

        logfile_handler = logging.FileHandler(self.log_dir + os.sep + self.log_file)
        logfile_handler.setFormatter(formatter)
        _logger.addHandler(logfile_handler)

        """output log msg to stderr"""
        stream_handler = logging.StreamHandler(sys.stderr)
        _logger.addHandler(stream_handler)

        self.logger = _logger

    def get(self):
        """!!remove additonal handlers"""
        if len(self.logger.handlers)>2:
            self.logger.handlers=self.logger.handlers[:2]
        return self.logger


