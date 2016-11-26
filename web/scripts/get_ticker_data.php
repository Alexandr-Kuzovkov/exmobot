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

$db = MySQL::get_instance();
$rows = $db->get('ticker', array('exchange=' => $exchange, 'updated>' => $start/1000, 'updated<' => $end/1000));

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