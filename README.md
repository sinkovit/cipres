## Utility programs for Cipres project

```
usage: cipres_data_parse.py [-h]
                            [-t {beast,beast2,migrate_parm,migrate_infile}]
                            file_name

Process file name and file type cmd line args

positional arguments:
  file_name

optional arguments:
  -h, --help            show this help message and exit
  -t {beast,beast2,migrate_parm,migrate_infile}, --type {beast,beast2,migrate_parm,migrate_infile}
```

### Note

cipres_data_parse.py can determine the filetype for most files, but
also provides the option to specify the file type. We recommend using
the latter since it is probably more robust. In addition, the program
cannot currently identify files of type 'migrate_infile'
