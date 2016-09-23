/**
 * конструктор объекта для работы с canvas(рисование графика)
 * @param canvasId id тега canvas
 **/
function Canvas(canvasId){
    this.canvas = document.getElementById(canvasId);
    this.context = this.canvas.getContext("2d");
    this.width = this.context.canvas.width;
    this.height = this.context.canvas.height;

    /**
     * очистка (заливка белым)
     **/
    this.clr = function(){
        this.context.fillStyle = 'rgb(255,255,255)';
        this.context.fillRect(0, 0, this.context.canvas.width, this.context.canvas.height);
    };

    /**
     * рисование линии
     * @param x1,y1,x2,y2 координаты начала и конца
     * @param options дополнительные параметры
     **/
    this.line = function(x1,y1,x2,y2,options){
        for (key in options){
            switch(key){
                case 'color': this.context.strokeStyle = 'rgba('+options.color.join(',')+',1.0)';break;
                default: this.context[key] = options[key];
            }
        }
        this.context.beginPath();
        this.context.moveTo(x1,y1);
        this.context.lineTo(x2,y2);
        this.context.stroke();
        this.context.closePath();
    };

    /**
     * вывод текста
     * @param text текст
     * @param x,y координаты текста
     * @param options дополнительные параметры
     **/
    this.text = function(text,x,y,options){
        for (key in options){
            switch(key){
                case 'color': this.context.fillStyle = 'rgba('+options.color.join(',')+',1.0)';break;
                default: this.context[key] = options[key];
            }
        }
        this.context.fillText(text,x,y);
    };
}