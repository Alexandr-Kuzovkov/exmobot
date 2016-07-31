var Storage =
{
	/**сохранение в локальном хранилище**/
	save: function(key,value){
		if ( typeof(localStorage) != 'undefined'){
            localStorage.setItem(key,JSON.stringify(value));
		}
	},
	
	/**чтение из локального хранилища**/
	load: function (key){
		if ( typeof(localStorage) != 'undefined'){
			return JSON.parse(localStorage.getItem(key));
		}
		return null; 
	},
    
    /**удаление значения из локального хранилища**/
	del: function (key){
		if ( typeof(localStorage) != 'undefined'){
			return localStorage.removeItem(key);
		}
		return null; 
	},
	
	/**очистка локального хранилища**/
	 clear: function(){
		if ( typeof(localStorage) != 'undefined'){
			localStorage.clear();
		}
	}

}