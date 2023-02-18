The following files are contained in this repo:

### ProgrammerWeek.ipynp
- The notebook for the entire workshop. Notebook contains a variety of notes and images for self study. You create the data for the notebook using the createData.py program. The notebook and program must reside in the same location.

### createData.py
- Creates the data for the workshop. File includes two functions:
    - **createProducts**(*connection name*, *number of rows per worker*) - Creates a fake product orders table. The function creates n number of rows PER thread. For example, if you specify the value 100 and have 16 threads, the function will create 1600 rows. Be careful when specifying n.
    - **createDiscountData**(*connect name*) - Creates a fake discount code lookup table with 7 rows.

### Images folder
- Notebook pulls images from the image folder to display in the notebook.
