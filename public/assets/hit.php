<?php
// X などからのサイト流入を hits.log に 1 行ずつ記録する（site.js が utm_source 付きで開かれたときに呼ぶ）
// 形式: YYYY-MM-DD<TAB>source<TAB>cid   （日本時間。IP などの個人情報は残さない）
// GET ?stats=1 で日付×流入元の件数だけを JSON で返す（scripts/site_hits.py が読む）
header('Cache-Control: no-store');
$log = __DIR__ . '/hits.log';

if (isset($_GET['stats'])) {
    header('Content-Type: application/json');
    $out = [];
    foreach (@file($log, FILE_IGNORE_NEW_LINES) ?: [] as $line) {
        list($d, $src) = explode("\t", $line) + [1 => ''];
        $out[$d][$src] = ($out[$d][$src] ?? 0) + 1;
    }
    echo json_encode($out);
    exit;
}

$src = isset($_GET['src']) ? $_GET['src'] : '';
$cid = isset($_GET['cid']) ? $_GET['cid'] : '';
if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !preg_match('/^[a-z0-9_-]{1,20}$/', $src)
    || !preg_match('/^[A-Za-z0-9_-]{0,40}$/', $cid)) {
    http_response_code(400);
    exit;
}
$date = gmdate('Y-m-d', time() + 9 * 3600);
file_put_contents($log, "$date\t$src\t$cid\n", FILE_APPEND | LOCK_EX);
http_response_code(204);
