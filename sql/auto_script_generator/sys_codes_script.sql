begin
  sys_code_pkg.delete_sys_code('{code}');
  sys_code_pkg.insert_sys_code('{code}','{code_name}','{code_name}','{code_name}','ZHS','');
  sys_code_pkg.update_sys_code('{code}','{code}','{code}','{code}','US','');

  sys_code_pkg.insert_sys_code_value('{code}','{code_value}','{code_value_name}','ZHS','');
  sys_code_pkg.update_sys_code_value('{code}','{code_value}','{code_value}','US','');

  sys_code_pkg.insert_sys_code_value('{code}','N','否','ZHS','');
  sys_code_pkg.update_sys_code_value('{code}','N','N','US','');

    sys_code_pkg.insert_sys_code_value('{code}','A','不适用','ZHS','');
  sys_code_pkg.update_sys_code_value('{code}','A','A','US','');
 end;