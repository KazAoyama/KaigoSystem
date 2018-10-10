<?php
        set_time_limit(0);
        header("Content-Type: text/event-stream");
        header('Cache-Control: no-cache');
        $i = rand(0,9);
        echo "data: サーバ側の出力:$i\n\n";
        echo "retry: 3000";
