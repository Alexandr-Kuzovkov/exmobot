<?php
/**
 * Класс для работы с СУБД MySQL
 */

class MySQL implements Db{

    private $DB_CHARSET = 'utf8';
    private static $instance = null;
    private $db_host = null;
    private $db_user = null;
    private $db_pass = null;
    private $db_name = null;
    private $tables = array();
    private $schema = SCHEMA_FILE;

    public static function get_instance(){
        if (self::$instance == null){
            self::$instance = new MySQL(DB_HOST, DB_USER, DB_PASS, DB_NAME);
        }
        return self::$instance;
    }

    private function __construct($db_host, $db_user, $db_pass, $db_name){
        $this->db_host = $db_host;
        $this->db_user = $db_user;
        $this->db_pass = $db_pass;
        $this->db_name = $db_name;
        $this->create_tables($this->schema);
    }

    /**
     * выполнение запроса к БД
     * @param $sql
     * @return array|bool|mysqli_result
     */
    public function query($sql){
        $db = mysqli_connect($this->db_host, $this->db_user, $this->db_pass, $this->db_name);
        if (!$db) {
            die('Connect Error (' . mysqli_connect_errno() . ') '
                . mysqli_connect_error());
        }
        $db->set_charset($this->DB_CHARSET);

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

        mysqli_close($db);
        return $result;
    }

    /**
     * получение записей из таблицы по условию
     * @param $table
     * @param array $conditions
     * @return array|bool|mysqli_result
     * @throws Exception
     */
    public function get($table, $conditions = array()){
        mysqli::set_charset ( $this->DB_CHARSET );
        $condition_strings = array();
        foreach ($conditions as $field => $value){
            if (is_int($value) || is_float($value)){
                $condition_strings[] = strval($field) . strval($value);
            }elseif(is_null($value)){
                $condition_strings[] = strval($field) . ' NULL';
            }elseif(is_string($value)){
                $condition_strings[] = strval($field) . mysqli::real_escape_string ($value);
            }else{
                throw new Exception(__CLASS__ . __METHOD__ . 'Bad field value');
            }
        }
        $where_str = (count($condition_strings))? implode(' AND ', $condition_strings) : 1;
        $sql  = "SELECT * FROM $table WHERE {$where_str}" ;
        return $this->query($sql);
    }


    /**
     * получение всех записей из таблицы
     * @param $table
     * @param array $conditions
     * @return array|bool|mysqli_result
     * @throws Exception
     */
    public function get_list($table){
        $sql = "SELECT * FROM $table";
        return $this->query($sql);
    }


    /**
     * Обновление записей в таблице
     * @param $table
     * @param array $data
     * @param array $conditions
     * @return array|bool|mysqli_result
     * @throws Exception
     */
    public function update($table, Array $data, $conditions = array()){
        $set_strings = array();
        $conditions_string = array();
         mysqli::set_charset ( $this->DB_CHARSET );
        if (!is_array($data) || !count($data))
            throw new Exception(__CLASS__ . __METHOD__ . 'Dataset must be array');
        foreach ($data as $field => $value){
            if (is_int($value) || is_float($value)){
                $set_strings[] = strval($field) . '=' . strval($value);
            }elseif(is_null($value)){
                $set_strings[] = strval($field) . '=NULL';
            }elseif(is_string($value)){
                $set_strings[] = strval($field) . "='" . mysqli::real_escape_string ($value)."'";
            }else{
                throw new Exception(__CLASS__ . __METHOD__ . 'Bad field value');
            }
        }

        foreach ($conditions as $field => $value){
            if (is_int($value) || is_float($value)){
                $conditions_string[] = strval($field) . strval($value);
            }elseif(is_null($value)){
                $conditions_string[] = strval($field) . ' NULL';
            }elseif(is_string($value)){
                $conditions_string[] = strval($field) .  "'".mysqli::real_escape_string ($value)."'";
            }else{
                throw new Exception(__CLASS__ . __METHOD__ . 'Bad field value');
            }
        }
        $where_str = (count($conditions_string))? implode(' AND ', $conditions_string) : 1;
        $sql = "UPDATE $table SET " . implode(',', $set_strings) . ' WHERE ' . $where_str;
        return $this->query($sql);
    }

    /**
     * удаление записи в таблице
     * @param $table
     * @param array $conditions
     * @return array|bool|mysqli_result
     * @throws Exception
     */
    public function delete($table, $conditions = array()){
        $set_strings = array();
        $conditions_string = array();
        mysqli::set_charset ( $this->DB_CHARSET );
        foreach ($conditions as $field => $value){
            if (is_int($value) || is_float($value)){
                $conditions_string[] = strval($field) . strval($value);
            }elseif(is_null($value)){
                $conditions_string[] = strval($field) . ' NULL';
            }elseif(is_string($value)){
                $conditions_string[] = strval($field) . "'".mysqli::real_escape_string ($value)."'";
            }else{
                throw new Exception(__CLASS__ . __METHOD__ . 'Bad field value');
            }
        }
        $where_str = (count($conditions_string))? implode(' AND ', $conditions_string) : 1;
        $sql = "DELETE FROM $table WHERE " . $where_str;
        return $this->query($sql);
    }


