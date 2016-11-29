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
if (!isset($_FILES['dump']) || $_FILES['dump']['error'] != 0){
    header('Location: /');
    exit();
}

if ($db == 'sqlite'){
    $res = move_uploaded_file($_FILES['dump']['tmp_name'], $fullname);
    chmod($fullname, 0666);
    header('Location: /database?db=sqlite');
    exit();
}elseif ($db == 'mysql'){
    ob_start();
    $dump_name = $_FILES['dump']['tmp_name'];
    $comm = 'mysql -u' . DB_USER . ' -p' . DB_PASS . ' < ' . $dump_name;
    system($comm);
    header('Location: /database?db=mysql');
    ob_end_clean();
    exit();
}else{
    header('Location: /');
    exit();
}