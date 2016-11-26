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
    $data = get_database_data_sqlite($fullname,null, 1000);
}elseif($db == 'mysql'){
    $data = get_database_data_mysql(null, 1000);
}
?>
<link rel="stylesheet" type="text/css" href="vendor/datatables/jquery.dataTables.css">
<?php foreach ($data as $table => $rows):?>
    <h3><?php echo $table;?></h3>
    <table class="table" id="<?php echo $table;?>">
        <thead>
        <tr>
        <?php if(isset($rows[0])): foreach ($rows[0] as $col=> $val):?>
            <th><?php echo $col;?></th>
        <?php endforeach; endif;?>
        </tr>
        </thead>
        <?php foreach($rows as $row):?>
            <tr>
                <?php foreach ($row as $key=>$val):?>
                    <td><?php echo ($key == 'utime' || $key == 'trade_date')? date('d.m.Y H:i:s', $val) : $val?></td>
                <?php endforeach;?>
            </tr>
        <?php endforeach;?>
    </table>

<?php endforeach;?>

<script type="text/javascript" charset="utf8" src="vendor/datatables/jquery.dataTables.min.js"></script>
<script>
   <?php foreach ($data as $table => $rows):if (count($rows)):?>
        $("#<?php echo $table;?>").dataTable();
    <?php endif; endforeach;?>
</script>
