<?php

    require_once('../include/common.inc.php');
    
    $email = isset($_POST['email'])? $_POST['email'] : '';
    $email_data = Db::get_email($email);
    if (is_array($email_data)){
        $subject = $email_data[0]['subject'];
        $message = $email_data[0]['message'];
        $images = $email_data[0]['images'];
    }else{
        $subject = '';
        $message = '';
        $images = null;
    }

    echo "<p>Тема: $subject </p><p>Текст: $message</p>";
    if($images != null){
        $images = explode(',', $images);
        if (is_array($images) && count($images)){
            foreach($images as $image){
                $src = IMG_DIR . basename($image);
                echo "<img style='margin:10px;' src='{$src}'/>";
            }
        }
    }

?>
