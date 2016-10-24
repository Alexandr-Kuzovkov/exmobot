<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php
    /**авторизация**/
    if (!Auth::isAuth()) { echo '<label>Требуется авторизация!</label>'; exit();}
    /**авторизация**/
?>

<h3>Установка темы и тела писем</h3>
<form method="post" action="/save-data">
    <div class="login-form">
        <div class="form-group align-left">
            <input type="text" class="form-control" name="subject" placeholder="Тема">
        </div>
        <div class="form-group">
            <textarea  id="need-tinymce" name="message">Текст</textarea>
        </div>

        <div class="img-list-wrap">
           <!-- <form method="post" action="/app-images"/>-->
            <div id="img-list">

                <?php
                $images = get_images($_SERVER['DOCUMENT_ROOT'] . '/' . IMG_DIR);
                if(count($images)):
                    foreach($images as $name => $src):
                        ?>

                        <div class="img-conteiner">
                            <img src="<?php echo $src;?>" alt="<?php echo $name?>"/>
                            <p><?php echo $name;?>&nbsp; <input class="img-checkbox" type="checkbox" name="attacment:<?php echo $name?>"/></p>
                        </div>


                    <?php endforeach; else:?>
                    <p>Изображений не загружено</p>
                <?php endif;?>
                <div class="clr"></div>
            </div>
            <a href="#" id="select-all-img">Отметить все</a>
            <a href="#" id="unselect-all-img">Снять отметки со всех</a>
            <p>&nbsp;</p>
            <!--<button class="img-del-btn">Прикрепить отмеченные</button>-->
    <!--</form>-->
    </div>
    <div class="clr"></div>

        <div class="form-group">
            <label>Только для неотправленных</label>
            <input type="checkbox" class="form-control" name="onlysended">
        </div>
        <button type="submit" id="login-btn" class="btn btn-default">Сохранить</button>
    </div>
</form>
<a href="#" id="application-img">Прикрепление изображений</a>




<script type="text/javascript">
    $('#application-img').click(function(){
        if ($(this).text() == 'Прикрепление изображений'){
            $('.img-list-wrap').show(1000);
            $(this).text('Скрыть изображения');
        }else{
            $('.img-list-wrap').hide(1000);
            $(this).text('Прикрепление изображений');
        }
    });


    $('#select-all-img').click(function(ev){
        ev.preventDefault();
        $('.img-checkbox').prop('checked', true);
    });

    $('#unselect-all-img').click(function(ev){
        ev.preventDefault();
        $('.img-checkbox').prop('checked', false);
    });
</script>

<?php require_once('_tinymce.php')?>
<?php require_once('_footer.php')?>
