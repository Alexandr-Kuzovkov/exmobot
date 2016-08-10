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
                <table class="table-bordered">
                <tr><th colspan="2"><h4> Валюта: <?php echo $currency;?></h4></th></tr>
                    <tr><td> Дата </td><td> Сумма </td></tr>
                <?php foreach($items as $item):?>
                    <tr>
                        <td> <?php echo date('d.m.Y H:i:s', $item['utime']);?> </td>
                        <td> <?php echo $item['amount'];?> </td>
                    </tr>
                <?php endforeach;?>
                </table>
            <?php endforeach;?>
                &nbsp;</td>
        <?php endforeach;?>
    </tr>
</table>