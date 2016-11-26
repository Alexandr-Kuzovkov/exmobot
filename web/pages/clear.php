<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>

<?php
$direction = (isset($_GET['db']))? $_GET['db'] : '';
$sqlite_db = get_database_file();
$mysql_db = DB_NAME;
?>
    <div class="left">
        <h3>Пересоздание базы данных</h3>
        <?php if ($direction == 'sqlite'):?>
            <p>Пересоздание базы sqlite  <span class="filename"><?php echo $sqlite_db;?></p>
            <p>Все данные в базе  sqlite <span class="filename"><?php echo $sqlite_db;?></span> будут уничтожены!</p>
        <?php elseif ($direction = 'mysql'):?>
            <p>Пересоздание базы mysql  <span class="filename"><?php echo $mysql_db;?></span></p>
            <p>Все данные в базе  mysql <span class="filename"><?php echo $mysql_db;?></span> будут уничтожены!</p>
        <?php else:?>
            <p>Не задан тип базы данных</p>
        <?php endif;?>
        <form method="post" action="/clear-db?db=<?php echo $direction;?>" enctype="multipart/form-data">
            <button> Пересоздать </button>
        </form>
    </div>


<?php require_once('_footer.php')?>