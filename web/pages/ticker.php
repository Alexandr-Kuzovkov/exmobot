<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>

<h3>История торгов</h3>

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


<script>
    var end = (new Date()).getTime();
    var start = end - 86400000;

    $('#exmo').on('show.bs.collapse', function () {
        var exchange = this.id;
        getTickerData(exchange,start,end,function (data) {
            console.log(data);
            var block = $('#exmo div');
            fillBlock(block, data);
        })
    })

    $('#btce').on('show.bs.collapse', function () {
        var exchange = this.id;
        getTickerData(exchange,start,end,function (data) {
            console.log(data);
            var block = $('#btce div');
            fillBlock(block, data);
        })
    })

    $('#poloniex').on('show.bs.collapse', function () {
        var exchange = this.id;
        getTickerData(exchange,start,end,function (data) {
            console.log(data);
            var block = $('#poloniex div');
            fillBlock(block, data);
        })
    })
    
    function getTickerData(exchange, start, end, callback){
        $.post('/get-ticker-data', {exchange:exchange, start:start, end:end}, function (data) {
            callback(data);
        })
    }

    function getExchangePairs($exchange, callback){
        $.post('/get-exchange-pairs', {exchange:exchange}, function (data) {
            callback(data);
        })
    }

    function fillBlock(block, data){
        block.html(JSON.stringify(data));
    }

</script>

<?php require_once('_footer.php')?>