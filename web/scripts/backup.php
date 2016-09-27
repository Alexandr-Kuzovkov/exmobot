<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 03.09.16
 * Time: 19:48
 */

require_once ('../include/functions.php');

$db = (isset($_GET['db']))? $_GET['db'] : 'sqlite';
$path = '../../db/';
$file = get_database_file();
$fullname = realpath($path . $file);

if ($db == 'sqlite'){
    ob_start();
    header('Content-Disposition: attachment; filename=' . $file);
    header('Content-Length: ' . filesize($fullname));
    header('Keep-Alive: timeout=5; max=100');
    header('Connection: Keep-Alive');
    header('Content-Type: application/octet-stream');
    ob_end_clean();
    readfile($fullname);
    exit();
}elseif($db == 'mysql'){
    ob_start();
    $dump_name = substr($fullname, 0, strpos($fullname, $file)) . 'temp.sql';
    //echo $dump_name;
    $comm = 'mysqldump -u' . DB_USER . ' -p' . DB_PASS . ' --opt --databases ' . DB_NAME . ' > ' . $dump_name;
    //echo $comm;
    system($comm);
    header('Content-Disposition: attachment; filename=' . basename($dump_name));
    header('Content-Length: ' . filesize($dump_name));
    header('Keep-Alive: timeout=5; max=100');
    header('Connection: Keep-Alive');
    header('Content-Type: application/octet-stream');
    ob_end_clean();
    readfile($dump_name);

}else{
    exit();
}