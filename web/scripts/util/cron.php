#!/usr/bin/env php

<?php
    $base_path = str_replace('scripts', '', __DIR__);
    include ($base_path . 'include/Db.class.php');
    include ($base_path . 'include/Mailer.class.php');

    $enable = intval(Db::get_option('enable'));
    if (!$enable) exit();
    $mail_per_once = intval(Db::get_option('mail_per_once'));
    $pause = intval(Db::get_option('pause'));
    $from = trim(Db::get_option('from'));


    $emails = Db::get_nosended_emails($mail_per_once);

    foreach($emails as $email){
        $images = $email['images'];
        $images = explode(',', $images);
        $files = array();
        $count = 0;
        if(is_array($images)){
            foreach($images as $image){
                if(!file_exists($image)) continue;
                $count++;
                $files[$count]['name'] = $image;
                $files[$count]['type'] = 'application/octet-stream';
            }
        }
        $result = Mailer::send3($email['email'], $email['subject'], $email['message'], $from, $files);
        if ($result){
            Db::mark_email_as_sended($email['email']);
            echo 'email to ' . $email['email'] . " отправлено\n";
        }
        sleep($pause);
    }
