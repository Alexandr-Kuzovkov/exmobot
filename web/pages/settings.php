<?php
    if ($_SERVER['REQUEST_METHOD'] == 'POST'){
        require_once ('../include/Db.class.php');
        $enable = isset($_POST['enable'])? 1 : 0;
        $pause = isset($_POST['pause'])? intval($_POST['pause']) : 5;
        $mail_per_once = isset($_POST['mail_per_once'])? intval($_POST['mail_per_once']) : 50;
        $from = isset($_POST['from'])? strval($_POST['from']) : '';
        Db::set_option('enable', $enable);
        Db::set_option('pause', $pause);
        Db::set_option('mail_per_once', $mail_per_once);
        Db::set_option('from', $from);

        //header('Location: /settings');
        //exit();
    }
?>

<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php
/**авторизация**/
if (!Auth::isAuth()) { echo '<label>Требуется авторизация!</label>'; exit();}
/**авторизация**/

$enable = Db::get_option('enable');
$pause = Db::get_option('pause');
$mail_per_once = Db::get_option('mail_per_once');
$from = Db::get_option('from');

?>

    <h3>Настройки</h3>

    <form method="post" action="/settings">
        <div class="login-form">
            <div class="form-group">
                <label>Разрешить отправку</label>
                <input type="checkbox" class="form-control" name="enable" <?php if($enable) echo 'checked';?>>
            </div>
            <div class="form-group">
                <label>Пауза между отправками (сек)</label>
                <input type="number" class="form-control" name="pause" value="<?php echo $pause;?>">
            </div>
            <div class="form-group">
                <label>Отправок за раз</label>
                <input type="number" class="form-control" name="mail_per_once" value="<?php echo $mail_per_once;?>">
            </div>
            <div class="form-group">
                <label>Обратный адрес</label>
                <input type="email" class="form-control" name="from" value="<?php echo $from;?>">
            </div>
            <button type="submit" id="login-btn" class="btn btn-default">Сохранить</button>
        </div>
    </form>
    <hr/>
    <form method="post" action="/reset-db">
        <button>Сброс базы данных</button>
    </form>


<?php require_once('_footer.php')?>