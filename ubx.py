#!/usr/bin/env python
# _*_ coding: gb2312 _*_
__author__ = 'wangxi'
__doc__ = 'Unibox Service as daemon process'

import sys
import os
import getopt

"""need pre-install pywin32"""
import time

import lib.logger
import lib.inet

import traceback

log = lib.logger.Logger().get()


def usage():
    print """\
    unibox X controller <wangxi@unibox.com.cn>
    Usage: ubx [-opt|--option] command
        install             ��װUniboxSvc����
        auto                ��װUniboxSvc������ϵͳ������
        start               ����UniboxSvc����
        stop                ֹͣUniboxSvc����
        status              ���UniboxSvc����״̬
        remove              ж��UniboxSvc����
        reload              ����UniboxSvc����(�޸�����������ubx)
        -l|--log            �鿴UniboxSvc��־
        -e|--edit           �޸�UniboxSvc����
        -h|--help           �г���������
        -v|--version        �鿴����汾

        -s|--sync
            -s all          ͬ��ȫ��������
            -s ad           ͬ��ad
            -s title        ͬ��title
            -s movie        ͬ��movie
            -s kiosk        ͬ��kiosk
            -s slot         ͬ��slot
            -s inv          ͬ��inventory
            -f|--force      ǿ��ͬ�� (����������ͬ���Ϳ�������)
            -s log          �鿴ͬ����־
            -s edit         �޸�ͬ������

        -m|--monitor
            -m run          ���м��
            -m stat         ���ܼ������
            -m plist        ���������б�
            -m cpu          CPUʹ����
            -m mem          �ڴ�ʹ����
            -m disk         Ӳ��ʹ����
            -m net          ����IO
            -m log          �鿴�����־
            -m edit         �޸ļ������
    """


def get_logfile():
    import datetime
    today_log = ''.join(str(datetime.date.today()).split('-')) + '.log'
    return today_log

def get_cwd():
    import inspect
    cur_dir=os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
    if 'dist' in cur_dir:
        cur_dir=cur_dir.replace('dist', '')
    if cur_dir[len(cur_dir)-1] != '/':
        cur_dir += '/'
    return cur_dir


def main():
    """sys.argv[0] is current script file"""
    args = sys.argv[1:]
    if len(args) == 0:
        usage()
        sys.exit(0)

    """check force tag"""
    use_force=False
    if '-f' in args:
        use_force=True
        args.remove('-f')
    if '--force' in args:
        use_force=True
        args.remove('--force')

    """simplify cmd"""
    ctl_cmd = ['install', 'auto', 'start', 'stop', 'status', 'remove', 'reload']
    if len(args) == 1 and args[0] in ctl_cmd:
        b = args.pop()
        args = ['-c', b]

    try:
        opt, args = getopt.getopt(args, "hc:s:m:vle",
                                  ["help", "control=",
                                   "sync=", "monitor=", "version", "log", "edit"])
    except getopt.GetoptError, err:
        log.error(err)
        sys.exit(-1)

    for cmd, arg in opt:
        """sync service manager, delegation"""
        if cmd in ('-c', '--control'):
            if arg in ['auto', 'install', 'remove']:
                if arg == 'auto':
                    sys.argv = sys.argv[:1]
                    arg = '--startup auto install'
                import subprocess
                import inspect
                try:
                    cur_dir=get_cwd()
                    call_sync = subprocess.check_output('python ' + cur_dir + 'svc.py ' + arg)
                    log.info(call_sync)
                except Exception, e:
                    log.error(e.message)

            elif arg in ['start', 'stop', 'status', 'reload']:
                import svc
                _svc = svc.SvcManager()
                if arg == 'status':
                    _svc.getStatus()
                elif arg == 'start':
                    _svc.start()
                elif arg == 'stop':
                    _svc.stop()
                elif arg == 'reload':
                    _svc.restart()
            else:
                print 'ubx install|auto|remove|start|reload|stop|status'
                sys.exit(1)

        elif cmd in ['-s', '--sync']:
            import apps.Sync.sync as mod_sync

            ub_sync=mod_sync.UniboxSync()
            ub_sync.set_force_sync(is_force=use_force)

            if arg=='log':
                today_log=get_logfile()
                log_file = mod_sync.base_dir + '/log/' + today_log
                os.system('notepad ' + log_file)
            elif arg=='edit':
                conf_file = ub_sync.conf_file
                os.system('notepad ' + conf_file)
                sys.exit(0)
            else:
                sync_host = ub_sync.conf['sync_server']
                """filter server hostname"""
                if sync_host[len(sync_host) - 1] == '/':
                    sync_host = sync_host[:-1]
                if 'http://' in sync_host:
                    sync_host = sync_host.replace('http://', '')

                print('===>check network connection...')
                if lib.inet.check_connection(sync_host) is False:
                    log.error('network connection error')
                    return
                print('===>connection ok')
                log.info('===>begin sync ' + str(arg) + ' items...')

                try:
                    sync_st = time.time()
                    if arg == 'all':
                        ub_sync.sync_all()
                    elif arg == 'ad':
                        ub_sync.sync_ad()
                    elif arg == 'title':
                        ub_sync.sync_title()
                    elif arg == 'movie':
                        ub_sync.sync_movie()
                    elif arg == 'inv':
                        ub_sync.sync_inventory()
                    elif arg == 'kiosk':
                        ub_sync.sync_kiosk()
                    elif arg == 'slot':
                        ub_sync.sync_slot()

                    sync_ed = time.time()
                    log.info('===>end sync ' + str(arg) + ' items, time elapsed ' + str(sync_ed - sync_st) + 'sec')

                except Exception, e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    log.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback) ) )

                    log.error('===>sync ' + str(arg) + ' items failed, ' + str(e))


        elif cmd in ['-m', '--monitor']:
            import apps.Monitor.monitor as mod_monitor

            ub_mon = mod_monitor.UniboxMonitor()

            if arg == 'run':
                print '[Monitor]Testing monitor every 5 sec\n'
                while True:
                    ub_mon.run()
                    time.sleep(ub_mon.monitor_interval)

            elif arg == 'stat':
                ub_mon.stat()
            elif arg == 'plist':
                import psutil
                psutil.test()
            elif arg == 'cpu':
                ub_mon.show_cpu()
            elif arg == 'mem':
                ub_mon.show_mem()
            elif arg == 'disk':
                ub_mon.show_disk()
            elif arg == 'net':
                ub_mon.show_net()
            elif arg == 'log':
                today_log = get_logfile()
                log_file = mod_monitor.base_dir + '/log/' + today_log
                os.system('notepad ' + log_file)
            elif arg == 'edit':
                conf_file = ub_mon.conf_file
                os.system('notepad ' + conf_file)
                sys.exit(0)

        else:
            if cmd in ('-v', '--version'):
                """just a joke"""
                print 'V1.0.1'
                sys.exit(0)
            elif cmd in ('-h', '--help'):
                usage()
                sys.exit(0)
            elif cmd in ('-l', '--log'):
                log_file = get_cwd() + 'log/' + get_logfile()
                os.system('notepad ' + log_file)
            elif cmd in ('-e', '--edit'):
                conf_file = get_cwd()+'unibox.ini'
                os.system('notepad ' + conf_file)
                sys.exit(0)

if __name__ == '__main__':
    main()