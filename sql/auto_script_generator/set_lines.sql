declare
 v_line varchar2(32767) := '1';
 v_status number := 1;
 v_clob clob;
 v_error exception;
 v_null_count number := 0;
begin
  delete from hls_output_lines;

  dbms_output.enable(10000000);

  {script_function}


  while v_null_count <= 2 loop
    dbms_output.get_line(v_line, v_status);
    if v_line is null then
      v_null_count := v_null_count + 1;
    else
      v_null_count := 0;
    end if;
    if length(v_line) > 4000 then
      raise v_error;
    end if;
    v_clob := v_line;
    insert into hls_output_lines values(hls_output_lines_s.nextval, v_clob, v_line);
  end loop;

  commit;

  exception
    when v_error then
      dbms_output.put_line('有行超过4000个字符');
      insert into hls_output_lines values(hls_output_lines_s.nextval, v_clob, '有行超过4000个字符');

end;