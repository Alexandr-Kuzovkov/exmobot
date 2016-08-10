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
$data = get_trades_data($fullname);
//print_r($data);
//exit();

?>

<table class="table">
    <?php foreach($data as $session_id => $session_data): ?>
    <tr>
            <td>&nbsp;
                <h3> Сессия: <?php echo $session_id;?> </h3>
                <?php foreach ($session_data as $pair => $items):?>
                    <table class="table-bordered stat-table">
                        <tr><th colspan="<?php echo count($items);?>"><h4> Пара: <?php echo $pair;?></h4></th></tr>
                        <tr>
                        <?php if (isset($items[0])): foreach ($items[0] as $key => $val): if ($key == 'pair' || $key == 'utime') continue; ?>
                            <th> <?php echo $key; ?> </th>
                        <?php endforeach; endif;?>
                        </tr>
                        <?php foreach($items as $item):?>
                            <tr>
                                <?php foreach($item as $key => $val):?>
                                    <?php if ($key == 'pair' || $key == 'utime') continue; ?>
                                    <td><?php echo ($key == 'trade_date')? date('d.m.Y H:i:s', $val) : $val;?></td>
                                <?php endforeach;?>
                            </tr>
                        <?php endforeach;?>
                    </table>
                <?php endforeach;?>
                &nbsp;</td>
    </tr>
    <?php endforeach;?>
</table>