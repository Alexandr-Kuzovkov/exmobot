<?php

    

    /*установка пункта меню активным если в нем находимся*/
    function check_active($url){
        $real_uri = $_SERVER['REQUEST_URI'];
        if (($p = strpos($real_uri, '?')) === false){
            $uri = substr($real_uri, 1);
        }else{
            $uri = substr($real_uri, 1, strpos($real_uri, '?') - 1);
        }
        echo ($uri == $url)? 'class="active"' : '';
    }




    function send_email(){
        $email = (isset($_POST['email']))? $_POST['email'] : '';
        $email_data = Db::get_email($email);
        if (is_array($email_data)){
            $to = $email_data[0]['email'];
            $subject = $email_data[0]['subject'];
            $message = $email_data[0]['message'];
            $from = Db::get_option('from');
            $images = $email_data[0]['images'];
            $images = explode(',', $images);
            $files = array();
            $count = 0;
            if(is_array($images)){
                foreach($images as $image){
                    if(!file_exists($image)) continue;
                    $count++;
                    $files[$count]['name'] = $image;
                    $files[$count]['type'] = 'application/octet-stream';
                }
            }
            
            if (Mailer::send3($to, $subject, $message, $from, $files)){
                Db::mark_email_as_sended($to);
            }
        }
    }

    /**
     * возвращает список изображений, имеющихся в каталоге изображений
     * @param $dir
     */
    function get_images($dir){
        $images = array();
        if (is_array($files = scandir($dir))){
            foreach($files as $file){
                if ($file == '.' || $file == '..') continue;
                $images[$file] = IMG_DIR . $file;
            }
        }
        return $images;
    }

    /**
     * возвращает список Log-файлов
     */
    function get_log_files(){
        $path = '../../log';
        $logs_files = array();
        $files = scandir($path);
        if (is_array($files) && count($files)){
            foreach ($files as $file){
                if ($file == '.' || $file == '..') continue;
                $logs_files[] = $file;
            }
        }
        return $logs_files;
    }

    /**
     * возвращает список config-файлов
     */
    function get_conf_files(){
        $path = '../../conf';
        $conf_files = array();
        $files = scandir($path);
        if (is_array($files) && count($files)){
            foreach ($files as $file){
                if ($file == '.' || $file == '..') continue;
                $conf_files[] = $file;
            }
        }
        return $conf_files;
    }


    /**
     * возвращает список файлов со стратегиями
     */
    function get_strategy_files(){
        $path = '../../strategy';
        $strategy_files = array();
        $files = scandir($path);
        if (is_array($files) && count($files)){
            foreach ($files as $file){
                if ($file == '.' || $file == '..') continue;
                if (pathinfo($file, PATHINFO_EXTENSION) !== 'py') continue;
                if ($file === '__init__.py') continue;
                $strategy_files[] = $file;
            }
        }
        return $strategy_files;
    }

    /**
     * возвращает имя фала базы данных в каталоге db 
     * (первый попавшийся файл с раширением sqlite)
     */
    function get_database_file(){
        $path = '../../db';
        $db_file = false;
        $files = scandir($path);
        if (is_array($files) && count($files)){
            foreach ($files as $file){
                if ($file == '.' || $file == '..') continue;
                if (pathinfo($file, PATHINFO_EXTENSION) !== 'sqlite') continue;
                $db_file = $file;
                break;
            }
        }
        return $db_file;
    }

    /**
     * возвращает содержимое всех таблиц базы данных sqlite
     * либо конкретной таблицы если задано ее имя
     *@param $db_name полное имя файла базы данных
     *@param  $table_name имя таблицы БД
     */
    function get_database_data($db_name, $table_name = null){
        try{
            $db = new SQLite3($db_name);
            $sql = "SELECT * FROM sqlite_master WHERE type = 'table'";
            $result = array();
            $tables = array();
            $res = $db->query($sql);
            while( $row = $res->fetchArray(SQLITE3_ASSOC)){
                $tables[] = $row['name'];
		    }
            foreach($tables as $table){
                if ($table_name !== null && $table_name !== $table) continue;
                $sql = "SELECT * FROM $table";
                $res = $db->query($sql);
                $count = 0;
                $result[$table] = array();
                while( $row = $res->fetchArray(SQLITE3_ASSOC)){
                    $result[$table][$count++] = $row;
                }
            }
            $db->close();
            return $result;

        }catch(Exception $e){
            return $e->getMessage();
        }
    }

    /**
     * выполняет произвольный запрос к базе
     */
    function exec_query($db_name, $sql){
        try{
            $db = new SQLite3($db_name);
            $res = $db->query($sql);
            $result = array();
            $count = 0;
            while( $row = $res->fetchArray(SQLITE3_ASSOC)){
                $result[$count++] = $row;
            }
            return $result;
        }catch(Exception $e){
            return $e->getMessage();
        }

    }

    /**
     * возвращает данные по изменению балансов
     * сгруппированные по сессиям и валютам и отсортированные по времени
     */
    function get_balances_data($db_name){
        $selector = array();
        $rows = exec_query($db_name, 'SELECT session_id FROM balance GROUP BY session_id');
        if (is_array($rows)){
            foreach ($rows as $row){
                $session_id = $row['session_id'];
                $rows2 = exec_query($db_name, "SELECT currency FROM balance WHERE session_id='{$session_id}' GROUP BY currency");
                if (is_array($rows2)){
                    foreach($rows2 as $row2){
                        $selector[$session_id][] = $row2['currency'];
                    }
                }

            }
        }
        $result = array();
        foreach($selector as $session_id => $currencies){
            foreach($currencies as $currency){
                $rows = exec_query($db_name, "SELECT utime, amount FROM balance WHERE currency='{$currency}' AND session_id='{$session_id}' ORDER BY utime ASC");
                $result[$session_id][$currency] = $rows;
            }
        }

        return $result;

    }

    /**
     * возвращает данные по сделкам
     * сгруппированные по сессиям и валютным парам и отсортированные по времени
     */
    function get_trades_data($db_name){
        $selector = array();
        $rows = exec_query($db_name, 'SELECT session_id FROM user_trades GROUP BY session_id');
        if (is_array($rows)){
            foreach ($rows as $row){
                $session_id = $row['session_id'];
                $rows2 = exec_query($db_name, "SELECT pair FROM user_trades WHERE session_id='{$session_id}' GROUP BY pair");
                if (is_array($rows2)){
                    foreach($rows2 as $row2){
                        $selector[$session_id][] = $row2['pair'];
                    }
                }

            }
        }
        $result = array();
        foreach($selector as $session_id => $pairs){
            foreach($pairs as $pair){
                $rows = exec_query($db_name, "SELECT * FROM user_trades WHERE pair='{$pair}' AND session_id='{$session_id}' ORDER BY trade_date DESC");
                $result[$session_id][$pair] = $rows;
            }
        }

        return $result;

    }

?>