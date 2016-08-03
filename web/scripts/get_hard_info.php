<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 31.07.16
 * Time: 13:52
 */

$item = isset($_GET['item'])? $_GET['item'] : false;


if ($item){
    if ($item === 'cpu'){
        $command = "sensors";
    }elseif ($item === 'mem'){
        $command = "free";
    }elseif($item === 'hdd'){
        $command = "df -m";
    }else{
        echo "Error: item not valid!";
        return;
    }

    ob_start();
    passthru($command);
    $res = ob_get_clean();
    echo $res;
}else{
    echo "Error: item not present!";
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
