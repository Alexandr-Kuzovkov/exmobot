<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 03.08.16
 * Time: 15:09
 */

require_once ('../include/functions.php');

$path = '../../db/';
$file = get_database_file();
$fullname = realpath($path . $file);
$db = (isset($_GET['db']))? $_GET['db'] : 'sqlite';
if ($db == 'sqlite'){
    $data = get_trades_data_sqlite($fullname);
}elseif($db == 'mysql'){
    $data = get_trades_data_mysql();
}
//print_r($data);
//exit();
$json = array();




    foreach($data as $session_id => $session_data){
        $json[$session_id] = array();

        foreach ($session_data as $pair => $items) {
            $count = 0;
            $json[$session_id][$pair] = array();
            $json[$session_id][$pair][$count] = array();

            if (isset($items[0])) {
                foreach ($items[0] as $key => $val) {
                    if ($key == 'pair' || $key == 'utime' || $key == 'session_id') continue;
                    $json[$session_id][$pair][$count][] = $key;
                }
            }

            foreach ($items as $item) {
                $json[$session_id][$pair][++$count] = array();
                foreach ($item as $key => $val) {
                    if ($key == 'pair' || $key == 'utime' || $key == 'session_id') continue;
                    $json[$session_id][$pair][$count][] = ($key == 'trade_date') ? date('d.m.Y H:i:s', $val) : $val;
                }

            }
        }
    }


    echo json_encode($json);


