<?php

    interface Db{

        public static function get_instance();

        /**
         * выполнение запроса к БД
         * @param $sql
         * @return array|bool|mysqli_result
         */
        public function query($sql);

        /**
         * получение записей из таблицы по условию
         * @param $table
         * @param array $conditions
         * @return array|bool|mysqli_result
         * @throws Exception
         */
        public function get($table, $conditions = array());


        /**
         * получение всех записей из таблицы
         * @param $table
         * @param array $conditions
         * @return array|bool|mysqli_result
         * @throws Exception
         */
        public function get_list($table);


        /**
         * Обновление записей в таблице
         * @param $table
         * @param array $data
         * @param array $conditions
         * @return array|bool|mysqli_result
         * @throws Exception
         */
        public function update($table, Array $data, $conditions = array());

        /**
         * удаление записи в таблице
         * @param $table
         * @param array $conditions
         * @return array|bool|mysqli_result
         * @throws Exception
         */
        public function delete($table, $conditions = array());

        /**
         * добавление записей в таблицу
         * @param $table
         * @param array $data
         * @return array|bool|mysqli_result
         * @throws Exception
         */
        public function insert($table, Array $data);


        /**
         * выполнение транзакции
         * @param array $queries
         * @throws Exception
         */
        public function transaction(Array $queries);

        public function get_db_name();
        
    }