<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>

<div class="exchange">
    <a href="https://exmo.com" target="_blank">
        <img src="img/exmo.png" />
        <p>EXMO</p>
    </a>
    <a id="exmo-balance" class="api-data">Баланс</a> |
    <a id="exmo-user_orders" class="api-data">Ордера</a> |
    <a id="exmo-user_trades" class="api-data">История торгов</a>
</div>
<div class="exchange">
    <a href="https://btc-e.nz" target="_blank">
        <img src="img/btce.png" />
        <p>BTC-E</p>
    </a>
    <a id="btce-balance" class="api-data">Баланс</a> |
    <a id="btce-user_orders" class="api-data">Ордера</a> |
    <a id="btce-user_trades" class="api-data">История торгов</a>
</div>
<div class="exchange">
    <a href="https://poloniex.com" target="_blank">
        <img src="img/poloniex.png" />
        <p>Poloniex</p>
    </a>
    <a id="poloniex-balance" class="api-data">Баланс</a> |
    <a id="poloniex-user_orders" class="api-data">Ордера</a> |
    <a id="poloniex-user_trades" class="api-data">История торгов</a>
</div>

<div class="clr"></div>
<div id="api-data"></div>

<script type="text/javascript" charset="utf8" src="js/api_data.js"></script>
<?php require_once('_footer.php')?>
