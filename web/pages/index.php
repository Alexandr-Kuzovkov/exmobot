<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php 
    /**авторизация**/
    if (!Auth::isAuth()) { echo '<label>Требуется авторизация!</label>'; exit();}
    /**авторизация**/
?>

<div class="exchange">
    <a href="https://exmo.com" target="_blank">
        <img src="img/exmo.png" />
        <p>EXMO</p>
    </a>
</div>
<div class="exchange">
    <a href="https://btc-e.nz" target="_blank">
        <img src="img/btce.png" />
        <p>BTC-E</p>
    </a>
</div>
<div class="clr"></div>
<?php require_once('_footer.php')?>
