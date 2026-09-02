# systemctl service to autostart webpage

* paths are hard coded
* If SELinux runs this may fail:
  * check _/var/log/messages_ and follow the instructions


* enable service (see below for failures):
   ```bash
   ln -s /opt/exseas_explorer/exseas_explorer/service/exseas_explorer.service /etc/systemd/system/

   systemctl daemon-reload
   systemctl enable exseas_explorer.service
   systemctl start exseas_explorer.service
   systemctl status exseas_explorer.service
   ```
