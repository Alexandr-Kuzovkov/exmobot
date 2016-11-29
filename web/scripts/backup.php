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
$dump_name = $_SERVER['SERVER_NAME'] . '.dump';


if ($db == 'sqlite'){
    ob_start();
    $dump_name .= '.sqlite';
    header('Content-Disposition: attachment; filename=' . $dump_name);
    header('Content-Length: ' . filesize($fullname));
    header('Keep-Alive: timeout=5; max=100');
    header('Connection: Keep-Alive');
    header('Content-Type: application/octet-stream');
    ob_end_clean();
    readfile($fullname);
    exit();
}elseif($db == 'mysql'){
    ob_start();
    $h_temp = tmpfile();
    $tmp_file_metadata = stream_get_meta_data($h_temp);
    $tmp_file_name = $tmp_file_metadata['uri'];
    $dump_name .= '.sql';
    $comm = 'mysqldump -u' . DB_USER . ' -p' . DB_PASS . ' --opt --databases ' . DB_NAME . ' > ' . $tmp_file_name;
    //echo $comm;
    system($comm);
    header('Content-Disposition: attachment; filename=' . basename($dump_name));
    header('Content-Length: ' . filesize($tmp_file_name));
    header('Keep-Alive: timeout=5; max=100');
    header('Connection: Keep-Alive');
    header('Content-Type: application/octet-stream');
    ob_end_clean();
    readfile($tmp_file_name);

}else{
    exit();
}