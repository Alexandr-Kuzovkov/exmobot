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

        function fillFileList(){
            var dir = $('#dir').val();
            $.post('/download-file', {dir:dir}, function(res){
                if (res.res){
                    $('#file-list').html(res.data);
                    $('.enter-dir').click(function(){
                        console.log(this);
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
                    var dir = $('#dir').val();
                    var arr = dir.split('/');
                    arr = trimArr(arr);
                    arr.pop();
                    dir = '/' + arr.join('/');
                    $('#dir').val(dir);
                    alert(res.data.message);
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

    </script>


<?php require_once('_footer.php')?>