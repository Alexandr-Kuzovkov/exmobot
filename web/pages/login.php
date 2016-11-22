
<?php require_once('_login_header.php') ?>


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

<?php require_once('_login_footer.php')?>