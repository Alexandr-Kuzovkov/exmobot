<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php') ?>

<?php if ($_SERVER['REQUEST_METHOD'] == 'POST'):
    $old_pass = (isset($_POST['old_pass']))? $_POST['old_pass'] : '';
    $pass1 = (isset($_POST['pass1']))? $_POST['pass1'] : '';
    $pass2 = (isset($_POST['pass2']))? $_POST['pass2'] : '';
    $login = (isset($_POST['login']))? $_POST['login'] : '';
    $result = Auth::changePass($login, $old_pass, $pass1, $pass2);
    $message = Auth::$messages[$result];
?>



<?php  endif; ?>

<form method="post" action="/change-pass">
    <div class="login-form">
        <div class="message"><?php echo isset($message)? $message : '';?></div>
        <div class="form-group">
            <input type="password" class="form-control" name="old_pass" placeholder="Старый пароль">
        </div>
        <div class="form-group">
            <input type="password" class="form-control" name="pass1" placeholder="Новый пароль">
        </div>
        <div class="form-group">
            <input type="password" class="form-control" name="pass2" placeholder="Повторите новый пароль">
        </div>
        <input type="hidden" name="login" value="<?php echo Auth::getCurrentUser(); ?>">
        <button type="submit" id="login-btn" class="btn btn-default">Сменить</button>
    </div>
</form>

<?php require_once('_footer.php')?>