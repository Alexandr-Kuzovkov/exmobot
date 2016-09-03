<?php
/**
 * Класс для работы с СУБД Sqlite
 */

class SQLite implements Db{

    private static $instance = null;
    private static $db_file = null;
    private $tables = array();

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
                $condition_strings[] = strval($field) . "'{$value}'";
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
                $set_strings[] = strval($field) . "='{$value}'";
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
                $conditions_string[] = strval($field) . "'{$value}'";
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
                $conditions_string[] = strval($field) . "'{$value}'";
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
                        $value_str[] = "'{$value}'";
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
                    $value_str[] = "'{$value}'";
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
     * инициализация схемы БД
     */
    private function init_tables(){
        $this->tables['orders'] = array(
            'schema' => "CREATE TABLE IF NOT EXISTS orders 
                  (
                    order_id INTEGER,
                    pair,
                    quantity REAL,
                    price REAL, 
                    order_type, 
                    session_id, 
                    utime INTEGER
                  )"
        );





        $this->tables['session_data'] = array(
            'schema' => "CREATE TABLE IF NOT EXISTS session_data 
                  (
                   key, 
                   value, 
                   type, 
                   session_id, 
                   utime INTEGER
                  )"
        );

        $this->tables['user_trades'] = array(
            'schema' => "CREATE TABLE IF NOT EXISTS user_trades 
                  (
                    trade_id, 
                    order_id, 
                    pair, 
                    quantity REAL, 
                    price REAL, 
                    amount REAL, 
                    trade_type, 
                    session_id, 
                    trade_date INTEGER, 
                    utime INTEGER
                  )"
        );

        $this->tables['balance'] = array(
            'schema' => "CREATE TABLE IF NOT EXISTS balance 
                  (
                   currency, 
                   amount REAL, 
                   session_id, 
                   utime INTEGER
                  )"
        );

    }

    /**
     * создание таблиц в БД
     */
    public function create_tables(){
        $this->init_tables();
        foreach($this->tables as $name => $table){
            $sql = $table['schema'];
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