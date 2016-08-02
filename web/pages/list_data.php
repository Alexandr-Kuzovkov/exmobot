<?php require_once ('../include/Db.class.php');?>
<?php
    if(isset($_POST['type'])){
        if($_POST['type'] == 'sended')
            $emails = Db::get_all_sended_emails();
        elseif($_POST['type'] == 'nosended')
            $emails = Db::get_all_nosended_emails();
        else
            $emails = Db::get_email();
    }else{
        $emails = Db::get_email();
    }
?>

<table class="table list" >
    <?php $count = 0; foreach ($emails as $row): $count ++;?>
        <tr>
            <?php foreach($row as $key=>$val): if($key == 'subject' || $key == 'message' || $key == 'images') continue;?>
                <td>
                    <?php
                    if($key == 'ctime')
                        echo date('Y-m-d H:i:s',$val);
                    elseif ($key == 'status')
                        echo ($val == 0)? '<a title="Отправить" class="email-send" href="#" id="send-'.$row['email'].'">не отправлено</a>' : 'отправлено';
                    elseif ($key == 'email')
                        echo '<a href="#" class="email" id="'.$val.'" title="Посмотреть">' . $val . '</a>';
                    elseif ($key == 'id')
                        echo $count;
                    else
                        echo $val;
                    ?>
                </td>
            <?php endforeach;?>
        </tr>
    <?php endforeach;?>
</table>
