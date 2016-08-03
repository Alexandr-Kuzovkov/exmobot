<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php require_once('_auth.php')?>

<?php
$filename = isset($_GET['file'])? $_GET['file'] : '';
$path = '../../conf/';
$fullname = realpath($path . $filename);
$content = prepResult(file_get_contents($fullname));

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
    <h3>Файл конфигурации <span class="filename"><?php echo $filename; ?></span></h3>
    <form method="post" action="/save-conf" onsubmit="save_content()">
        <div id="conf" class="black-field scroll2" contenteditable="true"><?php echo $content; ?></div>
        <input type="hidden" name="file" value="<?php echo $fullname;?>">
        <input type="hidden" id="conf-content" name="conf_content">
        <button>Сохранить</button>
    </form>
<p></p>
    <form method="post" action="/del-conf" onsubmit="return confirm_del();">
        <input type="hidden" value="<?php echo $fullname;?>" name="file">
        <button class="red-btn">Удалить</button>
    </form>

    <script type="text/javascript">
        function save_content(){
            $('#conf-content').val($('#conf').html());
        }

        function confirm_del(){
            return confirm("Удалить файл?");
        }
    </script>


<?php require_once('_footer.php')?>