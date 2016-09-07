/*рисуем график*/
function draw_chart(element_id, options){
    //console.log(options);
    var el = document.getElementById(element_id);
    var width = options.width || 920; /*ширина canvas*/
    var height = options.height || 690;/*высота canvas*/
    el.width = width;
    el.height = height;
    var c = new Canvas(element_id);
    var margin = options.margin || 50; /*отступ*/

    var MAX_NUMBER_DATES = options.max_labels || 15; /*максимальное количество дат на графике*/
    var dates = options.dates || []; /*массив дат*/
    var curses = options.curses || [];/*массив курсов*/
    //console.log(dates);
    //console.log(curses);
    /*очистка*/
    c.clr();
    /*оси*/
    c.line(0,0,0,c.height-margin,{lineWidth:3});
    c.line(0,c.height-margin,c.width,c.height-margin,{lineWidth:3});
    //var delta = Math.floor((c.width - 2 * margin)/(dates.length - 1)); /*расстояние между линиями курсов по X*/
    var delta = (c.width - 2 * margin)/(dates.length - 1); /*расстояние между линиями курсов по X*/
    var mincurs = Infinity;
    var maxcurs = -1;
    /*определяем максимальный и минимальный курсы*/
    for (var i = 0; i < curses.length; i++){
        if ( mincurs > curses[i] ) mincurs = curses[i];
        if ( maxcurs < curses[i] ) maxcurs = curses[i];
    }
    mincurs = 0;
    var coff = (c.height - 3 * margin)/(maxcurs-mincurs);/*коэффициент масштабирования по Y*/
    var count = 0;
    /*отрисовка графика и подписей дат*/
    for ( var i = 0; i < dates.length; i++ ){
        count++;
        /*если дат много рисуем с пропусками чтоб не было наложения*/
        if ( (count % Math.floor(dates.length/MAX_NUMBER_DATES +1) ) == 0 ){
            c.text(dates[i],margin+delta*i, c.height,{color:[0,0,0], textAlign:'center'});
            c.line(margin+delta*i, c.height-margin, margin+delta*i, c.height-margin+30, {lineWidth:1,color:[100,200,100]});
        }
        c.line(margin+delta*i, c.height-margin, margin+delta*i, c.height-2*margin - (curses[i]-mincurs)*coff, {lineWidth:3,color:[255,0,0]});
    }
    /*линии минимума и максимума и подписи к ним*/
    c.line(0,c.height-2*margin,c.width,c.height-2*margin,{lineWidth:1,color:[100,100,100]});
    c.line(0,margin,c.width,margin,{lineWidth:1,color:[100,100,100]});
    c.text(mincurs,2,c.height-2*margin,{color:[0,0,0],textBaseline:'bottom',textAlign:'left'});
    c.text(maxcurs,2,margin,{color:[0,0,0],textBaseline:'bottom',textAlign:'left'});

    /*промежуточные линии и подписи к ним*/
    var step = (maxcurs - mincurs)/20;
    for (var i = 1; i < 20; i++ ){
        c.line(0,c.height-2*margin - (step*i)*coff,c.width,c.height-2*margin - (step*i)*coff,{lineWidth:1,color:[100,100,100]});
        c.text((mincurs+i*step).toFixed(4),2,c.height-2*margin - (step*i)*coff,c.width,{color:[0,0,0],textBaseline:'bottom',textAlign:'left'});
    }


}
