<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php require_once ('_chartjs.php')?>

<h3>Тикеры</h3>

   <div class="exchange-block">
        <a class="btn btn-primary" role="button" data-toggle="collapse" href="#exmo" aria-expanded="false" aria-controls="collapseExample">
            EXMO
        </a>

        <div class="collapse" id="exmo">
            <div class="well">
                <img src="/img/loading.gif"/>
            </div>
        </div>
    </div>

    <div class="exchange-block">
        <a class="btn btn-primary" role="button" data-toggle="collapse" href="#btce" aria-expanded="false" aria-controls="collapseExample">
            BTCE
        </a>

        <div class="collapse" id="btce">
            <div class="well">
                <img src="/img/loading.gif"/>
            </div>
        </div>
    </div>

    <div class="exchange-block">
        <a class="btn btn-primary" role="button" data-toggle="collapse" href="#poloniex" aria-expanded="false" aria-controls="collapseExample">
            Poloniex
        </a>

        <div class="collapse" id="poloniex">
            <div class="well">
                <img src="/img/loading.gif"/>
            </div>
        </div>
    </div>


<script type="text/javascript" src="/js/drawcharts.js"></script>

<?php require_once('_footer.php')?>