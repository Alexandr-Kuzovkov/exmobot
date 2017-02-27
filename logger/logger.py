#coding=utf-8

import time
import os

class Logger:

    logfile = None

    def __init__(self, logfile=None):
        if logfile is not None:
            self.logfile = logfile

    #Подготовка сообщения к выводу
    def _prep_message(self, msg, prefix, status):
        date = prefix + ' ' + time.asctime(time.localtime())
        return date + ' ' + status + ': ' + str(msg) + "\n"

    #Запись сообщения в лог-файл или в stdout
    def info(self, msg, prefix=''):
        status = '<INFO>'
        if self.logfile is not None:
            try:
		f = open(self.logfile, 'a')
                f.write(self._prep_message(msg, prefix, status))
                f.close()
            except Exception, e:
                print 'Logger error: ' + e.strerror
                return False
        else:
            print self._prep_message(msg, prefix, status)

    # Запись сообщения об ошибке в лог-файл или в stdout
    def error(self, msg, prefix=''):
        status = '<ERROR>'
        if self.logfile is not None:
            try:
                f = open(self.logfile, 'a')
                f.write(self._prep_message(msg, prefix, status))
                f.close()
            except Exception, e:
                print 'Logger error: ' + e.strerror
                return False
        else:
            print self._prep_message(msg, prefix, status)

    #Удаление лог-файла
    def clear(self):
        if self.logfile is not None:
            try:
                os.remove(self.logfile)
            except Exception, e:
                print 'Logger error: ' + e.strerror
                return False

