/**
 * Created by user1 on 29.11.16.
 */

(function() {

    var end = (new Date()).getTime();
    var chartInterval = 86400000 / 8;
    var start = end - chartInterval;

    var chartsObj = {exmo: [], btce: [], poloniex: []};
    var chartsStatus = Storage.load('charts_status');
    if (chartsStatus == null) chartsStatus = {exmo: {}, btce: {}, poloniex: {}};
    var controls = '<a href="#" id="back" class="controls">back</a> &nbsp; <a href="#" id="forward" class="controls">forward</a>';


    $('.collapse').on('show.bs.collapse', function () {
        var exchange = this.id;
        getTickerData(exchange, start, end, updateBlock);
    })


    function getTickerData(exchange, start, end, callback) {
        $.post('/get-ticker-data', {exchange: exchange, start: start, end: end}, function (data) {
            callback(exchange, data);
        })
    }

    function updateBlock(exchange, data) {
        drawChart(exchange, data);
        //showJson(exchange, data);

        $('.pair-title').click(function(){
            var id = this.id;
            var chart_id = id.split('-').pop();
            var exchange = chart_id.split('0')[0];
            var pair = chart_id.split('0')[1];
            $('#'+chart_id).toggle(400, function(){
                if($(this).css('display') == 'none'){
                    changeChartStatus(exchange,pair,false);
                }else{
                    changeChartStatus(exchange,pair,true);
                }

            });
        });

        $('.controls').click(function(){
            var id = this.id;
            console.log(id);
        });
    }


    function showJson(exchange, data) {
        $('#' + exchange).html(JSON.stringify(data));
    }

    Array_max = function () {
        return Math.max.apply(Math, arguments[0])
    }

    Array_min = function () {
        return Math.min.apply(Math, arguments[0])
    }

    function drawChart(exchange, data, field_list) {
        destroyCharts(exchange);
        //console.log(JSON.stringify(chartsStatus));
        var block_selector = exchange + ' div';
        if (field_list == undefined) field_list = ['last_trade', 'sell_price', 'buy_price'];
        var block = $('#' + block_selector);
        var lines = {};
        block.children().remove();
        block.append(controls);
        //console.log(block.children());
        for (pair in data) {
            //console.log(pair);
            if (chartsStatus[exchange][pair] == undefined)
                chartsStatus[exchange][pair] = false;
            lines[pair] = {};
            if (data[pair][0] == undefined) continue;
            var updates = []
            var dates = [];
            for (var i = 0; i < data[pair].length; i++) {
                var timestamp = parseInt(data[pair][i]['updated']) * 1000;
                updates.push(timestamp);
                var date = new Date();
                date.setTime(timestamp);
                var hour = date.getHours();
                var minute = date.getMinutes();
                dates.push([hour, minute].join(':'));
                //dates.push(date);
            }

            var colors = {
                'buy_price': 'rgba(75,192,192,1)',
                'sell_price': 'rgba(192,75,192,1)',
                'last_trade': 'rgba(192,192,75,1)'
            };
            lines[pair] = {labels: dates, datasets: []};
            for (field in data[pair][0]) {
                if (field_list.indexOf(field) == -1) continue;
                lines[pair]['datasets'].push({
                    label: field,
                    fill: false,
                    lineTension: 0.1,
                    backgroundColor: "rgba(75,192,192,0.4)",
                    borderColor: "rgba(75,192,192,1)",
                    borderCapStyle: 'butt',
                    borderDash: [],
                    borderDashOffset: 0.0,
                    borderJoinStyle: 'miter',
                    pointBorderColor: "rgba(75,192,192,1)",
                    //pointBorderColor: colors[field],
                    pointBackgroundColor: "#fff",
                    pointBorderWidth: 1,
                    pointHoverRadius: 1,
                    pointHoverBackgroundColor: "rgba(75,192,192,1)",
                    pointHoverBorderColor: "rgba(220,22,22,1)",
                    pointHoverBorderWidth: 4,
                    pointRadius: 1,
                    pointHitRadius: 2,
                    data: [],
                    options: {
                        scales: {
                            xAxes: [{
                                type: 'time',
                                time: {
                                    unit: 'minute'
                                }
                            }]
                        }
                    }
                });

                for (var i = 0; i < data[pair].length; i++) {
                    lines[pair]['datasets'][lines[pair]['datasets'].length - 1]['data'].push(data[pair][i][field]);
                }

            }

            var beginInterval = new Date(Array_min(updates));
            var endInterval = new Date(Array_max(updates));
            var chartDiv = document.createElement('canvas');
            var chartDivId = [exchange, '0', pair].join('');
            chartDiv.id = chartDivId;
            chartDiv.style = 'width:1000px;height:300px;';
            block.append(['<h5><span id="'+ ['head-',exchange,'0',pair].join('') +'" class="pair-title">',pair, '</span>: ', '<span class="time-interval">', beginInterval, '-', endInterval, '</span>', '</h5>'].join(' '));
            block.append(chartDiv);

            var options = {
                legend: {
                    display: true,
                    labels: {
                        fontColor: 'rgb(255, 99, 132)'
                    }
                }
            }

            var chart = new Chart(chartDivId, {type: 'line', data: lines[pair], options: options});
            if (chartsStatus[exchange][pair]){
                $('#'+chartDivId).show();
            }else{
                $('#'+chartDivId).hide();
            }
            chartsObj[exchange].push(chart);

        }
    }

    function destroyCharts(exchange) {
        while (chartsObj[exchange].length > 0) {
            chartsObj[exchange][0].destroy();
            chartsObj[exchange].splice(0, 1);
        }
    }

    function changeChartStatus(exchange, pair, status){
        chartsStatus[exchange][pair] = status;
        Storage.save('charts_status', chartsStatus);
    }

})()
