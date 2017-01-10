<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>


<?php
$direction = (isset($_GET['db']))? $_GET['db'] : '';
$sqlite_db = get_database_file();
$mysql_db = DB_NAME;
?>
    <div class="left">
        <h3>Заливка базы данных</h3>
        <?php if ($direction == 'sqlite'):?>
            <p>Заливка базы sqlite  <span class="filename"><?php echo $sqlite_db;?></p>
            <p>Все прежние данные в базе  sqlite <span class="filename"><?php echo $sqlite_db;?></span> будут потеряны!</p>
        <?php elseif ($direction = 'mysql'):?>
            <p>Заливка дампа базы mysql в базу <span class="filename"><?php echo $mysql_db;?></span></p>
            <p>Все прежние данные в базе  mysql <span class="filename"><?php echo $mysql_db;?></span> будут потеряны!</p>
        <?php else:?>
            <p>Не задан тип базы данных</p>
        <?php endif;?>
        <form method="post" action="/upload-dump?db=<?php echo $direction;?>" enctype="multipart/form-data">
        <input type="file" name="dump" required="required"/><br/>
        <button> Загрузить </button>
        </form>
    </div>


<?php require_once('_footer.php')?>