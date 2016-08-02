<?php

$base_path = str_replace('include', '', __DIR__);
require_once ($base_path . 'vendor/PHPMailer/PHPMailerAutoload.php');


/**
 * Created by PhpStorm.
 * User: user1
 * Date: 22.05.16
 * Time: 21:15
 */
class Mailer{


    /**
     * отправка электронной почты через функцию mail
     * @param $to
     * @param $subject
     * @param $message
     * @param $from
     * @return bool
     */
    public static function send($to, $subject, $message, $from){
        $headers   = array();
        $headers[] = "MIME-Version: 1.0";
        $headers[] = "Content-type: text/plain; charset=utf-8";
        $headers[] = "From: {$from}";
        $headers[] = "Subject: {$subject}";
        $headers[] = "X-Mailer: PHP/".phpversion();

        return mail($to, $subject, $message, implode("\r\n", $headers));
    }



    /**
     * отправка электронной почты через класс PHPMailers
     * @param $to
     * @param $subject
     * @param $message
     * @param $from
     * @param null $file
     * @return bool
     * @throws phpmailerException
     */
    public static function send3($to, $subject, $message, $from, $files=null){
        $mail = new PHPMailer();
        $mail->setFrom($from, substr($from,0, strpos($from,'@')));
        $mail->addAddress($to, $to);
        $mail->addCustomHeader('From', $from);
        $mail->addCustomHeader('X-Mailer', 'PHP/'.phpversion());
        $mail->Subject  = trim($subject);
        $mail->isHTML(true);
        $mail->Body     = $message;
        $mail->AltBody = strip_tags($message);
        if ($files != null && is_array($files) && count($files)){
            foreach($files as $file){
                $mail->addAttachment($file['name'], basename($file['name']), 'base64', $file['type']);
            }
        }
        return $mail->send();
    }


}