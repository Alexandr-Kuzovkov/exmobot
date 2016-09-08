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
    $analize = analize_user_trades_sqlite($fullname);
}elseif($db == 'mysql'){
    $data = get_trades_data_mysql();
    $analize = analize_user_trades_mysql();
}
//print_r($data);
//exit();

?>
<link rel="stylesheet" type="text/css" href="vendor/datatables/jquery.dataTables.css">
<table class="table">
    <?php foreach($data as $session_id => $session_data): ?>
        <tr>
            <td>&nbsp;
                <h3> Сессия: <?php echo $session_id;?> </h3>
                <?php foreach ($session_data as $pair => $items):?>
                    <table class="table-bordered stat-table" id="<?php echo $session_id.$pair;?>">
                        <thead>
                        <tr><th colspan="<?php echo count($items)+1;?>"><h4> Пара: <?php echo $pair;?></h4></th></tr>
                        <tr>
                            <?php if (isset($items[0])): foreach ($items[0] as $key => $val): if ($key == 'pair' || $key == 'utime' || $key == 'session_id') continue; ?>
                                <th> <?php echo $key; ?> </th>
                            <?php endforeach; endif;?>
                            <th>Количество за дату</th>
                        </tr>
                        </thead>
                        <?php  $prev_date = date('d.m.Y', time()); $count_date = 0; foreach($items as $item):?>
                            <?php
                            $curr_date = date('d.m.Y', $item['trade_date']);
                            if ($curr_date == $prev_date){ $count_date++; $itog = '-';} else{
                                $itog =  "Итого за $prev_date: $count_date";
                                $count_date = 1; $prev_date = $curr_date;
                            } ?>
                            <tr>
                                <?php foreach($item as $key => $val):?>
                                    <?php if ($key == 'pair' || $key == 'utime' || $key == 'session_id') continue; ?>
                                    <td><?php echo ($key == 'trade_date')? date('d.m.Y H:i:s', $val) : $val;?></td>
                                <?php endforeach;?>
                                <td> <?php echo $itog;?> </td>
                            </tr>
                        <?php endforeach;?>
                    </table>
                    <?php foreach($analize[$session_id][$pair] as $key => $val):?>
                        <b><?php echo $key?></b> = <i><?php echo $val;?></i>; &nbsp;
                    <?php endforeach;?>
                <?php endforeach;?>
                &nbsp;</td>
        </tr>
    <?php endforeach;?>
</table>

<script type="text/javascript" charset="utf8" src="vendor/datatables/jquery.dataTables.min.js"></script>
<script>
    <?php foreach($data as $session_id => $session_data): ?>
        <?php foreach ($session_data as $pair => $items):?>
            $("#<?php echo $session_id.$pair;?>").dataTable({"aoColumnDefs":[
            {
				"aTargets": [ 1,2,3,4,5,7 ],
			   "bSortable": false
		    },{
				"aTargets":[ 6 ]
			  , "sType": "date"

		  }]});
        <?php endforeach;?>
    <?php endforeach;?>
</script>
