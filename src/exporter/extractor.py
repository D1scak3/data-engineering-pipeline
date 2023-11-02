import psycopg2 as psql

if __name__ == "__main__":
    print("CONNECTING TO POSTGRES...")
    conn = psql.connect(database="postgres", user="postgres", password="mysecretpassword", host="localhost", port="5432")

    print("QUERYING FOR DATA...")
    query = open("query.sql", "r").read()
    cur = conn.cursor()
    cur.execute(query)

    print("READING AND SAVING DATA...")
    with open("../../data/exported/exported_new_data.tsv", "w") as file:
        for row in cur:
            ls_row = list(row)
            # print(ls_row)
            # input(...)
            for x in range(len(ls_row)):
                ls_row[x] = str(ls_row[x])
                ls_row[x].replace("\t", " ")
            value = '\t'.join(map(str, ls_row))
            file.write(value + "\n")
    
    print("DONE WRITING DATA.")
    print("CLOSING EVERYTHING.")
    cur.close()
    conn.close        
