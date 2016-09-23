<?php
    require_once('../include/common.inc.php');

    if ($_SERVER['REQUEST_METHOD'] == 'POST'){
        require_once ('../include/Db.class.php');
        //print_r($_POST); exit();
        $subject = isset($_POST['subject'])? $_POST['subject'] : '';
        $message = isset($_POST['message'])? $_POST['message'] : '';
        $images = array();
        foreach($_POST as $name => $val){
            if (strpos($name, 'attacment:') === 0){
                $name = trim(str_replace('attacment:','',$name));
                $name = str_replace('_','.',$name);
                $fullname = $_SERVER['DOCUMENT_ROOT'] . '/' . IMG_DIR . $name;
                $images[] = $fullname;
            }
        }

        if (isset($_POST['onlysended'])){
            Db::set_nosended_email_param($subject, $message, $images);
        }else{
            Db::set_email_param($subject, $message, $images);
        }

        header('Location: /');
        exit();
    }
?>