    /**
     * добавление записей в таблицу
     * @param $table
     * @param array $data
     * @return array|bool|mysqli_result
     * @throws Exception
     */
    public function insert($table, Array $data){
         mysqli::set_charset ( $this->DB_CHARSET );
        if (!is_array($data))
            throw new Exception(__CLASS__ . __METHOD__ . 'Dataset must be array');
        if (!count($data))
            return false;
        $fields_str = array();
        $value_str = array();
        $queries = array();
        if (isset($data[0]) && is_array($data[0])){
            foreach ($data[0] as $field => $value){
                $fields_str[] = "`{$field}`";
            }

            foreach($data as $row){
                $value_str = array();
                foreach ($row as $field => $value){
                    //echo gettype($value);
                    if (is_int($value) || is_float($value)){
                        $value_str[] = strval($value);
                    }elseif(is_null($value)){
                        $value_str[] = ' NULL';
                    }elseif(is_string($value)){
                        $value_str[] = "'" . mysqli::real_escape_string ($value)."'";
                    }else{
                        throw new Exception(__CLASS__ . __METHOD__ . 'Bad field value');
                    }
                }
                $sql = "INSERT INTO `{$table}` (" . implode(',',$fields_str) . ") VALUES (" . implode(',',$value_str) . ")";
                $queries[] = $sql;
            }
            $this->transaction($queries);
        }else{
            foreach ($data as $field => $value){
                $fields_str[] = "`{$field}`";
            }
            foreach ($data as $field => $value){
                if (is_int($value) || is_float($value)){
                    $value_str[] = strval($value);
                }elseif(is_null($value)){
                    $value_str[] = ' NULL';
                }elseif(is_string($value)){
                    $value_str[] = "'" . mysqli::real_escape_string ($value)."'";
                }else{
                    throw new Exception(__CLASS__ . __METHOD__ . 'Bad field value');
                }
            }
            $sql = "INSERT INTO `{$table}` (" . implode(',',$fields_str) . ") VALUES (" . implode(',',$value_str) . ")";
            return $this->query($sql);
        }
    }


    /**
     * выполнение транзакции
     * @param array $queries
     * @throws Exception
     */
    public function transaction(Array $queries){
        if (!is_array($queries) || !count($queries))
            throw new Exception(__CLASS__ . __METHOD__ . 'Queries must be array');
        $db = mysqli_connect($this->db_host, $this->db_user, $this->db_pass, $this->db_name);
        if (!$db) {
            die('Ошибка подключения (' . mysqli_connect_errno() . ') '
                . mysqli_connect_error());
        }
        mysqli_query($db, "BEGIN");
        foreach($queries as $sql){
            mysqli_query($db, $sql);
        }
        mysqli_query($db, "COMMIT");
    }

    /**
     * возвращает имя базы данных
     * @return null
     */
    public function get_db_name(){
        return $this->db_name;
    }


    /**
     * Создание таблиц в БД
     * @param null $schema
     * @throws Exception
     */
    public function create_tables($schema=null){
        if($schema == null)
            $schema = $this->schema;
        if (!file_exists($schema)){
            throw new Exception("Config-file $schema not exists!");
        }
        $tables = parse_ini_file ($schema, true, INI_SCANNER_RAW);
        foreach($tables as $table=>$rows){
            $fls = array();
            foreach($rows as $field=>$params_str){
                $fparams = explode(' ', $params_str);
                $ftype = trim($fparams[0]);
                $fsize = trim($fparams[1]);
                if (count($fparams) > 2){
                    $fdef = trim($fparams[2]);
                    if (in_array($fdef, array('null','NULL','None','NONE'))){
                        $fdef = ' DEFAULT NULL ';
                    }elseif(is_numeric($fdef)) {
                        $fdef = ' DEFAULT ' . $fdef;
                    }else{
                        $fdef = ' DEFAULT ' . "'" . $fdef . "'";
                    }
                }else{
                    $fdef = '';
                }
                if ($ftype == 'int'){
                    $fls[] = implode('', array('`',$field, '`', ' INT(', $fsize, ')', $fdef));
                }elseif($ftype == 'float') {
                    $fls[] = implode('', array('`', $field, '`', ' REAL(', $fsize, ')', $fdef));
                }elseif($ftype == 'text'){
                    $fls[] = implode('', array('`', $field, '`', ' TEXT ', $fdef));
                }elseif($ftype == 'datetime') {
                    $fls[] = implode('', array('`', $field, '`', ' DATETIME ', $fdef));
                }else{
                    $fls[] = implode('', array('`',$field, '`', ' varchar(', $fsize, ')', $fdef));
                }
            }
            $sql = implode(' ', array('CREATE TABLE IF NOT EXISTS ', $table,'(', implode(',',$fls), ')', ' ENGINE=InnoDB DEFAULT CHARSET=utf8'));
            $this->query($sql);
        }

    }


    /**
     * удаление таблиц в БД
     */
    public function delete_tables(){
        $res = $this->query("SHOW TABLES");
        foreach($res as $row){
            $table = $row['Tables_in_' . $this->get_db_name()];
            $sql = "DROP TABLE IF EXISTS `{$table}`";
            $this->query($sql);
        }
    }

}