<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>

<?php
$path = '../../db/';
$db = (isset($_GET['db']))? $_GET['db'] : 'sqlite';
if($db == 'sqlite'){
    $file = get_database_file();
}else{
    $file = DB_NAME;
}
?>
    <h3>Результаты запроса к базе <span class="filename"><?php echo $file; ?></span> </h3>
    <pre  id="db" class="db scroll2"><img src="/img/preload.gif"/></pre>
    <pre id="query" class="query" contenteditable="true"></pre>
    <button id="run-query">Выполнить</button>
    <button id="run-reset" class="red-btn">Сброс</button>

    <script type="text/javascript">
        $('#db').load('/get-data?db=<?php echo $db;?>');

        $('#run-query').click(function(){
            $('#db').html('<img src="/img/preload.gif"/>');
            $('#db').load('/exec-query?db=<?php echo $db;?>', {query:$('#query').text()});
        });

        $('#run-reset').click(function(){
            $('#db').html('<img src="/img/preload.gif"/>');
            $('#db').load('/get-data?db=<?php echo $db;?>');
        });
    </script>

<?php require_once('_footer.php')?>