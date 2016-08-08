<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php require_once('_auth.php')?>

<?php
$path = '../../db/';
$file = get_database_file();

?>
    <h3>Результаты запроса к базе <span class="filename"><?php echo $file; ?></span> </h3>
    <pre  id="db" class="db scroll2"><img src="/img/preload.gif"/></pre>
    <pre id="query" class="query" contenteditable="true"></pre>
    <button id="run-query">Выполнить</button>
    <button id="run-reset" class="red-btn">Сброс</button>

    <script type="text/javascript">
        $('#db').load('/get-data');

        $('#run-query').click(function(){
            $('#db').load('/exec-query', {query:$('#query').text()});
        });

        $('#run-reset').click(function(){
            $('#db').load('/get-data');
        });
    </script>

<?php require_once('_footer.php')?>