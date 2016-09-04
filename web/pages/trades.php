<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php require_once('_auth.php')?>
<link rel="stylesheet" type="text/css" href="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css">

<?php
    $db = (isset($_GET['db']))? $_GET['db'] : 'sqlite';
    if($db == 'sqlite'){
        $file = get_database_file();
    }else{
        $file = DB_NAME;
    }

?>

    <h3>Статистика по сделкам <span class="filename"><?php echo $file;?></span></h3>
    <pre  id="db" class="db scroll2"><img src="/img/preload.gif"/></pre>
    <!--<script type="text/javascript" charset="utf8" src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js"></script>-->
    <script type="text/javascript" charset="utf8" src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js"></script>
    <script type="text/javascript">

        function update_data() {
            $('#db').load('/get-trades?db=<?php echo $db;?>', {}, function (data) {
            });
        }
        update_data();
        //var interval =setInterval(update_data, 10000);
    </script>

<?php require_once('_footer.php')?>

