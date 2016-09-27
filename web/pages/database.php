<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php require_once('_auth.php')?>

<?php
$path = '../../db/';
$db = (isset($_GET['db']))? $_GET['db'] : 'sqlite';
if($db == 'sqlite'){
    $file = get_database_file();
}else{
    $file = DB_NAME;
}


?>
    <h3>База данных <span class="filename"><?php echo $file; ?></span> </h3>
    <pre  id="db" class="db scroll2"><img src="/img/preload.gif"/></pre>
    <script type="text/javascript">

        function update_data(){
            $('#db').load('/get-data?db=<?php echo $db;?>');
        }
        //var interval =setInterval(update_data, 2000);
        update_data();

    </script>

<?php require_once('_footer.php')?>