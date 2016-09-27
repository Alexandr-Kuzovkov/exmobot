<!-- Static navbar -->
<nav class="navbar navbar-default">
    <div class="container-fluid">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="/">Exmo Bot</a>
        </div>
        <div id="navbar" class="navbar-collapse collapse">
            <ul class="nav navbar-nav">
                <li <?php check_active('');?>><a href="/">Биржи</a></li>
                <?php $log_files = get_log_files();?>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Логи<span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <?php foreach($log_files as $file): ?>
                        <li <?php check_active($file);?>><a href="/log?file=<?php echo $file;?>"><?php echo $file;?></a></li>
                        <?php endforeach;?>
                    </ul>
                </li>



                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Конфигурации<span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <?php $conf_files = get_conf_files();?>
                        <?php foreach($conf_files as $file): ?>
                            <li <?php check_active($file);?>><a href="/conf?file=<?php echo $file;?>"><?php echo $file;?></a></li>
                        <?php endforeach;?>
                        <li role="separator" class="divider"></li>
                        <li <?php check_active('add-conf');?>><a href="/add-conf">Добавить новый</a></li>
                    </ul>
                </li>

                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Стратегии<span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <?php $strategy_files = get_strategy_files();?>
                        <?php foreach($strategy_files as $file): ?>
                            <li <?php check_active($file);?>><a href="/strategy?file=<?php echo $file;?>"><?php echo $file;?></a></li>
                        <?php endforeach;?>
                    </ul>
                </li>
                <li <?php check_active('hard');?>><a href="/hard">Оборудование</a></li>
                
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Состояние<span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <li <?php check_active('database');?>><a href="/database?db=sqlite">Все данные(SQLite)</a></li>
                        <li <?php check_active('query');?>><a href="/query?db=sqlite">Запрос(SQLite)</a></li>
                        <li <?php check_active('balances');?>><a href="/balances?db=sqlite">Балансы(SQLite)</a></li>
                        <li <?php check_active('trades');?>><a href="/trades?db=sqlite">Сделки(SQLite)</a></li>
                        <li <?php check_active('copy');?>><a href="/copy?db=sqlite_mysql">Копирование SQLite -> MySQL</a></li>
                        <li role="separator" class="divider"></li>
                        <li <?php check_active('database');?>><a href="/database?db=mysql">Все данные(MySQL)</a></li>
                        <li <?php check_active('query');?>><a href="/query?db=mysql">Запрос(MySQL)</a></li>
                        <li <?php check_active('balances');?>><a href="/balances?db=mysql">Балансы(MySQL)</a></li>
                        <li <?php check_active('trades');?>><a href="/trades?db=mysql">Сделки(MySQL)</a></li>
                        <li <?php check_active('copy');?>><a href="/copy?db=mysql_sqlite">Копирование MySQL -> SQLite</a></li>
                        <li role="separator" class="divider"></li>
                        <li <?php check_active('backup');?>><a href="/backup?db=sqlite" target="_blank">Скачать файл базы SQLite</a></li>
                        <li <?php check_active('backup');?>><a href="/backup?db=mysql" target="_blank">Скачать дамп базы MySQL</a></li>
                        <li role="separator" class="divider"></li>
                        <li <?php check_active('backup');?>><a href="/upload?db=sqlite">Залить файл базы SQLite</a></li>
                        <li <?php check_active('backup');?>><a href="/upload?db=mysql">Залить базу MySQL</a></li>

                    </ul>
                </li>

            </ul>


            <ul class="nav navbar-nav navbar-right">
                <li <?php check_active('help');?>><a href="/help">Справка</a></li>
                <li <?php check_active('login');?>><a href="/login"><?php if(!Auth::isAuth()):?>Войти<?php else:?>Выйти<?php endif;?></a></li>
            </ul>
        </div><!--/.nav-collapse -->
    </div><!--/.container-fluid -->
</nav>
<script type="text/javascript">
    $('.navbar-nav li a').click(function(){
        $('.navbar-nav li').removeClass('active');
        $(this).parent().addClass('active');
    });


</script>
<!-- Main component for a primary marketing message or call to action -->
<div class="jumbotron">