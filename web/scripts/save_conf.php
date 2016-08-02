<?php
/**
 * Created by PhpStorm.
 * User: user1
 * Date: 31.07.16
 * Time: 16:14
 */

    $content = isset($_POST['conf_content'])? $_POST['conf_content'] : false;

    if (!isset($_POST['new_conf'])){
        $fullname = isset($_POST['file'])? $_POST['file'] : false;
        if ($content !== false && $fullname !== false && file_exists($fullname)){
            try{
                file_put_contents($fullname, prepContent($content));
            } catch (Exceptorn $e){
                echo $e->getMessage();
                echo '<p><a href="/conf?file=' . basename($fullname) . '">Назад</a></p>';
                exit();
            }
        }

        $header = 'Location: /conf?file=' . basename($fullname);
        header($header);
        exit();
    }else{
        $filename = isset($_POST['file'])? $_POST['file'] : false;

        if ($content !== false && $filename !== false){
            $path = '../../conf/';
            $fullname = $path . $filename;

            try{
                file_put_contents($fullname, prepContent($content));
            } catch (Exceptorn $e){
                echo $e->getMessage();
                echo '<p><a href="/conf?file=' . basename($fullname) . '">Назад</a></p>';
                exit();
            }
        }
        $fullname = realpath($fullname);
        chmod($fullname, 0666);
        $header = 'Location: /conf?file=' . basename($fullname);
        header($header);
        exit();
    }




    /**
    * @param $str
    * @return mixed
    */
    function prepContent($str){
        $template = array(
            "<br/>" => "\n",
            "<br>" => "\n",
            "<div>" => "\n",
            "</div>" => "\n"
        );

        foreach ($template as $key => $val) {
            $str = str_replace($key, $val, $str);
        }

        return $str;
    }

?>