<?php

    require_once('../include/common.inc.php');
    
    $file_field = 'img';

    //print_r($_FILES); exit();
    if (isset($_FILES[$file_field])){
        $files = $_FILES[$file_field];
        if (isset($files['error'])){
            foreach($files['error'] as $index => $error){
                if ($error == 0){
                    if (strpos($files['type'][$index], 'image') === 0){
                        $tmp_name = $files['tmp_name'][$index];
                        $name = $files['name'][$index];
                        move_uploaded_file($tmp_name, $_SERVER['DOCUMENT_ROOT'] . '/' . IMG_DIR . $name);
                    }
                }
            }

        }
    }
    
    header('Location: /images');