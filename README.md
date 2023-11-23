# Generate SQL for creating SQLite tables
**How to use:**

1. Fill in the `in.txt` file. One line represents one table. 

	Example of the `in.txt` file:
	> TableName1 column_name1 colum_name2 <br>
	> TableName2 column_name1 colum_name2 column_name3

2. Run `main.py`. The script will generate SQL and then store it in the `create-db.sql` file.
3. Additionally, you can now read the `sorted-in.txt` file. It contains the sorted contents of the `in.txt` file.

***Note before using:***

>  * If table names aren't capitalized, the script will do it
> automatically. Also, it will remove any `_` characters from those names.<br>
>  * If column names contain any capital letters, running the script
> will also replace them with their lower case counterparts.
>
> These changes will be present in both the `create-db.sql` file and the `sorted-in.txt` file.<br>
> Check the `log.txt` file for the verbose explanations on these and other user mistakes, and for the script failures.
