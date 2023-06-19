-- AlertType 
replace into ZabbixAlert_text.AlertType values(1,'SMS');
replace into ZabbixAlert_text.AlertType values(2, 'Email');
replace into ZabbixAlert_text.AlertType values(3, 'Wechat');

-- AppTye
replace into ZabbixAlert_text.AppType values(1,'PERFORMANCE');
replace into ZabbixAlert_text.AppType values(2,'PING');
replace into ZabbixAlert_text.AppType values(3,'SNMP');
replace into ZabbixAlert_text.AppType values(4,'APPLICATION');

