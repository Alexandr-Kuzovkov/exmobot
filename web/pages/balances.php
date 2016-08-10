<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php require_once('_auth.php')?>


    <h3>Статистика по балансам</h3>
    <pre  id="db" class="db scroll2"><img src="/img/preload.gif"/></pre>
    <script type="text/javascript">

        function update_data(){
            $('#db').load('/get-balances');
        }
        var interval =setInterval(update_data, 2000);
    </script>

<?php require_once('_footer.php')?>