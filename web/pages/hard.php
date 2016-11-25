<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>



    <h3>Датчики</h3>
    <pre class="hard-info scroll" id="cpu-temp"><img src="/img/preload.gif"/></pre>

    <h3>Память</h3>
    <pre class="hard-info scroll" id="mem"><img src="/img/preload.gif"/></pre>

    <h3>Диск</h3>
    <pre class="hard-info scroll" id="hdd"><img src="/img/preload.gif"/></pre>

    <script type="text/javascript">
        function update_info(){
            $('#cpu-temp').load('/get_hard_info?item=cpu');
            $('#mem').load('/get_hard_info?item=mem');
            $('#hdd').load('/get_hard_info?item=hdd');
        }
        var interval = setInterval(update_info, 2000);
    </script>

<?php require_once('_footer.php')?>