<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST'){
    header('Content-Type: application/json');
    if (isset($_POST['dir'])){
        ob_start();
        $dir = $_POST['dir'];
        $files = scandir($dir);
        if (is_array($files) && count($files)){
            $output = array();
            foreach($files as $file){
                if ($file == '.') continue;
                $path = $dir . DIRECTORY_SEPARATOR . $file;
                $path = realpath($path);
                if (is_dir($path)){
                    $output[] = '<li><a class="enter-dir" id="'.$path.'"href="#"><img src="/img/folder.ico" width="20" height="20"/><b>' . $file . '</b></a></li>';
                }
            }
            foreach($files as $file){
                if ($file == '.') continue;
                $path = $dir . DIRECTORY_SEPARATOR . $file;
                $path = realpath($path);
                if (!is_dir($path)){
                    $output[] = '<li><a href="/get-file?file='. $path .'">' . $file . '</a></li>';
                }
            }

            echo json_encode(array('res' => true, 'data' => implode('', $output)));
            ob_end_flush();
        }else{
            ob_end_clean();
            echo json_encode(array('res' => false, 'data' => error_get_last()));
        }
    }
    exit();
}
?>
<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>


    <h3>Скачать файл</h3>
    <div class="error" id="error"></div>
    Каталог: <input id="dir" type="text" value="/tmp" size="100"/>
    <div id="file-list-wrap" class="scroll">
        <ul id="file-list">

        </ul>
    </div>

    <script type="text/javascript">

        $('#dir').change(function(){
            fillFileList();
        });

        $('#dir').keyup(function(){
            fillFileList();
        });

        /*заполнение списка файлов*/
        function fillFileList(){
            var dir = $('#dir').val();
            $.post('/download-file', {dir:dir}, function(res){
                console.log(res);
                if (res.res){
                    $('#error').html('');
                    $('#file-list').html(res.data);
                    $('.enter-dir').click(function(){
                        if (this.text == '..'){
                            var dir = $('#dir').val();
                            var arr = dir.split('/');
                            arr = trimArr(arr);
                            arr.pop();
                            dir = '/' + arr.join('/');
                            $('#dir').val(dir);
                        }else{
                            $('#dir').val(this.id);
                        }
                        fillFileList();
                    });
                }else{
                    var errno = getErrNo(res.data.message);
                    if (errno == 13){
                        var dir = $('#dir').val();
                        var arr = dir.split('/');
                        arr = trimArr(arr);
                        arr.pop();
                        dir = '/' + arr.join('/');
                        $('#dir').val(dir);
                    }
                    $('#error').html(res.data.message);
                }
            });

        }

        fillFileList();

    /* удаляет пустые строки из массива*/
    function trimArr(arr){
        if (arr.length == 0) return [];
        var i = 0;
        while (i < arr.length){
            if (arr[i] === ''){
                arr.splice(i,1);
            }else{
                i++;
            }
        }
        return arr;
    }

    /*получение номера ошибки*/
    function getErrNo(message){
        var regE = /\(errno \d{1,}\)/;
        var regE2 = /\d{1,}/;
        var match = message.match(regE);
        if (match){
            return match[0].match(regE2)[0];
        }
    }

</script>


<?php require_once('_footer.php')?>