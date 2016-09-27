<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php require_once('_auth.php')?>

<?php
    $direction = (isset($_GET['db']))? $_GET['db'] : '';
    $sqlite_db = get_database_file();
    $mysql_db = DB_NAME;
?>
<div class="left">
    <h3>Копирование базы данных</h3>
    <?php if ($direction == 'sqlite_mysql'):?>
        <p>Копирование данных из базы sqlite  <span class="filename"><?php echo $sqlite_db;?></span> в базу mysql <span class="filename"><?php echo $mysql_db;?></span></p>
        <p>Все данные в базе  mysql <span class="filename"><?php echo $mysql_db;?></span> будут потеряны!</p>
    <?php elseif ($direction = 'mysql_sqlite'):?>
        <p>Копирование данных из базы mysql  <span class="filename"><?php echo $mysql_db;?></span> в базу sqlite <span class="filename"><?php echo $sqlite_db;?></span></p>
        <p>Все данные в базе  sqlite <span class="filename"><?php echo $sqlite_db;?></span> будут потеряны!</p>
    <?php else:?>
        <p>Не задано направление копирования!</p>
    <?php endif;?>
    <button id="copy_btn">Копировать</button>
</div>
<div id="copy_result"></div>
<script type="text/javascript">

    $('#copy_btn').click(function(){
        $('#copy_result').html('<img src="/img/preload.gif"/>');
        $.post('/copy-data', {'direction': '<?php echo $direction;?>'}, function(data){
            $('#copy_result').html(data);
        });
    });
</script>

<?php require_once('_footer.php')?>