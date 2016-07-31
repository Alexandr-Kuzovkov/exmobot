<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 22.05.16
 * Time: 15:01
 */
    class Db{

        static private $DB_NAME = 'mailer';
        static private $DB_USER = 'root';
        static private $DB_PASS = 'rootroot';
        static private $DB_HOST = 'localhost';
        static private $DB_CHARSET = 'utf8';
        static private $table_emails = 'emails';
        static private $table_settings = 'settings';


        static public function query($sql){
            $db = mysqli_connect(self::$DB_HOST, self::$DB_USER, self::$DB_PASS, self::$DB_NAME);
            if (!$db) {
                die('Ошибка подключения (' . mysqli_connect_errno() . ') '
                    . mysqli_connect_error());
            }
            $db->set_charset(self::$DB_CHARSET);
            //$esc_sql= mysqli_real_escape_string($db, $sql);
            //echo $sql;
            $mysql_res = mysqli_query($db, $sql);
            if (mysqli_errno($db) == 0){
                if (is_object($mysql_res)){
                    $result = array();
                    while($row = mysqli_fetch_assoc ($mysql_res))
                        $result[] = $row;
                    mysqli_free_result($mysql_res);
                }else{
                    $result = $mysql_res;
                }
            }else{
                echo mysqli_error($db);
                $result = false;
            }
            //var_dump($result); exit();
            mysqli_close($db);
            return $result;
        }

        /*создание таблиц в БД если еще не созданы*/
        static public function create_tables(){
            $table_emails = self::$table_emails;
            $table_settings = self::$table_settings;
            $sql1 = "
            CREATE TABLE IF NOT EXISTS `{$table_emails}` 
                  (
                    `id` INT(10) NOT NULL AUTO_INCREMENT,
                    `email` varchar(255) NOT NULL,
                    `subject` varchar(255) DEFAULT '',
                    `message` TEXT DEFAULT '',
                    `status` INT(1) DEFAULT 0, 
                    `ctime` INT(11) NOT NULL DEFAULT 0,
                    `images` TEXT DEFAULT '',
                    PRIMARY KEY (`id`)
                  )ENGINE=InnoDB DEFAULT CHARSET=utf8;
            ";

            $sql2 = "
             CREATE TABLE IF NOT EXISTS `{$table_settings}` 
                  (
                    `id` INT(10) NOT NULL AUTO_INCREMENT,
                    `key` varchar(255) NOT NULL,
                    `value` varchar(255) NOT NULL,
                    PRIMARY KEY (`id`)
                  )ENGINE=InnoDB DEFAULT CHARSET=utf8;
            ";

            self::query($sql1);
            self::query($sql2);

        }

        /**
         * пересоздание таблиц БД
         */
        static public function reset_database(){
            $table_emails = self::$table_emails;
            $table_settings = self::$table_settings;
            $sql1 = "DROP TABLE IF EXISTS `{$table_emails}`";
            $sql2 = "DROP TABLE IF EXISTS `{$table_settings}`";
            self::query($sql1);
            self::query($sql2);
            self::create_tables();

            $sql = "
             INSERT INTO `{$table_settings}` (`key`,`value`) VALUES
                ('mail_per_once', 50),
                ('pause', 3),
                ('enable', 0),
                ('from', 'admin@mail.ru')
            ";
            self::query($sql);
        }

        static public function insert_emails_from_file($filename){
            $db = mysqli_connect(self::$DB_HOST, self::$DB_USER, self::$DB_PASS, self::$DB_NAME);
            if (!$db) {
                die('Ошибка подключения (' . mysqli_connect_errno() . ') '
                    . mysqli_connect_error());
            }
            $handle = @fopen($filename, "r");
            $table_emails = self::$table_emails;
            if ($handle) {
                mysqli_query($db, "BEGIN");
                while (($email = fgets($handle, 4096)) !== false) {
                    $email = trim($email);
                    $ctime = time();
                    if (!$email) continue;
                    $sql = "INSERT INTO $table_emails (email, ctime) VALUES('{$email}', $ctime)";
                    mysqli_query($db, $sql);
                }
                mysqli_query($db, "COMMIT");
                if (!feof($handle)) {
                    echo "Error: unexpected fgets() fail\n";
                }
                fclose($handle);
            }
        }


        static public function add_email($email, $subject='none', $message='none'){
            $table_emails = self::$table_emails;
            $sql = "INSERT INTO `{$table_emails}` (email, subject, message) VALUES('{$email}','{$subject}','{$message}')";
            return self::query($sql);
        }

        /*получение email по значению, id или всех*/
        static public function get_email($id=null){
            $table_emails = self::$table_emails;
            if($id == null) $sql = "SELECT * FROM $table_emails";
            elseif (is_string($id)) $sql = "SELECT * FROM $table_emails WHERE email='{$id}' LIMIT 1";
            elseif (is_int($id)) $sql = "SELECT * FROM $table_emails WHERE id=$id LIMIT 1";
            else return null;
            return self::query($sql);
        }

        /*получение отправленных emails*/
        static public function get_all_sended_emails(){
            $table_emails = self::$table_emails;
            $sql = "SELECT * FROM $table_emails WHERE status=1";
            return self::query($sql);
        }

        /*получение неотправленных emails*/
        static public function get_all_nosended_emails(){
            $table_emails = self::$table_emails;
            $sql = "SELECT * FROM $table_emails WHERE status=0";
            return self::query($sql);
        }

        /*пометка email как отработанного*/
        static function mark_email_as_sended($email){
            $table_emails = self::$table_emails;
            $ctime = time();
            $sql = "UPDATE $table_emails SET status=1, ctime=$ctime WHERE email='{$email}'";
            return self::query($sql);
        }


        /*пометка всех email как неотработанных*/
        static function mark_allemail_as_nosended(){
            $table_emails = self::$table_emails;
            $ctime = time();
            $sql = "UPDATE $table_emails SET status=0, ctime=$ctime";
            return self::query($sql);
        }

        /*пометка всех email как отработанных*/
        static function mark_allemail_as_sended(){
            $table_emails = self::$table_emails;
            $ctime = time();
            $sql = "UPDATE $table_emails SET status=1, ctime=$ctime";
            return self::query($sql);
        }

        /**получение неотработанных emails в кoличестве
         * @param $n
         * @return array|bool|mysqli_result|null
         */
        static public function get_nosended_emails($n){
            $table_emails = self::$table_emails;
            $sql = "SELECT * FROM $table_emails WHERE status=0 LIMIT $n";
            return self::query($sql);
        }

        /**
         * установка темы и тела писем
         * @param $subject
         * @param $message
         * @param $images
         * @return array|bool|mysqli_result|null
         */
        static public function set_nosended_email_param($subject, $message, $images){
            $table_emails = self::$table_emails;
            $subject = addslashes($subject);
            $message = addslashes($message);
            $images = addslashes(implode(',',$images));
            $sql = "UPDATE $table_emails SET subject='{$subject}', message='{$message}', images='{$images}' WHERE status=0";
            return self::query($sql);
        }

        /**
         * установка темы и тела всех писем
         * @param $subject
         * @param $message
         * @param $images
         * @return array|bool|mysqli_result|null
         */
        static public function set_email_param($subject, $message, $images){
            $table_emails = self::$table_emails;
            $subject = addslashes($subject);
            $message = addslashes($message);
            $images = addslashes(implode(',',$images));
            $sql = "UPDATE $table_emails SET subject='{$subject}', message='{$message}', images='{$images}'";
            return self::query($sql);
        }

        /**
         * удаление всех emails
         * @return array|bool|mysqli_result
         */
        static public function delete_all_emails(){
            $table_emails = self::$table_emails;
            $sql = "DELETE FROM $table_emails";
            return self::query($sql);
        }

        /**
         * удаление всех отправленных emails
         * @return array|bool|mysqli_result
         */
        static public function delete_all_sended_emails(){
            $table_emails = self::$table_emails;
            $sql = "DELETE FROM $table_emails WHERE status=1";
            return self::query($sql);
        }

        /**
         * получение значения настройки
         * @param $key
         * @return null
         */
        static public function get_option($key){
            $table_settings = self::$table_settings;
            $sql = "SELECT * FROM $table_settings WHERE `key`='{$key}' LIMIT 1";
            $res = self::query($sql);
            return (is_array($res))? trim($res[0]['value']) : null;
        }

        /**
         * установка значения настройки
         * @param $key
         * @param $value
         * @return array|bool|mysqli_result|null
         */
        static public function set_option($key, $value){
            $table_settings = self::$table_settings;
            $key = strval($key);
            if (self::get_option($key) == null) $sql = "INSERT INTO $table_settings (`key`,`value`) VALUES({'$key'},'{$value}')";
            else $sql = "UPDATE $table_settings SET `value`='{$value}' WHERE `key`='{$key}'";
            return self::query($sql);
        }
    }




