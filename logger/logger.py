#coding=utf-8

import time
import os

class Logger:

    logfile = None

    def __init__(self, logfile=None):
        if logfile is not None:
            self.logfile = logfile

    #Подготовка сообщения к выводу
    def _prep_message(self, msg, prefix):
        date = prefix + ' ' + time.asctime(time.localtime())
        return date + ': ' + str(msg) + "\n"

    #Запись сообщения в лог-файл или в stdout
    def info(self, msg, prefix=''):
        if self.logfile is not None:
            try:
                f = open(self.logfile, 'a')
                f.write(self._prep_message(msg, prefix))
                f.close()
            except Exception, e:
                print 'Error: ' + e.strerror
                return False
        else:
            print self._prep_message(msg, prefix)

    #Удаление лог-файла
    def clear(self):
        if self.logfile is not None:
            try:
                os.remove(self.logfile)
            except Exception, e:
                print 'Error: ' + e.strerror
                return False

