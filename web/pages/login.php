<?php
    if(session_status() !== PHP_SESSION_ACTIVE ) session_start();
    require_once ('../include/Auth.class.php');
    if(Auth::isAuth()){ Auth::logout(); header('Location: /');}
?>

<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>



    <form method="post" action="/auth">
    <div class="login-form">
        <div class="form-group">
            <input type="login" class="form-control" name="login" placeholder="Имя">
        </div>
        <div class="form-group">
            <input type="password" class="form-control" name="pass" placeholder="Пароль">
        </div>
        <button type="submit" id="login-btn" class="btn btn-default">Войти</button>
    </div>
    </form>

<?php require_once('_footer.php')?>