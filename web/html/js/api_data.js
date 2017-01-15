/**
 * Created by user1 on 25.10.16.
 */

    var api_data = {};
    api_data.exchange='';
    api_data.method = '';

    var dict = {
        'balance':'Баланс',
        'user_orders':'Ордера',
        'user_trades':'История торгов',
        'ticker':'Тикер',
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
		$.get('/api-data',{'exchange':api_data.exchange, 'method':api_data.method}, showData);
		$( "#api-data" ).dialog("open");
	});

    function showData(data){
        //console.log(data);
        $( "#api-data" ).dialog({'title':dict[api_data.exchange] + ' - ' + dict[api_data.method]});
        document.getElementById("api-data").innerHTML = '';
        document.getElementById("api-data").innerHTML = data;
    }


