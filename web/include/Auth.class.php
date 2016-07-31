<?php
	class Auth{
	
		static public $hash = '21232f297a57a5a743894a0e4a801fc3'; /*admin*/
		static public $login = 'admin';
		
		static public function login($login, $pass){
			if (isset($_SESSION)){
				$_SESSION['login'] = $login;
				$_SESSION['pass'] = $pass;
			}
		}
		
		static public function logout(){
			if (isset($_SESSION)){
				$_SESSION['login'] = '';
				$_SESSION['pass'] = '';
			}
		}
		
		static public function checkPass($login, $pass){						
			return ($login == self::$login && md5($pass) == self::$hash)? true : false;
		}
		
		static public function isAuth(){
			$login = (isset($_SESSION['login']))? $_SESSION['login'] : '';
			$pass = (isset($_SESSION['pass']))? $_SESSION['pass'] : '';
			return self::checkPass($login, $pass);
		}
		
		
	
	}
	
	
	