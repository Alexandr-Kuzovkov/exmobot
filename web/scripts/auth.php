<?php
if(session_status() !== PHP_SESSION_ACTIVE ) session_start();
require_once('../include/common.inc.php');

if (!Auth::isAuth()){
    $login = (isset($_POST['login']))? $_POST['login']:'user';
    $pass = (isset($_POST['pass']))? $_POST['pass']:'pass';
    Auth::login($login,$pass);

}else{
    Auth::logout();
}

if (Auth::isAuth()){
    header('Location: /');
}else{
    header('Location: /login');
}

?>
	