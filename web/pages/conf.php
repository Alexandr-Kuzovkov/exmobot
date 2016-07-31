<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php
/**авторизация**/
if (!Auth::isAuth()) { echo '<label>Требуется авторизация!</label>'; exit();}
/**авторизация**/
?>

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
        <div id="conf" class="scroll2" contenteditable="true"><?php echo $content; ?></div>
        <input type="hidden" name="file" value="<?php echo $fullname;?>">
        <input type="hidden" id="conf-content" name="conf_content">
        <button>Сохранить</button>
    </form>

    <script type="text/javascript">
        function save_content(){
            $('#conf-content').val($('#conf').html());
        }
    </script>


<?php require_once('_footer.php')?>