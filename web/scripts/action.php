<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 24.05.16
 * Time: 12:46
 */

    require_once ('../include/common.inc.php');

    $redirect = array(
        'default' => '/',
        'del-all' => '/',
        'mark-as-nosend' => '/',
        'mark-as-send' => '/',
        'del-sended' => '/',
        'reset-db' => '/settings',

    );

    if(!isset($_GET['action'])){
        $uri = $redirect['default'];
    }else{
        $action = $_GET['action'];
        switch ($action){
            case 'del-all': del_all(); break;
            case 'mark-as-nosend': mark_as_nosend(); break;
            case 'mark-as-send': mark_as_send(); break;
            case 'del-sended': del_sended(); break;
            case 'reset-db': reset_db(); break;
            case 'send-email': send_email(); exit(); break;
        }
        $uri = (isset($redirect[$action]))? $redirect[$action] : $redirect['default'];
    }

    header('Location: ' . $uri);
    exit();

    