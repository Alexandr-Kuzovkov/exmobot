<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 01.08.16
 * Time: 0:08
 */

$fullname = isset($_POST['file'])? $_POST['file'] : false;

if ($fullname !== false && file_exists($fullname)){
    try{
        unlink($fullname);
    } catch(Exception $e){
        print $e->getMessage();
        exit();
    }
}

header('Location: /');


















