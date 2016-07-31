<?php if(session_status() !== PHP_SESSION_ACTIVE ) session_start();?>
<?php require_once('../include/common.inc.php');?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="icon" href="../../favicon.ico">

    <title>Mailer</title>

    <!-- Bootstrap core CSS -->
    <link href="vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="css/style.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <!--<link href="vendor/bootstrap/css/navbar.css" rel="stylesheet">-->
    <script src="vendor/jquery/jquery-1.12.3.min.js"></script>
    <script src="//code.jquery.com/jquery-1.10.2.js"></script>
    <!-- Just for debugging purposes. Don't actually copy these 2 lines! -->
    <script src="vendor/bootstrap/js/ie-emulation-modes-warning.js"></script>
    <link rel="stylesheet" href="vendor/jqueryui/jquery-ui.min.css">
    <script src="vendor/jqueryui/jquery-ui.min.js"></script>
    <link rel="stylesheet" href="vendor/jqueryui/jquery-ui.structure.min.css">
    <link rel="stylesheet" href="vendor/jqueryui/jquery-ui.theme.min.css">
    <script src="js/storage.js"></script>
    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
    <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
    <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
</head>
<body>
<div class="container">