#!/bin/sh
/happypandax/happypandax user create -t "admin" -u "TODO" -p "TODO"
/happypandax/happypandax --restore /happypandax/data/HPX_Backup.zip

chown -R hpx:hp /media/Files