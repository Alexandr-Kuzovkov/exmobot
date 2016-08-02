<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php
/**авторизация**/
if (!Auth::isAuth()) { echo '<label>Требуется авторизация!</label>'; exit();}
/**авторизация**/
?>


    <form method="post" action="/upload" enctype="multipart/form-data">
        <div class="login-form">
            <div class="form-group">
                <label for="file">Файл со списком адресов</label>
                <input id="file" type="file" class="form-control" name="file" placeholder="Файл со списком email">
            </div>
            <button type="submit" id="login-btn" class="btn btn-default">Загрузить</button>
        </div>
    </form>


<?php require_once('_footer.php')?>