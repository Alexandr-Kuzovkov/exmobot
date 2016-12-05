<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 27.09.16
 * Time: 23:28
 */

require_once ('../include/functions.php');


$db = (isset($_GET['db']))? $_GET['db'] : 'sqlite';
$path = '../../db/';
$file = get_database_file();

$fullname = realpath($path . $file);

if ($db == 'sqlite'){
    ob_start();
    $sqlite = SQLite::get_instance();
    $sqlite->delete_tables();
    $sqlite->create_tables();
    header('Location: /database?db=sqlite');
    ob_end_clean();
    exit();
}elseif ($db == 'mysql'){
    ob_start();
    $mysql = MySQL::get_instance();
    $mysql->delete_tables();
    $mysql->create_tables();
    header('Location: /database?db=mysql');
    ob_end_clean();
    exit();
}else{
    header('Location: /');
    exit();
}