""" 
Module for generating SQL for creating new tables in SQLite
Documentation: https://github.com/Matija-Djordjevic/sql-table-generator
"""
import sys
import datetime
import os

from tools import ArgsTypeChecker as checker 
from tools import ArgsFixer as fixer
from tools import ArgsValidator as validator
from tools import SqliteGenerator as generator

REDUNDANT_ARGS = ["", "\n", " "]
GITHUB_LINK = "https://github.com/Matija-Djordjevic/sql-table-generator"

if __name__=="__main__":
    log_file  = open("log.txt", "a", encoding="utf-8")
    log_file.write(f"{datetime.datetime.now()}\n")
    
    if not os.path.exists("in.txt"):
        open("in.txt", "w", encoding="utf-8")
        log_file.write("Aborted: 'in.txt' file missing!\n\n\n")
        print(f"No 'in.txt' file!\nMade you one :)\nFor help, check:\n{GITHUB_LINK}")
        exit()
        
    sql_out_file = open("create-db.sql", "w+", encoding="utf-8")
    sorted_in_file = open("sorted-in.txt", "w+", encoding="utf-8")
    
    in_file = open("in.txt", "r", encoding="utf-8")
    in_file_cont = in_file.read()
    in_file.close()

    if validator.contains_invalid_args(in_file_cont.lower().split("\n")):
        log_file.write(f"Invalid keywords in 'in.txt' such as: {' '.join(validator.INVALID_ARGS)}" + "\n\n")
        print("Errors occurred, check 'log.txt' for more info!")
        exit()
    
    # data curration
    lines = in_file_cont.split("\n")
    
    def can_represent_table(line: str):
        return line not in REDUNDANT_ARGS
    tables = list(filter(can_represent_table, lines))

    tables = sorted(tables)

    tables = [table.split(" ") for table in tables]

    def can_represent_column(table: str):
        return table not in REDUNDANT_ARGS
    tables = [list(filter(can_represent_column, table)) for table in tables] 

    # name fixing
    fix_table     = fixer.fix_table_name_arg
    fix_non_table = fixer.fix_non_table_name_arg
    tables = [[fix_table(table[0], log_file, line_ind)] + [fix_non_table(non_table_arg, log_file, line_ind) for non_table_arg in table[1:]] for (line_ind, table) in enumerate(tables)]

    for (ind, table) in enumerate(tables):

        table_name = table[0]
        columns = table[1:]
        
        # columns that end with _id last, rest sorted by alpha order
        columns = sorted(columns, key = lambda x : chr(sys.maxunicode) if x.endswith("_id") else x)
        
        sorted_in_file.write(table_name
                             + (" " + " ".join(columns)) if columns != [] else "" 
                             + "\n")

        foreign_keys = list(filter(checker.is_foreign_key_arg, columns))
        
        primary_and_composite_keys = list(filter(checker.is_primary_or_composite_key, columns))
        
        sql_out_file.write(generator.get_table_name_sql(table_name, end="\n"))

        have_primary_composite_and_keys = primary_and_composite_keys != []
        have_foreign_keys = foreign_keys != []
        have_columns = columns != []

        if not have_primary_composite_and_keys:
            sql_out_file.write(generator.get_default_key_sql(table_name, generator.get_new_line_sql()))
        
        sql_out_file.write(generator.get_created_column_sql(generator.get_new_line_sql()))
        
        sql_out_file.write(generator.get_modified_column_sql(generator.get_end_query_or_new_line_sql(columns == [])))
        
        if have_columns:
            sql_out_file.write(generator.get_column_names_sql(columns,
                                                              generator.get_end_query_or_new_line_sql(not have_foreign_keys and
                                                                                                      not primary_and_composite_keys)))

        if have_foreign_keys:
            sql_out_file.write(generator.get_foreign_keys_sql(foreign_keys,
                                                              table_name,
                                                              generator.get_end_query_or_new_line_sql(not have_primary_composite_and_keys)))
        
        if have_primary_composite_and_keys:
            sql_out_file.write(generator.get_primary_slash_composite_keys_sql(primary_and_composite_keys,
                                                                              generator.get_end_the_query_sql()))
    
    sql_out_file.close()

    log_file.write("\n\n")
    log_file.close()

    sorted_in_file.close()
    
    print("Done, check the 'log.txt' file for more info!")
