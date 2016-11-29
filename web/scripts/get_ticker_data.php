<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 26.11.16
 * Time: 23:41
 */

$exchange = (isset($_POST['exchange']))? $_POST['exchange'] : null;
$start = (isset($_POST['start']))? intval($_POST['start']) : null;
$end = (isset($_POST['end']))? intval($_POST['end']) : null;


function cmp($a, $b){
    if ($a == $b) {
        return 0;
    }
    return ($a < $b)? -1 : 1;
}

$start = $start/1000;
$end = $end/1000;
$db = MySQL::get_instance();
//$rows = $db->get('ticker', array('exchange=' => $exchange, 'updated>' => $start/1000, 'updated<' => $end/1000));
$rows = $db->query("SELECT * FROM ticker WHERE exchange='{$exchange}' AND updated>{$start} AND updated<$end ORDER BY updated ASC");
//usort($rows, 'cmp');

$tickers = array();
foreach($rows as $row){
    $ticker = array();
    foreach($row  as $col => $val){
        if ($col == 'pair' || $col == 'exchange') continue;
        $ticker[$col] = $val;
    }
    $tickers[$row['pair']][] = $ticker;
}

header('Content-Type: application/json');
echo json_encode($tickers);