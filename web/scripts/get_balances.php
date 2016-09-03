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
    $data = get_balances_data_sqlite($fullname);
}elseif($db == 'mysql'){
    $data = get_balances_data_mysql();
}
//print_r($data);
//exit();

?>

<table class="table">
    <tr>
        <?php foreach($data as $session_id => $session_data): ?>
            <td>&nbsp;
            <h3> Сессия: <?php echo $session_id;?> </h3>
            <?php foreach ($session_data as $currency => $items):?>
                <?php $first_amount = (count($items))? $items[0]['amount'] : 1; $prev_amount = $first_amount;?>
                <table class="table-bordered">
                <tr><th colspan="4"><h4> Валюта: <?php echo $currency;?></h4></th></tr>
                    <tr><td> Дата </td><td> Сумма </td><td>Профит(%)</td><td>Итого(%)</td></tr>
                <?php foreach($items as $item):?>
                    <tr>
                        <td> <?php echo date('d.m.Y H:i:s', $item['utime']);?> </td>
                        <td> <?php echo $item['amount'];?> </td>
                        <td> <?php if ($prev_amount != 0) printf('%.4f',($item['amount'] - $prev_amount)/$prev_amount * 100.0); else echo '-';?> </td>
                        <td> <?php if ($first_amount != 0) printf('%.4f',($item['amount'] - $first_amount)/$first_amount * 100.0); else echo '-';?> </td>
                        <?php $prev_amount = $item['amount']?>
                    </tr>
                <?php endforeach;?>
                </table>
            <?php endforeach;?>
                &nbsp;</td>
        <?php endforeach;?>
    </tr>
</table>