<?php
	class Auth{

		static private $users = array(
			array('login' => 'admin', 'hash' => '21232f297a57a5a743894a0e4a801fc3'),
		);

		static private $db = 'MySQL'; //используемая БД (MySQL | SQLite)

		static public $messages = array(
			'Пароли не совпадают',
			'Старый пароль неверен',
			'Пароль успешно изменен',
			'Ошибка при обновлении пароля'
		);
		
		static public function login($login, $pass){
			if (isset($_SESSION)){
				$_SESSION['login'] = $login;
				$_SESSION['pass'] = $pass;
			}
		}
		

		static protected function _hash($str){
			return md5($str);
		}

		static public function logout(){
			if (isset($_SESSION)){
				$_SESSION['login'] = '';
				$_SESSION['pass'] = '';
			}
		}
		
		static public function checkPass($login, $pass){
			self::getUsers();
			foreach(self::$users as $user){
				if ($login == $user['login'] && self::_hash($pass) == $user['hash'])
					return true;
			}
			return false;
		}
		
		static public function isAuth(){
			$login = (isset($_SESSION['login']))? $_SESSION['login'] : '';
			$pass = (isset($_SESSION['pass']))? $_SESSION['pass'] : '';
			return self::checkPass($login, $pass);
		}

		public static function getCurrentUser(){
			return (self::isAuth())? $_SESSION['login'] : 'guest';
		}

		static protected function getUsers(){
			$users = null;
			$db = null;
			$db = (self::$db == 'MySQL')? MySQL::get_instance() : SQLite::get_instance();
			if ($db)
				$users = $db->get('user');
			if (is_array($users) && count($users)){
				self::$users = array();
				foreach($users as $user){
					self::$users[] = array('login' => $user['login'], 'hash' => $user['hash'], 'role' => $user['role']);
				}
			}
		}

		static public function changePass($login, $old_pass, $pass1, $pass2){
			if ($pass1 != $pass2)
				return 0;
			if (!self::checkPass($login, $old_pass))
				return 1;
			$db = (self::$db == 'MySQL')? MySQL::get_instance() : SQLite::get_instance();
			$users = $db->get('user', array('login=' => $login));
			if (is_array($users) && count($users)){
				$res = $db->update('user', array('hash' => self::_hash($pass1)), array('login=' => $login));
			}else{
				$res = $db->insert('user', array('hash' => self::_hash($pass1), 'login'=>$login));
			}
			return ($res)? 2 : 3;
		}

	}
	
	
	