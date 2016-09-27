<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 03.09.16
 * Time: 19:34
 */

require_once('../include/functions.php');

$direction = (isset($_POST['direction']))? $_POST['direction'] : '';
$sqlite_db = get_database_file();
$path = '../../db/';
$fullname = realpath($path . $sqlite_db);

//print_r(get_database_data_sqlite($fullname));
//var_dump(get_database_data_mysql());

if ($direction == 'sqlite_mysql'){
    $res = move_data_sqlite_mysql($fullname);
    echo ($res === true)? 'Success' : $res;
}elseif ($direction == 'mysql_sqlite'){
    $res = move_data_mysql_sqlite();
    echo ($res === true)? 'Success' : $res;
}else{
    echo 'Direction not valid!';
}