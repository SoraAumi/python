
json_model = '''
  {
    "current_seq": "{current_seq}",
    "revise_data": [
      {
        "ds_name": "{ds_name}",
        "tab_group": "{tab_group}",
        "columns": [
          {columns}
        ]
      }
    ]
  }
'''

column_model = '''
        {
            "column_name": "{column_name}",
            "property": {
              "readonly": {readonly_status},
              "required": {required}
            },
            "column_value": "{column_value}"
        }
'''