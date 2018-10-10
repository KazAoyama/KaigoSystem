#!/bin/bash
#
# RESTAURANT_DUMMY.CGI : スキャン画面呼び出し用のダミーページCGI
#
# Usage :  RESTAURANT_DUMMY.CGI
#
# Note  : スキャン画面の起動はURLのクエリ文字列「post_camera」で判定している。
#         「post_camera」と併せてデータ処理を実装したCGIをURLに指定するとスキ
#         ャン画面起動時点でデータ処理が実行されてしまうため、スキャン画面の
#         起動の際は当CGI（空ページを返す）を指定する。
#
# Written by R.Suzuki Date:2015/06/05 

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/SHOKUJI/CGI/SHOKUJI.INI &> /dev/null

#スキャン画面呼び出し用のダミーページ（空白ページを表示する）
echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
cat - 
exit 0

