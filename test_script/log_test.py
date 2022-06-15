# Create a logger object.
import logging
import coloredlogs

import emoji

logger = logging.getLogger('file_module')
coloredlogs.install(level='DEBUG')

# Some examples.
logger.debug("this is a debugging message")
logger.info("this is an informational message")
logger.warning("this is a warning message")
logger.error("this is an error message")
logger.critical("this is a critical message")

print(" (t1.employee_id = (select su.employee_id from sys_user su where su.user_id = ${/session/@user_id}) or ( ${/session/@user_id} in (select user_id from sys_user_role_groups where role_id = 1)) or exists (SELECT 1 FROM sys_user su,exp_employee_assigns eea,exp_employees ex,exp_org_position_vl eo WHERE su.employee_id = eea.employee_id AND eea.position_id = eo.position_id and ex.employee_id =su.employee_id and nvl (su.frozen_flag ,'N' )<>'Y' and eea.enabled_flag ='Y' and ex.enabled_flag ='Y' and eo.ENABLED_FLAG='Y' and sysdate between su.start_date and nvl(su.end_date ,to_date ('3000-01-01' ,'yyyy-mm-dd' )) and su.user_id = ${/session/@user_id} and eo.POSITION_CODE = '1200')or((select count(1)\n" +
		"  from sys_user_role_groups_vl v\n" +
		" where v.user_id =  ${/session/@user_id}\n" +
		"   and v.enabled_flag = 'Y'\n" +
		"   and v.role_code = 'ARCHIVIST')>0) or ${/session/@user_id} in (SELECT distinct user_id\n" +
		"        FROM exp_emp_assign_e_v e\n" +
		"       WHERE e.unit_code in (120, 70)))")
