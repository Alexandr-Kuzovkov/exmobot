<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 31.07.16
 * Time: 13:52
 */

$filename = $_GET['file'];
$path = '../../log/';
$fullname = realpath($path . $filename);

if (file_exists($fullname)){
    $command = "tail -100 $fullname";
    ob_start();
    passthru($command);
    $res = ob_get_clean();
    echo prepResult($res);
}else{
    echo "file not found: $filename";
}

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


