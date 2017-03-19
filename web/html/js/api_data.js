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
        'poloniex': 'Биржа Poloniex',
        'fix_profit': 'Зафиксировать прибыль',
        'cfm_fix_profit': 'Зафиксировать прибыль',
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

    /*отображение данных в окне диалога*/
    function showData(data){
        //console.log(data);
        $( "#api-data" ).dialog({'title':dict[api_data.exchange] + ' - ' + dict[api_data.method]});
        document.getElementById("api-data").innerHTML = '';
        document.getElementById("api-data").innerHTML = data;
        if (api_data.method == 'user_orders'){
            $('.order-cancel').click(handleCancelClick);
        }
        if (api_data.method == 'cfm_fix_profit'){
            $('.fix-profit').click(fixProfit);
        }
    }

    /*обновление данных в окне диалога*/
    function updateOrders(data){
        $( "#api-data" ).dialog({'title':dict[api_data.exchange] + ' - ' + dict[api_data.method]});
        document.getElementById("api-data").innerHTML = '';
        document.getElementById("api-data").innerHTML = data;
        $('.order-cancel').click(handleCancelClick);
    }


    /*обработчик клика на Cancel*/
    function handleCancelClick(ev){
        var order_id = this.id;
        $('#api-data').html('<img class="preload" src="img/preload.gif"/>');
        $( "#api-data" ).dialog({'title':'Loading...'});
        $.get('/api-data',{'exchange':api_data.exchange, 'method': 'order_cancel', 'id': order_id}, updateOrders);
    }

    /*обработка клика по кнопкам фиксации прибыли(confirm)*/
    $('.cfm-fix-profit').click(function(){
        var id = this.id;
        api_data.exchange = id.split('-')[0];
        api_data.method = 'cfm_fix_profit';
        session = id.split('~')[0];
        db = id.split('~').pop();
        $('#api-data').html('<img class="preload" src="img/preload.gif"/>');
        $( "#api-data" ).dialog({'title':'Loading...'});
        $.get('/api-data',{'exchange':api_data.exchange, 'method':api_data.method, 'session': session, 'db': db}, showData);
        $( "#api-data" ).dialog("open");
    });

    /*обработка клика по кнопкам фиксации прибыли(action)*/
    function fixProfit(){
        var id = this.id;
        api_data.exchange = id.split('-')[0];
        api_data.method = id.split('~')[0].split('-')[1];
        session = id.split('~').pop()
        $('#api-data').html('<img class="preload" src="img/preload.gif"/>');
        $( "#api-data" ).dialog({'title':'Loading...'});
        $.get('/api-data',{'exchange':api_data.exchange, 'method':api_data.method, 'session':session}, showData);
        
    }


