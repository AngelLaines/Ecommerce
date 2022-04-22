import psycopg2

class datos():
    
    def __init__(self):
        credenciales = {
                "dbname": "pelon",
                "user": "postgres",
                "password": "moreno2001",
                "host": "127.0.0.1",
                "port": 5432
            }
        self.conexion = psycopg2.connect(**credenciales)

    def buscar(self,tabla):
        cursor1=self.conexion.cursor()
        sql="select * from "+tabla
        cursor1.execute(sql)
        consulta=cursor1.fetchall()
        cursor1.close()
        return consulta
    
    def buscarUnaLinea(self,tabla,where,condicion):
        cursor1=self.conexion.cursor()
        sql="select * from "+tabla+ " where "+where+"='"+condicion+"'"
        cursor1.execute(sql)
        consulta=cursor1.fetchall()
        cursor1.close()
        return consulta
    
    def insertar(self,tabla,datos):
        cursor1=self.conexion.cursor()
        sql="insert into "+tabla+" values("
        i=1
        for n in datos:
            if type(datos[n])==int:
                sql+=str(datos[n])
            else:
                sql+="'"+datos[n]+"'"
            if i==len(datos):
                sql+=")"
            else:
                sql+=","
            i+=1
        cursor1.execute(sql)
        self.conexion.commit()
        cursor1.close()
        
    def update(self, consulta):
        cursor1=self.conexion.cursor()
        cursor1.execute(consulta)
        self.conexion.commit()
        cursor1.close()