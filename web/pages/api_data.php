<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 25.10.16
 * Time: 22:16
 */

$exchange = (isset($_GET['exchange']))? $_GET['exchange'] : null;
$method = (isset($_GET['method']))? $_GET['method'] : null;

if ($exchange == null || $method == null){
    echo 'Bag parameters!'; exit();
}


$handler = array(
    'balance' => 'getBalanceTable',
    'user_orders' => 'getOrdersTable',
    'user_trades' => 'getTradesTable',

);

echo $handler[$method]($exchange);

/**
 * Возвращает HTML таблицу с данными
 * @param $exchange имя биржи
 */
function getBalanceTable($exchange){
    $balance = json_decode(file_get_contents("{$_SERVER['HTTP_REFERER']}api?exchange={$exchange}&method=balance"), true);
    $orders_balance = json_decode(file_get_contents("{$_SERVER['HTTP_REFERER']}api?exchange={$exchange}&method=orders_balance"), true);
    $balance_full_usd = json_decode(file_get_contents("{$_SERVER['HTTP_REFERER']}api?exchange={$exchange}&method=balance_full_usd"), true);
    $h1 = '<h3>Баланс</h3>';
    $table1 = array('<table class="table table-striped">');
    $table1[] = '<tr><th>Валюта</th><th>Сумма</th></tr>';

    foreach($balance as $currency => $amount){
        if ($amount == 0) continue;
        $table1[] = "<tr><td>{$currency}</td><td>{$amount}</td></tr>";
    }
    $table1[] = '</table>';

    $h2 = '<h3>Баланс в ордерах</h3>';
    $table2 = array('<table class="table table-striped"');
    $table2[] = '<tr><th>Валюта</th><th>Сумма</th></tr>';
    foreach($orders_balance as $currency => $amount){
        if ($amount == 0) continue;
        $table2[] = "<tr><td>{$currency}</td><td>{$amount}</td></tr>";
    }
    $table2[] = '</table>';

    $p = "<p>Эквивалентный баланс в USD: <b>{$balance_full_usd}</b></p>";

    echo $h1, implode('',$table1), $h2, implode('', $table2), $p;

}


/**
 * Возвращает HTML таблицу с данными
 * @param $exchange имя биржи
 */
function getOrdersTable($exchange){
    $orders = json_decode(file_get_contents("{$_SERVER['HTTP_REFERER']}api?exchange={$exchange}&method=user_orders"), true);
    $fields_name = array('created'=>'Создан', 'order_id'=>'Id', 'pair'=> 'Пара', 'price' => 'Цена', 'amount' => 'Сумма', 'quantity' => 'Количество', 'type'=>'Тип');
    $h1 = '<h3>Ордера</h3>';
    $table1 = array('<table class="table table-striped"');
    $table1[] = '<tr>';
    if (is_array($orders) && count($orders)){
        foreach ($orders as $pair => $items){
            foreach($items[0] as $field => $val){
                $table1[] = "<th>{$fields_name[$field]}</th>";
            }
            break;
        }
    }
    $table1[] = '</tr>';
    if (is_array($orders) && count($orders)){
        foreach ($orders as $pair => $items){
            foreach($items as $row){
                $table1[] = '<tr>';
                foreach($row as $field => $val){
                    $table1[] = ($field == 'created')? "<td>".date('d.m.Y H:i:s', intval($val))."</td>" : "<td>{$val}</td>";
                }
                $table1[] = '</tr>';
            }
        }
    }

    $table1[] = '</table>';
    echo $h1, implode('', $table1);
}


/**
 * Возвращает HTML таблицу с данными
 * @param $exchange имя биржи
 */
function getTradesTable($exchange){
    $trades = json_decode(file_get_contents("{$_SERVER['HTTP_REFERER']}api?exchange={$exchange}&method=user_trades"), true);
    $fields_name = array('date'=>'Дата и время', 'order_id'=>'Order Id', 'pair'=> 'Пара', 'price' => 'Цена', 'amount' => 'Сумма', 'quantity' => 'Количество', 'type'=>'Тип', 'trade_id'=>'Trade Id');
    $h1 = '<h3>История торгов</h3>';
    $table1 = array('<table class="table table-striped"');
    $table1[] = '<tr>';
    if (is_array($trades) && count($trades)){
        foreach ($trades as $pair => $items){
            if (!count($items)) continue;
            foreach($items[0] as $field => $val){
                $table1[] = "<th>{$fields_name[$field]}</th>";
            }
            break;
        }
    }
    $table1[] = '</tr>';
    $rows = array();
    if (is_array($trades) && count($trades)){
        foreach ($trades as $pair => $items){
            foreach($items as $row)
                $rows[] = $row;
        }
    }

    usort($rows, 'sortByDate');

    foreach($rows as $row){
        $table1[] = '<tr>';
        foreach($row as $field => $val){
            $table1[] = ($field == 'date')? "<td>".date('d.m.Y H:i:s', intval($val))."</td>" : "<td>{$val}</td>";
        }
        $table1[] = '</tr>';
    }
    $table1[] = '</table>';
    echo $h1, implode('', $table1);
}

function sortByDate($a,$b){
    return $a['date'] < $b['date'];
}