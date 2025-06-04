GNU nano 7.2                    urls.php                              
<?php
// Retourne dynamiquement l'URL en JSON
header('Content-Type: application/json');
echo json_encode(["url" => "http://cogihi.pagekite.me"]);
/* A changer sur mon nom de doimaine  */
?>


