<?php
/**
 * Класс для работы с СУБД Sqlite
 */

class SQLite implements Db{

    private static $instance = null;
    private static $db_file = null;
    private $tables = array();
    private $schema = SCHEMA_FILE;

    public static function get_instance(){
        if (self::$instance == null){
            self::$db_file = substr(__DIR__, 0, strpos(__DIR__, '/web')) . '/db/' . DB_FILE;
            self::$instance = new SQLite();
        }
        return self::$instance;
    }

    private function __construct(){
        $this->create_tables();
    }


    private function _get_connection(){
        $db = new SQLite3(self::$db_file);
        if (!$db) {
            throw new Exception('Error while opening database: ' . self::$db_file);
        }
        return $db;
    }

    /**
     * выполнение запроса к БД
     * @param $sql
     * @param $db
     * @return array|bool|result
     */
    public function query($sql){
        $db = $this->_get_connection();
        try{
            $sqlite_result = $db->query($sql);
            if (is_object($sqlite_result)){
                $result = array();
                while($row = $sqlite_result->fetchArray(SQLITE3_ASSOC))
                    $result[] = $row;
            }else{
                $result = $sqlite_result;
            }
        }catch(Exception $e){
            throw new Exception($e->getMessage());
        }

        $db->close();
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
        $condition_strings = array();
        foreach ($conditions as $field => $value){
            if (is_int($value) || is_float($value)){
                $condition_strings[] = strval($field) . strval($value);
            }elseif(is_null($value)){
                $condition_strings[] = strval($field) . ' NULL';
            }elseif(is_string($value)){
                $condition_strings[] = strval($field) . "'".SQLite3::escapeString($value)."'";
            }else{
                throw new Exception(__CLASS__ . __METHOD__ . 'Bad field value');
            }
        }
        $where_str = (count($condition_strings))? implode(' AND ', $condition_strings) : 1;
        $sql  = "SELECT * FROM $table WHERE {$where_str}";
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

        if (!is_array($data) || !count($data))
            throw new Exception(__CLASS__ . __METHOD__ . 'Dataset must be array');
        foreach ($data as $field => $value){
            if (is_int($value) || is_float($value)){
                $set_strings[] = strval($field) . '=' . strval($value);
            }elseif(is_null($value)){
                $set_strings[] = strval($field) . '=NULL';
            }elseif(is_string($value)){
                $set_strings[] = strval($field) . "='".SQLite3::escapeString($value)."'";
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
                $conditions_string[] = strval($field) . "'".SQLite3::escapeString($value)."'";
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

        foreach ($conditions as $field => $value){
            if (is_int($value) || is_float($value)){
                $conditions_string[] = strval($field) . strval($value);
            }elseif(is_null($value)){
                $conditions_string[] = strval($field) . ' NULL';
            }elseif(is_string($value)){
                $conditions_string[] = strval($field) . "'".SQLite3::escapeString($value)."'";
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
                        $value_str[] = "'".SQLite3::escapeString($value)."'";
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
                    $value_str[] = "'".SQLite3::escapeString($value)."'";
                }else{
                    throw new Exception(__CLASS__ . __METHOD__ . 'Bad field value');
                }
            }
            $sql = "INSERT INTO `{$table}` (" . implode(',',$fields_str) . ") VALUES (" . implode(',',$value_str) . ")";
            $db = $this->_get_connection();
            $result = $db->exec($sql);
            $db->close();
            return $result;
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
        $db = $this->_get_connection();
        $db->exec("BEGIN");
        foreach($queries as $sql){
            $db->exec($sql);
        }
        $db->exec("COMMIT");
        $db->close();
    }

    /**
     * возвращает имя базы данных
     * @return null
     */
    public function get_db_name(){
        return basename(self::$db_file);
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
                    $fls[] = implode('', array($field, ' INTEGER(', $fsize, ')', $fdef));
                }elseif($ftype == 'float') {
                    $fls[] = implode('', array($field, ' REAL(', $fsize, ')', $fdef));
                }elseif($ftype == 'text' || $ftype == 'str'){
                    $fls[] = implode('', array($field, ' TEXT ', $fdef));
                }else{
                    $fls[] = implode('', array($field, ' TEXT ', $fdef));
                }
            }
            $sql = implode(' ', array('CREATE TABLE IF NOT EXISTS ', $table,'(', implode(',',$fls), ')'));
            $this->query($sql);
        }

    }


    /**
     * удаление таблиц в БД
     */
    public function delete_tables(){
        try{
            $db = $this->_get_connection();
            $sql = "SELECT * FROM sqlite_master WHERE type = 'table'";
            $tables = array();
            $res = $db->query($sql);
            while( $row = $res->fetchArray(SQLITE3_ASSOC)){
                $tables[] = $row['name'];
            }
            foreach($tables as $table){
                $sql = "DROP TABLE IF EXISTS {$table}";
                $this->query($sql);
            }
        }catch (Exception $e){
            throw new Exception($e->getMessage());
        }
        $db->close();
    }

}