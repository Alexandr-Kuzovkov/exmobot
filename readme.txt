exmobot - скрипт для автоматической торговли на биржах криптовалют
В текущей версии поддерживаются Exmo, Wex (бывшая btc-e), Poloniex

I. Требования:
    - OC Linux (Ubuntu 14.04 and older)
    - Apache2, php 5.5+, 7.0+ , mysql
    - Python 2.7 (Обычно уже установлен в системе)
    - git


II. Установка (на примере Ubuntu 14.04)
    1. Скачиваем исходники:
        cd /var/www
        git clone https://github.com/kuzovkov/exmobot

    2. Прописываем ключи и секреты от API криптовалютных бирж в файлах:
            - exchange/btce/config.py,
            - exchange/exmo/config.py,
            - exchange/poloniex/config.py
            - web/wsgi/accounts.conf
            Также в файле storage/MySQL/crud.py прописываем параметры для mysql базы, например:
            dbhost = 'localhost'
            dbname = 'exmobot'
            dbuser = 'you-user'
            dbpass = 'you-password'

    3. Устанавливаем Mysql connector для Python:
       скачиваем тут https://dev.mysql.com/downloads/connector/python/
       устанавливаем sudo dpkg -i mysql-connector-python-cext_2.1.7-1ubuntu14.04_amd64.deb
    
    4. Настраиваем веб сервер:

        sudo nano /etc/apache2/sites-available.conf
        Пример конфига apache2:
        <VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        ServerName exmobot.loc
    
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/exmobot/web/html
    
        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn
    
        <Directory /var/www/exmobot/web/html>
                   Options Indexes FollowSymLinks
                    AllowOverride All
            </Directory>
         WSGIScriptAlias /test /var/www/exmobot/web/wsgi/test.py
            WSGIScriptAlias /api /var/www/exmobot/web/wsgi/api.py
            WSGIDaemonProcess exmobot.loc processes=2 threads=15 display-name=%{GROUP}
            WSGIProcessGroup exmobot.loc
    
    
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    
        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
        </VirtualHost>
    
    sudo apt-get install -y libapache2-mod-wsgi
    sudo a2enmod, вводим wsgi
    sudo a2ensite exmobot.conf
    sudo service apache2 restart

    добавляем строку в /etc/hosts:
    127.0.0.1	exmobot.loc

    Открываем в браузере http://exmobot.loc
    Должны увидеть окно логина в web интерфейс


III. Использование

    Боты запускаются с помощью cron.
    Параметром при запуске служит полный путь к файлу конфигурации.
    Могут запускаться несколько экзкмпляров ботов, работающих на разных
    биржах, с разными стратегиями и т.д.
    Указания боту какую использовать биржу и какую торговую стратегию и
    другие параметры содержатся в файле конфигурации.
    Примеры:
    Открываем для редактирования crontab:
    $crontab -e
    Записываем туда:
    * * * * * <?php echo $work_dir?>bot.py --config-file=<?php echo $work_dir?>conf/btce_eth_usd_flip.conf
    */3 * * * * <?php echo $work_dir?>bot.py -c <?php echo $work_dir?>conf/exmo_eth_usd_flip.conf

    Первая строка будет запускать бота каждую минуту с файлом конфигурации btce_eth_usd_flip.conf
    Вторая строка будет запускать бота каждые 3 минуты с файлом конфигурации exmo_eth_usd_flip.conf
    Для приостановки работы бота нужно закомментировать соответствующую строчку.

    Для просмотра показаний датчиков (вкладка "Оборудование") должна быть установлена утилита sensors
    (sudo apt-get install lm-sensors)

    На вкладке "База данных -> Запрос" можно делать запросы к базе данных, в том числе и запросы на модификацию.
    Пример удаления записей из таблицы старше 1 часа:
    DELETE FROM session_data WHERE utime < (strftime('%s','now') - 3600)

    Пример экспорта запроса из базы MySQL в файл .csv, который может быть открыт в Exel:
    SELECT 'utime', 'exchange', 'pair', 'orders_qt_sell', 'orders_qt_buy'
    UNION ALL
    (SELECT utime, exchange, pair, orders_qt_sell, orders_qt_buy FROM stat WHERE exchange='btce'
    INTO OUTFILE '/tmp/stat_data3.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n')

    Файлы конфигов в каталоге conf
    Скрипты торговых стратегий в каталоге strategy, последняя версия торговой стратегии flip6.py

    
    
    


 