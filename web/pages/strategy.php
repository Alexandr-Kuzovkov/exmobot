<?php require_once('_header.php') ?>
<?php require_once('_topmenu.php')?>

<?php
$filename = isset($_GET['file'])? $_GET['file'] : '';
$path = '../../strategy/';
$fullname = realpath($path . $filename);
$content = file_get_contents($fullname);

?>
    <h3>Торговая стратегия <span class="filename"><?php echo $filename; ?></span> </h3>
    <pre class="scroll2"><?php echo $content;?></pre>


<?php require_once('_footer.php')?>