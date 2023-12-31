"""

"""
class ArgsValidator():
    INVALID_ARGS = ["created",  "modified"]

    @staticmethod
    def contains_invalid_args(args_list):
        for iArg in ArgsValidator.INVALID_ARGS:
            if iArg in args_list:
                return True
            
        return False
    
    @staticmethod
    def is_valid_table_name(table_name: str):
        return table_name[0].isupper() and "_" not in table_name

    @staticmethod
    def is_valid_foreign_key_arg(foreign_key: str):
        before_id_part = foreign_key[:-3]
        return before_id_part[0].isupper() and "_" not in before_id_part
    
    @staticmethod
    def is_valid_primary_or_composite_key(key_name: str):
        if ArgsTypeChecker.is_foreign_key_arg(key_name):
            after_key_part = key_name[3:]
            return ArgsValidator.is_valid_foreign_key_arg(after_key_part)
        else:
            return ArgsValidator.is_valid_column_name_arg(key_name)
    
    @staticmethod
    def is_valid_column_name_arg(column_name: str):
        return column_name.islower()

class ArgsTypeChecker():
    @staticmethod
    def is_foreign_key_arg(foreign_key: str):
        return foreign_key.endswith("_id") and foreign_key != "key_id"

    @staticmethod
    def is_primary_or_composite_key(key_name: str):
        return key_name != "key_id" and key_name.startswith("key") and len(key_name) > 3

class ArgsFixer():
    @staticmethod
    def fix_column_name_arg(column_name: str, log_file, err_line_ind, print_to_log = True) -> str:
        if print_to_log:
            log_file.write(f"    Line {int(err_line_ind)} ('in.txt'): Fixed COLUMN name: {column_name} -> ")
            
        fixed_name = column_name.lower()
        
        if print_to_log:
            log_file.write(f"{fixed_name}\n")

        return fixed_name

    @staticmethod
    def fix_foreign_key_arg(foreign_key_name: str, log_file, err_line_ind, print_to_log = True) -> str:
        if print_to_log:
            log_file.write(f"    Line {int(err_line_ind)} ('in.txt'): Fixed FOREIGN KEY name: {foreign_key_name} -> ")
        # TableName_id
        beofre_id = foreign_key_name[:-3]
        fixed_name = beofre_id.replace("_", "").capitalize() + "_id"
        
        if print_to_log:
            log_file.write(f"{fixed_name}\n")

        return fixed_name

    @staticmethod
    def fix_table_name_arg(table_name: str, log_file, err_line_ind) -> str:
        if not ArgsValidator.is_valid_table_name(table_name):
            log_file.write(f"    Line {int(err_line_ind)} ('in.txt'): Fixed TABLE name: {table_name} -> ")
            table_name = table_name.replace("_", "").capitalize()
            log_file.write(f"{table_name}\n")
    
        return table_name

    @staticmethod
    def fix_primary_or_composite_key(key_name: str, log_file, err_line_ind) -> str:
        log_file.write(f"    Line {int(err_line_ind)} ('in.txt'): Fixed PRIMARY/COMPOSITE KEY name: {key_name} -> ")
        if ArgsTypeChecker.is_foreign_key_arg(key_name):
            # keyTableName_id
            fixed_name = 'key' + ArgsFixer.fix_foreign_key_arg(key_name[3 : ], log_file, err_line_ind, print_to_log = False)
        else:
            # keycolumnname_id
            fixed_name = ArgsFixer.fix_column_name_arg(key_name, log_file, err_line_ind, print_to_log = False)
            
        log_file.write(f"{fixed_name}\n")
        
        return fixed_name
    
    @staticmethod
    def fix_non_table_name_arg(arg_name: str, log_file, err_line_ind) -> str:
        if ArgsTypeChecker.is_primary_or_composite_key(arg_name):
            if not ArgsValidator.is_valid_primary_or_composite_key(arg_name):
                return ArgsFixer.fix_primary_or_composite_key(arg_name, log_file, err_line_ind)
            
        elif ArgsTypeChecker.is_foreign_key_arg(arg_name):
              if not ArgsValidator.is_valid_foreign_key_arg(arg_name):
                return ArgsFixer.fix_foreign_key_arg(arg_name, log_file, err_line_ind)
              
        elif not ArgsValidator.is_valid_column_name_arg(arg_name):
                return ArgsFixer.fix_column_name_arg(arg_name, log_file, err_line_ind)
        
        return arg_name

class SqliteGenerator():
    @staticmethod
    def get_table_name_sql(table_name, end = ""):
        return f"CREATE TABLE {table_name} (" + end
    
    @staticmethod
    def get_end_the_query_sql():
        return "\n);\n"
    
    @staticmethod
    def get_end_query_or_new_line_sql(query_ends):
        if query_ends:
            return SqliteGenerator.get_end_the_query_sql()
        
        return ",\n"  
    
    @staticmethod
    def get_new_line_sql():          
        return ",\n"  
    
    @staticmethod
    def get_default_key_sql(table_name, end=""):
        return f"    {table_name.lower()}_id INTEGER PRIMARY KEY AUTOINCREMENT" + end
    
    @staticmethod
    def get_modified_column_sql(end=""):
        return "    modified TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP" + end
    
    @staticmethod
    def get_created_column_sql(end=""):
        return "    created TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP" + end
        
    @staticmethod
    def get_column_name_sql(column_name, end=""):
        if ArgsTypeChecker.is_primary_or_composite_key(column_name):
            column_name = column_name[3:]

        return f"    {column_name.lower()} INTEGER NOT NULL" + end
        
    @staticmethod
    def get_primary_slash_composite_keys_sql(key_name, end=""):
        return f"    PRIMARY KEY ({', '.join(map(lambda x: x[3: ], key_name))})" + end

    @staticmethod
    def get_column_names_sql(column_names, end=""):
        ret_str = ""
        
        if column_names == []:
            return ret_str

        if len(column_names) == 1:
            return SqliteGenerator.get_column_name_sql(column_names[0], end=end)
        
        for column_name in column_names[:-1]:
            ret_str += SqliteGenerator.get_column_name_sql(column_name, end=",\n")
        
        ret_str += SqliteGenerator.get_column_name_sql(column_names[-1], end=end)

        return ret_str
    
    @staticmethod
    def get_foreign_key_sql(key_name, table_name, end=""):
        foreign_table_name  = key_name[3:-3] if ArgsTypeChecker.is_primary_or_composite_key(key_name) else key_name[:-3]
        constraint_name     = f"{table_name.lower()}_{foreign_table_name.lower()}_fk"
        foreign_column_name = key_name.lower()
        
        return f"    CONSTRAINT {constraint_name} FOREIGN KEY ({foreign_column_name}) REFERENCES {foreign_table_name}({foreign_column_name})" + end

    @staticmethod
    def get_foreign_keys_sql(key_names, table_name, end=""):
        ret_str = ""

        if key_names == []:
            return ret_str

        if len(key_names) == 1:
            return SqliteGenerator.get_foreign_key_sql(key_names[0], table_name, end=end)

        for key_name in key_names[:-1]:
            ret_str += SqliteGenerator.get_foreign_key_sql(key_name, table_name, end=",\n")
        
        ret_str += SqliteGenerator.get_foreign_key_sql(key_names[-1], table_name, end=end)

        return ret_str
