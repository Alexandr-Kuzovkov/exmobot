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
$data = get_balances_data($fullname);
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
                        <td> <?php echo ($prev_amount != 0)? ($item['amount'] - $prev_amount)/$prev_amount * 100.0 : '-';?> </td>
                        <td> <?php echo ($first_amount != 0)? ($item['amount'] - $first_amount)/$first_amount * 100.0 : '-';?> </td>
                        <?php $prev_amount = $item['amount']?>
                    </tr>
                <?php endforeach;?>
                </table>
            <?php endforeach;?>
                &nbsp;</td>
        <?php endforeach;?>
    </tr>
</table>