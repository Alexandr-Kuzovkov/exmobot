<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 22.05.16
 * Time: 21:18
 */

$pages = 'pages/';
$scripts = 'scripts/';
$root_dir = ''; /*если скрипт не в корневом каталоге сервера*/

$routes = array(
    '/' => $pages . 'index.php',
    '/login' => $pages . 'login.php',
    '/auth' => $scripts . 'auth.php',
    '/log' => $pages . 'log.php',
    '404' => $pages . '404.php',
    '/get-log' => $scripts . 'get_log.php',
    '/conf' => $pages . 'conf.php',
    '/save-conf' => $scripts . 'save_conf.php',
    '/add-conf' => $pages . 'add_conf.php',
    '/save-new-conf' => $scripts . 'save_conf.php',
    '/del-conf' => $scripts . 'del_conf.php',
    '/help' => $pages . 'help.php',
    '/strategy' => $pages . 'strategy.php',
    '/hard' => $pages . 'hard.php',
    '/get_hard_info' => $scripts . 'get_hard_info.php',
    '/database' => $pages . 'database.php',
    '/get-data' => $scripts . 'get_data.php',
    '/query' => $pages . 'query.php',
    '/exec-query' => $scripts . 'exec_query.php',
    '/balances' => $pages . 'balances.php',
    '/trades' => $pages . 'trades.php',
    '/get-balances' => $scripts . 'get_balances2.php',
    '/get-trades' => $scripts . 'get_trades2.php',
    '/copy' => $pages . 'copy.php',
    '/copy-data' => $scripts . 'copy_data.php',
    '/backup' => $scripts . 'backup.php',
    '/upload' => $pages . 'upload.php',
    '/upload-dump' => $scripts . 'upload_dump.php',
    '/api-data' => $pages . 'api_data.php'

    /*
    '/file' => $pages . 'file.php',


    '/settings' => $pages . 'settings.php',

    '/upload' => $scripts . 'upload.php',
    '/get_email_data' => $scripts . 'get_email_data.php',
    '/del-all' => array($scripts . 'action.php',array('action' => 'del-all')),
    '/mark-as-nosend' => array($scripts . 'action.php',array('action' => 'mark-as-nosend')),
    '/mark-as-send' => array($scripts . 'action.php',array('action' => 'mark-as-send')),
    '/del-sended' => array($scripts . 'action.php',array('action' => 'del-sended')),
    '/set-data' => $pages . '/email_form.php',
    '/sended' => array($pages . 'index.php', array('type'=>'sended')),
    '/nosended' => array($pages . 'index.php', array('type'=>'nosended')),
    '/reset-db' => array($scripts . 'action.php', array('action' => 'reset-db')),
    '/get-list-emails' => $pages . 'list_data.php',
    '/send-email' => array($scripts . 'action.php', array('action' => 'send-email')),
    '/images' => $pages . 'img.php',
    '/img-upload' => $scripts . 'img_upload.php',
    '/del-images' => $scripts . 'img_del.php',
    '/save-data' => $scripts . 'save_data.php'
    */
);



if (isset($_SERVER['REQUEST_URI'])){

    $real_uri = $_SERVER['REQUEST_URI'];

    if (($p = strpos($real_uri, '?')) === false){
        $uri = substr($real_uri, 0);
    }else{
        $uri = substr($real_uri, 0, strpos($real_uri, '?') );
    }


    /*учет случая когда скрипт не в корневом каталоге сервера*/
    if (strlen($root_dir) && strpos($uri, $root_dir) === 0){
        $uri = substr($uri, strlen($root_dir));
    }

    if (isset($routes[$uri])){
        if(is_array($routes[$uri])){
            if (isset($routes[$uri][1]) && is_array($routes[$uri][1]))
                    foreach($routes[$uri][1] as $key => $val)
                        $_GET[$key] = $val;
            $require = '../' . $routes[$uri][0];
        }else{
            $require = '../' . $routes[$uri];
        }

    }else{
        $require = '../' . $routes['404'];
    }

    require_once ($require);

}else{
    echo 'Access not allow';
}