<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 22.05.16
 * Time: 22:17
 */
    require_once('../include/common.inc.php');

    $file_field = 'file';
    if (isset($_FILES[$file_field])){
        $files = $_FILES[$file_field];
        if (isset($files['error']) && $files['error'] == 0){
            $tmp_name = $files['tmp_name'];
            Db::insert_emails_from_file($tmp_name);
        }
    }

    header('Location: /file');


