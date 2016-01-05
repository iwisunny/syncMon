#!/usr/bin/env python
# _*_ coding: gb2312 _*_
__author__ = 'wangxi'
__doc__ = 'a unibox monitor utility'

import sys
import os
import string
import datetime
import time
import inspect
import json

import apps

import lib.logger
import lib.util
import lib.sqlite
import lib.inet

import psutil

base_dir = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
logger = lib.logger.Logger('uniboxMonitor', base_dir).get()


class UniboxMonitor():
    """�����ļ�·��"""
    conf_file = base_dir + '/monitor_app.ini'

    sync_conf_file = os.path.abspath(base_dir + '/../Sync/sync_app.ini')

    """���������"""
    conf = {}

    def __init__(self):
        """define data structure to keep monitor data"""
        self.ds = {
            'kiosk_id': ''
            , 'kiosk_ip': ''
            , 'connected': False
            , 'mem_used': ''
            , 'cpu_used': ''
            , 'disk_free_size': ''
            , 'udm_rental_started': False
            , 'udm_controller_started': False
            , 'last_sync_time': 0
        }

        conf = self.get_config()
        if len(conf) == 0:
            logger.error('invalid monitor config file')
            sys.exit(-1)

        self.conf = conf


    def get_config(self):
        conf = lib.util.parse_config(self.conf_file, 'MONITOR')
        if type(conf) is dict:
            return conf
        return {}

    def get_process_list(self):
        plist = {}
        for p in psutil.process_iter():
            plist[p.name()] = p.pid
        return plist

    def get_kiosk_id(self):
        kiosk_conf = lib.util.parse_config(self.conf['kiosk_conf'], '*')
        return kiosk_conf['kioskid']

    def get_client_ip(self):
        import socket

        return socket.gethostbyname(socket.gethostname())

    def get_attrs(self):
        self.ds['kiosk_id'] = self.get_kiosk_id()
        self.ds['kiosk_ip'] = self.get_client_ip()

        plist = self.get_process_list()
        self.ds['udm_rental_started'] = self.conf['udm_rental'] in plist.keys()
        self.ds['udm_controller_started'] = self.conf['udm_controller'] in plist.keys()

        self.ds['cpu_used'] = '%d' % psutil.cpu_percent()
        self.ds['mem_used'] = '%d' % psutil.virtual_memory().percent
        self.ds['disk_free_size'] = '%d' % psutil.disk_usage('c:\\').free
        self.ds['last_sync_time'] = (lib.util.parse_config(self.sync_conf_file, 'SYNC'))['last_sync']
        return self.ds

    def stat(self):
        py_svc = 'pythonservice.exe'
        if py_svc in self.get_process_list():
            print u'UniboxSvc����������'
            # pid_svc_daemon=self.get_process_list()[py_svc]
            # p=psutil.Process(pid=pid_svc_daemon)
            # print p
        else:
            print u'UniboxSvc������ֹͣ'

        self.endl()

        self.show_udm_proc()
        self.show_cpu()
        self.show_mem()
        self.show_disk()
        self.show_net()
        self.show_login_users()
        self.show_boot_time()

    def endl(self):
        print '---------------------------------------------\n'

    def show_udm_proc(self):
        print u'###���UDM_Rental, UDM_Controller����'
        plist = self.get_process_list()
        if 'UDM_Rental.exe' in plist.keys():
            print 'UDM_Rental ������'
        else:
            print 'UDM_Rental ��ֹͣ'

        if 'UDM_Controller.exe' in plist.keys():
            print 'UDM_Controller ������'
        else:
            print 'UDM_Controller ��ֹͣ'

        self.endl()

    def show_cpu(self):
        print u'###�鿴CPU��Ϣ'
        print u'CPU����: %s' % psutil.cpu_count()
        print u'CPU times: %s' % str(psutil.cpu_times())
        print u'CPUʹ����:% (���4��)'
        for x in range(4):
            print psutil.cpu_percent(interval=1)

        self.endl()

    def show_mem(self):
        print u'###�鿴�ڴ���Ϣ'
        vmem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        print u'�����ڴ�(bytes): %s' % str(vmem)
        print u'�����ڴ�(bytes): %s' % str(swap)
        print u'�ڴ�����: %.2f GB' % float(vmem.total / 1024.0 / 1024 / 1024)
        print u'�ڴ�������: %.2f %%' % vmem.percent
        self.endl()

    def show_disk(self):
        print u'###�鿴Ӳ����Ϣ'
        c_disk = psutil.disk_usage('c:\\')
        print u'Ӳ�̷���: %s' % str(psutil.disk_partitions('c\\'))
        print u'Ӳ��IO״��: %s' % str(psutil.disk_io_counters())
        print u'C��ʹ��״��: %s' % str(c_disk)
        print u'C�̴�С: %.2f GB' % float(c_disk.total / 1024.0 / 1024 / 1024), \
            u', ʣ��ռ�: %.2f GB' % float(c_disk.free / 1024.0 / 1024 / 1024)
        self.endl()

    def show_net(self):
        print u'###�鿴������Ϣ'
        net = psutil.net_io_counters()
        bytes_sent = '{0:.2f} Mb'.format(net.bytes_recv / 1024 / 1024)
        bytes_rcvd = '{0:.2f} Mb'.format(net.bytes_sent / 1024 / 1024)
        print u"������������ %s ������������ %s" % (bytes_rcvd, bytes_sent)
        self.endl()

    def show_boot_time(self):
        print u"�����ϴ�����ʱ�� %s" % datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        self.endl()

    def show_login_users(self):
        print u'###�鿴��ǰϵͳ��¼�û�'
        users_count = len(psutil.users())
        users_list = ",".join([u.name for u in psutil.users()])
        print u"��ǰ��%s���û����ֱ��� %s" % (users_count, users_list)
        self.endl()


if __name__ == '__main__':
    import time

    ub_mon = UniboxMonitor()
    try:
        ub_mon.stat()
    except Exception, e:
        logger.error(str(e))

    # while True:
    # logger.info( time.ctime()+': [Monitor]sending beacon request')
    #
    #     """ģ�����������beacon����"""
    #     data=ub_mon.get_attrs()
    #     post_param = {
    #         "data": json.dumps(data)
    #     }
    #     req_url=ub_mon.conf['server']+'/api/beacon?kioskId='+data['kiosk_id']
    #     logger.info('req url: '+req_url)
    #
    #     resp_body, resp_status,resp_code = lib.inet.http_post(req_url, ub_mon.conf['server'], post_param)
    #     if len(resp_body)>0:
    #         resp_body = json.loads(resp_body)
    #
    #     print resp_body, resp_status, resp_code
    #
    #     time.sleep(10)


