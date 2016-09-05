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
<link rel="stylesheet" type="text/css" href="vendor/datatables/jquery.dataTables.css">
<table class="table">
    <tr>
        <?php foreach($data as $session_id => $session_data): ?>
            <td>&nbsp;
                <h3> Сессия: <?php echo $session_id;?> </h3>
                <?php foreach ($session_data as $currency => $items):?>
                    <?php $first_amount = (count($items))? $items[0]['amount'] : 1; $prev_amount = $first_amount;?>
                    <table class="table-bordered" id="<?php echo $session_id.$currency;?>">
                        <thead>
                        <tr><th colspan="5"><h4> Валюта: <?php echo $currency;?></h4></th></tr>
                        <tr><td> Дата </td><td> Сумма </td><td>Профит(%)</td><td>Итого(%)</td><th>Количество за дату</th>
                        </tr></thead>
                        <?php $prev_date = date('d.m.Y', time()); $count_date = 0; foreach($items as $item):?>
                            <?php
                            $curr_date = date('d.m.Y', $item['utime']);
                            $curr_datetime = date('d.m.Y H:i:s', $item['utime']);
                            if ($curr_date == $prev_date){ $count_date++; $itog = '-';} else{
                                $itog =  "Итого за $prev_date: $count_date";
                                $count_date = 1; $prev_date = $curr_date;
                            } ?>
                            <tr>
                                <td> <?php echo $curr_datetime;?> </td>
                                <td> <?php echo $item['amount'];?> </td>
                                <td> <?php if ($prev_amount != 0) printf('%.4f',($item['amount'] - $prev_amount)/$prev_amount * 100.0); else echo '-';?> </td>
                                <td> <?php if ($first_amount != 0) printf('%.4f',($item['amount'] - $first_amount)/$first_amount * 100.0); else echo '-';?> </td>
                                <td> <?php echo $itog;?> </td>
                                <?php $prev_amount = $item['amount']?>

                            </tr>
                        <?php endforeach;?>
                    </table>
                <?php endforeach;?>
                &nbsp;</td>
        <?php endforeach;?>
    </tr>
</table>

<script type="text/javascript" charset="utf8" src="vendor/datatables/jquery.dataTables.min.js"></script>
<script>
    <?php foreach($data as $session_id => $session_data): ?>
    <?php foreach ($session_data as $currency => $items):?>
    $("#<?php echo $session_id.$currency;?>").dataTable({"aoColumnDefs":[
        {
            "aTargets": [ 1,2,3,4 ],
            "bSortable": false
        },
        {
            "aTargets":[ 0 ],
            "sType": "date"

        }]});
    <?php endforeach;?>
    <?php endforeach;?>
</script>