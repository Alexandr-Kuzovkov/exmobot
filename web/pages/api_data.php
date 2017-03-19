<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 25.10.16
 * Time: 22:16
 */

$exchange = (isset($_GET['exchange']))? $_GET['exchange'] : null;
$method = (isset($_GET['method']))? $_GET['method'] : null;
$order_id = (isset($_GET['id']))? intval($_GET['id']) : null;
$session_id = (isset($_GET['session']))? $_GET['session'] : null;
$db = (isset($_GET['db']))? $_GET['db'] : null;

if ($exchange == null || $method == null){
    echo 'Bag parameters!'; exit();
}


$handler = array(
    'balance' => 'getBalanceTable',
    'user_orders' => 'getOrdersTable',
    'user_trades' => 'getTradesTable',
    'ticker' => 'getTickerTable',
    'order_cancel' => 'getOrdersTable',
    'cfm_fix_profit' => 'confirmFixProfit',
    'fix_profit' => 'fixProfit',

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
    global $order_id;
    if ($order_id != null){
        $res = json_decode(file_get_contents("{$_SERVER['HTTP_REFERER']}api?exchange={$exchange}&method=order_cancel&id={$order_id}"), true);
    }
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
    }else{
        echo 'Ордеров нет';
        return;
    }
    $table1[] = '<th>';
    $table1[] = '</tr>';
    if (is_array($orders) && count($orders)){
        foreach ($orders as $pair => $items){
            foreach($items as $row){
                $table1[] = '<tr>';
                foreach($row as $field => $val){
                    $table1[] = ($field == 'created')? "<td>".date('d.m.Y H:i:s', intval($val))."</td>" : "<td>{$val}</td>";
                }
                $table1[] = '<td class="red">' . "<span class='order-cancel pointer' title='Cancel' id='{$row['order_id']}'>Cancel</span></td>";
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

function getTickerTable($exchange){
    $ticker = json_decode(file_get_contents("{$_SERVER['HTTP_REFERER']}api?exchange={$exchange}&method=ticker"), true);
    $fields_name = array(
        'high'=>'максимальная цена сделки за 24 часа',
        'low'=>'минимальная цена сделки за 24 часа',
        'avg'=> 'средняя цена сделки за 24 часа',
        'vol' => 'объем всех сделок за 24 часа',
        'vol_curr' => 'сумма всех сделок за 24 часа',
        'last_trade' => 'цена последней сделки',
        'buy_price'=>'текущая максимальная цена покупки',
        'sell_price' => 'текущая минимальная цена продажи',
        'updated' => 'дата и время обновления данных',
    );
    $fee = ($exchange == 'poloniex')? 0.0015 : 0.002;
    $h1 = '<h3>Тикер</h3>';
    $table1 = array('<table class="table table-striped"');
    $table1[] = '<tr>';
    if (is_array($ticker) && count($ticker)){
        $table1[] = '<th>Пара</th>';
        foreach($fields_name as $field => $name){
            $table1[] = "<th>{$fields_name[$field]}</th>";
        }
        $table1[] = '<th>профитность</th>';
    }
    $table1[] = '</tr>';
    if (is_array($ticker) && count($ticker)){
        foreach ($ticker as $pair => $items){
            $table1[] = '<tr>';
            $table1[] = "<td>{$pair}</td>";
            foreach($fields_name as $field => $name){
                $table1[] = ($field == 'updated')? "<td>".date('d.m.Y H:i:s', intval($items[$field]))."</td>" : "<td>{$items[$field]}</td>";
            }
            $profit = $items['sell_price'] / $items['buy_price'] * (1-$fee) * (1-$fee) - 1;
            $table1[] = ($profit >= 0)? '<td class="green">' . $profit . "</td>" : '<td class="red">' . $profit . "</td>";
            $table1[] = '</tr>';

        }
    }

    $table1[] = '</table>';
    echo $h1, implode('', $table1);
}


function confirmFixProfit($exchange){
    global $db, $session_id;
    $start_balance = get_start_balance($db, $session_id, 'USD');
    $balance_full_usd = json_decode(file_get_contents("{$_SERVER['REQUEST_SCHEME']}://{$_SERVER['HTTP_HOST']}/api?exchange={$exchange}&method=possable_amount_usd"), true);
    if (is_array($start_balance) && count($start_balance)){
        $start_balance = $start_balance[0]['amount'];
        $profit_abs = $balance_full_usd - $start_balance;
        $profit_rel = ($balance_full_usd - $start_balance)/$start_balance * 100.0;
    }else{

    }

    $body = array(
        '<h3>Фиксация прибыли</h3>',
        '<p>Будет выполнено:</p>',
        '<ul>',
        '<li>останов торгов;</li>',
        '<li>отмена текущих ордеров;</li>',
        '<li>продажа всех криптовалют по рынку;</li>',
        '<li>очистка истории баланса;</li>',
        '</ul>',
        "<p>Начальный совокупный баланс: <b>{$start_balance}</b> USD</p>",
        "<p>Текущий совокупный баланс: <b>{$balance_full_usd}</b> USD</p>",
        "<p>Абсолютный профит: <b>{$profit_abs}</b> USD</p>",
        "<p>Относительный профит: <b>{$profit_rel}</b> %</p>",
        "<button id='{$exchange}-fix_profit~{$session_id}' class='fix-profit'>Зафиксировать</button>"
    );
    echo implode('', $body);
}


function fixProfit($exchange){
    global $session_id;
    $result = json_decode(file_get_contents("{$_SERVER['REQUEST_SCHEME']}://{$_SERVER['HTTP_HOST']}/api?exchange={$exchange}&method=fix_profit&session_id={$session_id}"), true);
    print_r($result);
}

function sortByDate($a,$b){
    return $a['date'] < $b['date'];
}