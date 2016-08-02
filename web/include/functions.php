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


?>