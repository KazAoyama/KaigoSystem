#!/bin/bash
# HTML の出力



echo -e "Content-Type: text/event-stream\n\n"
echo -e "data: サーバデータ\n\n"


: <<'#__COMENTOUT__'

newinfo=""
bkinfo=""

while :
do
  
  newinfo=$(ls --full-time  /home/hands/E-LIFE/SHOKUJI/POMPA/0003/201508/TEST_REST | self 5/NF-1)

  if [ "$newinfo" != "$bkinfo" ] ; then

    echo -e "Content-Type: text/event-stream\n\n"
 #   echo -e "event: ping\n"
    echo -e "data: 更新あり" $newinfo "\n\n"

    bkinfo=$(ls --full-time  /home/hands/E-LIFE/SHOKUJI/POMPA/0003/201508/TEST_REST | self 5/NF-1)

  fi

done


#__COMENTOUT__

#newinfo=$(ls --full-time  /home/hands/E-LIFE/SHOKUJI/POMPA/0003/201508/TEST_REST | self 5)
#echo -e "Content-Type: text/event-stream\n\n"
#echo -e "data: $(echo $newinfo) \n\n"


