<?php

    $file = (isset($_GET['file']))?  $_GET['file'] : false;
    if ($file === false){
        header('Location: /download-file');
        exit();
    }
    ob_start();
    $basename = basename($file);
    header('Content-Disposition: attachment; filename=' . $basename);
    header('Content-Length: ' . filesize($file));
    header('Keep-Alive: timeout=5; max=100');
    header('Connection: Keep-Alive');
    header('Content-Type: application/octet-stream');
    ob_end_clean();
    readfile($file);
    exit();