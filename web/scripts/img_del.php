<?php

    require_once ('../include/const.php');

    foreach($_POST as $name => $val){
        $name = trim(str_replace('_','.',$name));
        $fullname = $_SERVER['DOCUMENT_ROOT'] . '/' . IMG_DIR . $name;

        echo $fullname;
        if (file_exists($fullname)) unlink($fullname);
    }

    header('Location: /images');