<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php require_once('_auth.php')?>

<?php

/**
 * @param $str
 * @return mixed
 */
function prepResult($str){
    $template = array(
        "#033[" => " ",
        "#015" => " ",
        "0m" => " ",
        "30m" => "",
        "32m" => "",
        "35m" => "",
        "34m" => "",
        "96m" => "",
        "94m" => "",
        "91m" => "",
        "\n" => "<br/>"

    );

    foreach ($template as $key => $val) {
        $str = str_replace($key, $val, $str);
    }

    return $str;
}

?>
    <form method="post" action="/save-new-conf" onsubmit="save_content()">
    <h3>Создать файл конфигурации <input name="file" value="default.conf"></h3>

        <div id="conf" class="scroll2" contenteditable="true"></div>
        <input type="hidden" name="new_conf" value="1">
        <input type="hidden" id="conf-content" name="conf_content">
        <button>Сохранить</button>
    </form>

    <script type="text/javascript">
        function save_content(){
            $('#conf-content').val($('#conf').html());
        }
    </script>


<?php require_once('_footer.php')?>