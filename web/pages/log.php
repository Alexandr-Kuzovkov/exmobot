<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>

<?php
    $filename = isset($_GET['file'])? $_GET['file'] : '';
?>
    <h3>Лог файл <span class="filename"><?php echo $filename; ?></span> </h3>
    <div  id="log" class="black-field scroll"><img src="/img/preload.gif"/></div>
    <script type="text/javascript">

        function update_log(){
            $('#log').load('/get-log?file=<?php echo $filename;?>');
        }

        var interval =setInterval(update_log, 2000);
    </script>

<?php require_once('_footer.php')?>