import mysql.connector


while True:
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="layefaye",
    database="projetlicence"
    )

            
    mycursor = mydb.cursor()

    sql = "SELECT id, activate_at FROM connection_station"

    mycursor.execute(sql)

    myresult = mycursor.fetchall()
    
    for x in myresult:
        if x[1]:
            # sql = "UPDATE connection_station SET activate_at = null, statut = true  WHERE id = 23"
            mycursor = mydb.cursor()
            
            sql = "UPDATE connection_station SET statut=1 WHERE id=23"
            mycursor.execute(sql)
            print(mycursor.fetchall())
            # myresult = mycursor.fetchall()
            # print(myresult)
            mycursor.close()
            print(x[1])
            
    break