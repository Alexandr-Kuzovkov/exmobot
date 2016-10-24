<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>
<?php require_once('_auth.php')?>

<div class="exchange">
    <a href="https://exmo.com" target="_blank">
        <img src="img/exmo.png" />
        <p>EXMO</p>
    </a>
    <a id="exmo-balance" class="api-data">Баланс</a> |
    <a id="exmo-user_orders" class="api-data">Ордера</a>
</div>
<div class="exchange">
    <a href="https://btc-e.nz" target="_blank">
        <img src="img/btce.png" />
        <p>BTC-E</p>
    </a>
    <a id="btce-balance" class="api-data">Баланс</a> |
    <a id="btce-user_orders" class="api-data">Ордера</a>
</div>
<div class="exchange">
    <a href="https://poloniex.com" target="_blank">
        <img src="img/poloniex.png" />
        <p>Poloniex</p>
    </a>
    <a id="poloniex-balance" class="api-data">Баланс</a> |
    <a id="poloniex-user_orders" class="api-data">Ордера</a>
</div>

<div class="clr"></div>
<div id="api-data"></div>
<script>
    var api_data = {};
    api_data.exchange='';
    api_data.method = '';

    var dict = {
        'balance':'Баланс',
        'exmo': 'Биржа EXMO',
        'btce': 'Биржа BTC-E',
        'poloniex': 'Биржа Poloniex'
    };

    $("#api-data").dialog({
		autoOpen: false,
		height: 400,
		width: 1000,
		modal: true
	});

    /*обработка клика по надписям - показ данных с api биржи*/
	$('.api-data').click(function(){
		var id = this.id;
        api_data.exchange = id.split('-')[0];
        api_data.method = id.split('-')[1];
		$('#api-data').html('<img class="preload" src="img/preload.gif"/>');
        $( "#api-data" ).dialog({'title':'Loading...'});
		$.get('/api',{'exchange':api_data.exchange, 'method':api_data.method}, showData);
		$( "#api-data" ).dialog("open");
	});

    function showData(data){
        console.log(data);
        $( "#api-data" ).dialog({'title':dict[api_data.exchange] + ' - ' + dict[api_data.method]});
        document.getElementById("api-data").innerHTML = '';
        document.getElementById("api-data").appendChild(createTable(data));
    }

    function createTable(data){
        data = JSON.parse(data);
        var table = document.createElement('table');
        table.className = 'table';
        for (var key in data){

            var tr = document.createElement('tr');
            var td1 = document.createElement('td');
            td1.innerHTML = key;
            tr.appendChild(td1);
            var td2 = document.createElement('td');
            td2.innerHTML = data[key];
            tr.appendChild(td2);
            table.appendChild(tr);
        }
        return table;
    }

</script>
<?php require_once('_footer.php')?>
