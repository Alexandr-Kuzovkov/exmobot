<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php require_once('_auth.php')?>

<form method="post" action="/del-images"/>
    <div id="img-list">

        <?php
            $images = get_images($_SERVER['DOCUMENT_ROOT'] . '/' . IMG_DIR);
            if(count($images)):
            foreach($images as $name => $src):
        ?>

                <div class="img-conteiner">
                    <img src="<?php echo $src;?>" alt="<?php echo $name?>"/>
                    <p><?php echo $name;?>&nbsp; <input class="img-checkbox" type="checkbox" name="<?php echo $name?>"/></p>
                </div>


        <?php endforeach; else:?>
        <p>Изображений не загружено</p>
        <?php endif;?>
        <div class="clr"></div>
    </div>
    <button class="img-del-btn">Удалить отмеченные</button>
</form>
<a href="#" id="select-all-img">Отметить все</a>
<a href="#" id="unselect-all-img">Снять отметки со всех</a>
<div class="clr"></div>

<form method="post" action="/img-upload" enctype="multipart/form-data">
    <div class="login-form">
        <div class="form-group">
            <label for="file">Файлы изображения</label>
            <input id="file" type="file" class="form-control" name="img[]" multiple placeholder="Файл изображения">
        </div>
        <button type="submit" id="login-btn" class="btn btn-default">Загрузить</button>
    </div>
</form>

<script type="text/javascript">
    $('#select-all-img').click(function(ev){
        ev.preventDefault();
        $('input:checkbox').prop('checked', true);
    });

    $('#unselect-all-img').click(function(ev){
        ev.preventDefault();
        $('input:checkbox').prop('checked', false);
    });
</script>
<?php require_once('_footer.php')?>
