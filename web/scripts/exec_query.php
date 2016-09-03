<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 08.08.16
 * Time: 15:09
 */

require_once ('../include/functions.php');

$path = '../../db/';
$file = get_database_file();
$fullname = realpath($path . $file);
$query = (isset($_POST['query']))? $_POST['query'] : '';
echo $query;
$db = (isset($_GET['db']))? $_GET['db'] : 'sqlite';
if ($db == 'sqlite'){
    $data = exec_query_sqlite($fullname, $query);
}elseif($db == 'mysql'){
    $data = exec_query_mysql($query);
}
?>


    <table class="table">
         <tr>
            <?php if(isset($data[0])): foreach ($data[0] as $col=> $val):?>
                <th><?php echo $col;?></th>
            <?php endforeach; endif;?>
        </tr>
        <?php foreach($data as $row):?>
            <tr>
                <?php foreach ($row as $key=>$val):?>
                    <td><?php echo ($key == 'utime' || $key == 'trade_date')? date('d.m.Y H:i:s', $val) : $val?></td>
                <?php endforeach;?>
            </tr>
        <?php endforeach;?>
    </table>
