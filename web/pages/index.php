<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php 
    /**авторизация**/
    if (!Auth::isAuth()) { echo '<label>Требуется авторизация!</label>'; exit();}
    /**авторизация**/
?>


<?php require_once('_footer.php')?>
