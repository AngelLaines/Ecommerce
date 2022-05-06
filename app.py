from flask import Flask, render_template, request, session
from flask.templating import render_template_string
from numpy import empty
from werkzeug.utils import redirect,secure_filename
from datetime import datetime
import secrets
import bd,sys,os
import json

bdEcommerce=bd.datos()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = './static/img'

@app.route('/shop',methods=["GET","POST"])
def tienda():
    error=None
    rowCate=bdEcommerce.buscar("catalogo")
    productRow=bdEcommerce.buscar("producto")
    if 'idUsuario' in session and 'tipo' in session:
        userRow=bdEcommerce.buscarUnaLinea("clientes","idUsuario",session['idUsuario'])
        idcliente=bdEcommerce.buscarUnaLinea("clientes","idusuario",session['idUsuario'])[0][0]
        condicion="ca.idCliente='"+str(idcliente)+"' and ca.estado='En carrito'"
        cart=bdEcommerce.search("carrito"," ca join producto pr on ca.idproducto=pr.idproducto where ",condicion)
        if request.method=='POST':
            if request.form['submitButton']=="ver producto":
                print("ver producto")
                return redirect('/')
            if request.form['submitButton']=="añadir al carrito":
                carrito=bdEcommerce.buscarUnaLinea("carrito","idCliente",userRow[0][0])
                nombre=request.form['nameProduct']
                idProducto=request.form['IdProduct']
                
                if len(carrito)>0:
                    idCarrito=bdEcommerce.buscarUnaLinea("carrito","idCliente",userRow[0][0])[0][0]
                else:
                    idCarrito=int(datetime.today().strftime('%H%S%m%d'))+9999
                
                IdCliente=bdEcommerce.buscarUnaLinea("clientes","idUsuario",session['idUsuario'])[0][0]
                cantidad=1
                subTotal=cantidad*float(request.form['price'])
                fecha=str(datetime.today().strftime('%Y-%m-%d'))
                print(idCarrito)
                print(subTotal)
                datos={
                    'idCarrito':idCarrito,
                    'idcliente':IdCliente,
                    'idProducto':idProducto,
                    'cantidad':cantidad,
                    'subtotal':subTotal,
                    'fechaagregado':fecha,
                    'estado':'En carrito'
                    
                }
                if len(bdEcommerce.buscarUnaLinea("carrito","idCliente",userRow[0][0])) > 1:
                    cantidad=float(bdEcommerce.buscarUnaLinea("carrito","idCliente",userRow[0][0])[0][3])+1
                    subtotal = float(bdEcommerce.buscarUnaLinea("producto","idProducto",request.form['IdProduct'])[0][4])*cantidad
                    sql = "update carrito set cantidad = "+str(cantidad)+ ", subtotal = "+str(round(subtotal,2))+" where idCliente='"+str(IdCliente)+"' and idProducto="+request.form['IdProduct']+" and idCarrito="+str(idCarrito)
                    bdEcommerce.update(sql)
                else:
                    bdEcommerce.insertar("carrito",datos)
                return redirect('/carrito')
            return redirect('/')
        if session['tipo']=="Admin":
            return render_template('shop.html',productos=productRow,tipo=session['tipo'],categorias=rowCate)
        return render_template('shop.html',user=userRow[0][2],productos=productRow,categorias=rowCate,numCart=len(cart))
    return render_template('shop.html',productos=productRow,categorias=rowCate)

@app.route('/modificarProducto',methods=["GET","POST"])
def modificar():
    error=None
    if 'idUsuario' in session and 'tipo' in session:
        if request.method=='POST':
            id=session['idProducto']
            nombre=request.form['nombre']
            idProveedor=bdEcommerce.buscarUnaLinea("proveedor","nombreproveedor",request.form.get('proveedor'))[0][0]
            idCategoria=bdEcommerce.buscarUnaLinea("catalogo","nombrecategoria",request.form.get('categoria'))[0][0]
            preciounitario=str(request.form['precio'])
            
            sql="update producto set nombreproducto='"+nombre+"', preciounitario="+preciounitario+", idproveedor="+str(idProveedor)+", idcatalogo="+str(idCategoria)+" where idProducto="+str(id)
            bdEcommerce.update(sql)
            return redirect('/modificarProducto')
        return render_template('ModificarProducto.html',tipo=session['tipo'])

@app.route('/buscar',methods=["GET","POST"])
def buscar():
    if request.method=='POST':
        session['idProducto']=request.form['idProducto']
        datos=bdEcommerce.buscarUnaLinea("producto","idProducto",request.form['idProducto'])
        proveedor=list()
        categoria=list()
        rowsP=bdEcommerce.buscar("proveedor")
        rowsC=bdEcommerce.buscar("catalogo")
        for elemento in rowsP:
            proveedor.append(elemento[1])
        for elemento in rowsC:
            categoria.append(elemento[1])
        return render_template('ModificarProducto.html',nombre=datos[0][3],precio=datos[0][4],tProveedor=proveedor,tCategoria=categoria)

@app.route('/eliminarProducto',methods=["GET","POST"])
def deleteProduct():
    error=None
    if 'idUsuario' in session and 'tipo' in session:
        if request.method=='POST':
            listaEliminar = request.form.getlist('checkbox')
            print(listaEliminar)
            for elemento in listaEliminar:
                sql="delete from carrito where idProducto="+str(elemento)
                bdEcommerce.delete(sql)
                sql="delete from producto where idProducto="+str(elemento)
                bdEcommerce.delete(sql)
                os.remove('./static/img/'+elemento+'.png')
            return redirect('/eliminarProducto')
        else:
            rows=bdEcommerce.buscar("producto")
            return render_template("eliminarProducto.html",productos=rows,tipo=session['tipo'])

@app.route('/añadirProducto',methods=["GET","POST"])
def addProduct():
    error=None
    if 'idUsuario' in session and 'tipo' in session:
        if request.method=='POST':
            f = request.files['imagen']
            filename = secure_filename(f.filename)
            print(filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            idProducto=int(datetime.today().strftime('%H%S%m%d'))+666
            nombre=request.form['nombre']
            print(request.form.get('proveedor'))
            print(request.form.get('categoria'))
            idProveedor=bdEcommerce.buscarUnaLinea("proveedor","nombreproveedor",request.form.get('proveedor'))[0][0]
            idCategoria=bdEcommerce.buscarUnaLinea("catalogo","nombrecategoria",request.form.get('categoria'))[0][0]
            preciounitario=float(request.form['precio'])
            
            datos={
                'idproducto':idProducto,
                'idcatalogo':idCategoria,
                'idproveedor':idProveedor,
                'nombre':nombre,
                'precio':preciounitario
            }
            bdEcommerce.insertar("producto",datos)
            
            rutaO='./static/img/'+str(filename)
            
            nombre_nuevo='./static/img/'+str(idProducto)+'.'+filename.split('.')[1]
            os.rename(rutaO, nombre_nuevo)
            return redirect('/añadirProducto')
        else:
            proveedor=list()
            categoria=list()
            rowsP=bdEcommerce.buscar("proveedor")
            rowsC=bdEcommerce.buscar("catalogo")
            
            for elemento in rowsP:
                proveedor.append(elemento[1])
            for elemento in rowsC:
                categoria.append(elemento[1])
                
            print(proveedor)
            print(categoria)
            return render_template("añadirProducto.html",tipo=session['tipo'],tProveedor=proveedor,tCategoria=categoria)

@app.route('/añadirProveedor',methods=["GET","POST"])
def proveedores():
    error=None
    if 'idUsuario' in session and 'tipo' in session:
        if request.method=='POST':
            proveedor=request.form['nombre']
            idProveedor=int(datetime.today().strftime('%H%S%m%d'))+900
            dictDatos={'idProveedor':idProveedor,'proveedor':proveedor}
            bdEcommerce.insertar("proveedor",dictDatos)
            return redirect('/añadirProveedor')
        return render_template("añadirProveedor.html",tipo=session['tipo'])
    
@app.route('/añadirCategoria',methods=["GET","POST"])
def categorias():
    error=None
    if 'idUsuario' in session and 'tipo' in session:
        if request.method=='POST':
            categoria=request.form['nombre']
            idCategoria=int(datetime.today().strftime('%H%S%m%d'))+800
            dictDatos={'idCategoria':idCategoria,'categoria':categoria}
            bdEcommerce.insertar("catalogo",dictDatos)
            return redirect('/añadirCategoria')
        return render_template("añadirCategoria.html",tipo=session['tipo'])

@app.route('/carrito',methods=["GET","POST"])
def añadircarrito():
    error=None
    if 'idUsuario' in session and 'tipo' in session:
        userRow=bdEcommerce.buscarUnaLinea("clientes","idUsuario",session['idUsuario'])
        IdCliente=bdEcommerce.buscarUnaLinea("clientes","idUsuario",session['idUsuario'])[0][0]
        
        idcliente=bdEcommerce.buscarUnaLinea("clientes","idusuario",session['idUsuario'])[0][0]
        condicion="ca.idCliente='"+str(idcliente)+"' and ca.estado='En carrito'"
        cart=bdEcommerce.search("carrito"," ca join producto pr on ca.idproducto=pr.idproducto where ",condicion)
        
        sub=float()
        for producto in cart:
            sub+=float(producto[4])
            
        envio=10.0
        
        if request.method == 'POST':
            idCarrito=cart[0][0]
            sql = " where idCliente='"+str(IdCliente)+"' and idProducto="+request.form['idProducto']+" and idCarrito="+str(idCarrito)
            if request.form['submitButton']=='increase':
                cantidad=float(bdEcommerce.search("carrito","",sql)[0][3])+1
                subtotal = float(bdEcommerce.buscarUnaLinea("producto","idProducto",request.form['idProducto'])[0][4])*cantidad
                sql = "update carrito set cantidad = "+str(cantidad)+ ", subtotal = "+str(round(subtotal,2))+" where idCliente='"+str(IdCliente)+"' and idProducto="+request.form['idProducto']+" and idCarrito="+str(idCarrito)
                bdEcommerce.update(sql)
                return redirect('/carrito')
            if request.form['submitButton']=='decrease':
                cantidad=float(bdEcommerce.search("carrito","",sql)[0][3])-1
                subtotal = float(bdEcommerce.buscarUnaLinea("producto","idProducto",request.form['idProducto'])[0][4])*cantidad
                if cantidad == 0:
                    pass
                else:
                    sql = "update carrito set cantidad = "+str(cantidad)+ ", subtotal = "+str(round(subtotal,2))+" where idCliente='"+str(IdCliente)+"' and idProducto="+request.form['idProducto']+" and idCarrito="+str(idCarrito)
                    bdEcommerce.update(sql)
                return redirect('/carrito')
            if request.form['submitButton']=='delete':
                idProducto = request.form['idProducto']
                sql = "delete from carrito where idProducto="+idProducto+" and idCliente='"+idcliente+"'"
                bdEcommerce.delete(sql)
                return redirect('/carrito')
        
        return render_template("cart.html",carrito=cart,subTotal=str(round(sub,2)),shipping=str(envio),total=str(round((envio+sub),2)),user=userRow[0][2])
    return redirect('/login')

@app.route('/',methods=["GET","POST"])
def index():
    error=None
    productRow=bdEcommerce.buscar("producto")
    rowCate=bdEcommerce.buscar("catalogo")
    if 'idUsuario' in session and 'tipo' in session:
        if request.method=='POST':
            if request.form['submitButton']=="ver producto":
                print("ver producto")
                return redirect('/')
            if request.form['submitButton']=="añadir al carrito":
                
                nombre=request.form['nameProduct']
                idProducto=request.form['IdProduct']
                userRow=bdEcommerce.buscarUnaLinea("clientes","idUsuario",session['idUsuario'])
                carrito=bdEcommerce.buscarUnaLinea("carrito","idCliente",userRow[0][0])
                if len(carrito)>0:
                    idCarrito=bdEcommerce.buscarUnaLinea("carrito","idCliente",userRow[0][0])[0][0]
                else:
                    idCarrito=int(datetime.today().strftime('%H%S%m%d'))+9999
                
                IdCliente=bdEcommerce.buscarUnaLinea("clientes","idUsuario",session['idUsuario'])[0][0]
                cantidad=1
                subTotal=cantidad*float(request.form['price'])
                fecha=str(datetime.today().strftime('%Y-%m-%d'))
                print(idCarrito)
                print(subTotal)
                datos={
                    'idCarrito':idCarrito,
                    'idcliente':IdCliente,
                    'idProducto':idProducto,
                    'cantidad':cantidad,
                    'subtotal':subTotal,
                    'fechaagregado':fecha,
                    'estado':'En carrito'
                    
                }
                print(len(bdEcommerce.buscarUnaLinea("carrito","idCliente",userRow[0][0])))
                if len(bdEcommerce.buscarUnaLinea("carrito","idCliente",userRow[0][0])) > 1:
                    cantidad=float(bdEcommerce.buscarUnaLinea("carrito","idCliente",userRow[0][0])[0][3])+1
                    subtotal = float(bdEcommerce.buscarUnaLinea("producto","idProducto",request.form['IdProduct'])[0][4])*cantidad
                    sql = "update carrito set cantidad = "+str(cantidad)+ ", subtotal = "+str(round(subtotal,2))+" where idCliente='"+str(IdCliente)+"' and idProducto="+request.form['IdProduct']+" and idCarrito="+str(idCarrito)
                    bdEcommerce.update(sql)
                else:
                    bdEcommerce.insertar("carrito",datos)
                return redirect('/carrito')
        if session['tipo']=='Admin':
            return render_template('index.html',tipo=session['tipo'],categorias=rowCate,productos=productRow)
        else:
            row=bdEcommerce.buscarUnaLinea("clientes","idUsuario",session['idUsuario'])
            if len(row)>0:
                idcliente=bdEcommerce.buscarUnaLinea("clientes","idusuario",session['idUsuario'])[0][0]
                condicion="ca.idCliente='"+str(idcliente)+"' and ca.estado='En carrito'"
                cart=bdEcommerce.search("carrito"," ca join producto pr on ca.idproducto=pr.idproducto where ",condicion)
                return render_template('index.html',user=row[0][2],categorias=rowCate,numCart=len(cart),productos=productRow)
            else:
                return redirect('/checkout')
        
    return render_template('index.html',categorias=rowCate,productos=productRow)

@app.route('/actualizarDatosCliente',methods=['GET','POST'])
def actualizarDatosUsuario():
    error=None
    
    row=list()
    if (session['idUsuario']) and session['tipo']=='cliente':
        row=bdEcommerce.buscarUnaLinea("clientes","idUsuario",session['idUsuario'])[0]
        
    
        
    if request.method=='POST':
        if request.form['submitButton']=='check':
            idCliente= row[0]
            print(idCliente)
            nombre=request.form['nombre']
            apellidoP=request.form['apellidoP']
            apellidoM=request.form['apellidoM']
            telefono=request.form['telefono']
            pais=request.form.get('pais')
            estado=request.form['estado']
            ciudad=request.form['ciudad']
            colonia=request.form['colonia']
            codigoPostal=request.form['codigoPostal']
            direccion=request.form['direccion']
            update="update clientes set nombre='"+nombre+"', apellidop='"+apellidoP+"', apellidom='"+apellidoM+"', telefono='"+telefono+"', pais='"+pais+"', estado='"+estado+"', ciudad='"+ciudad+"', colonia='"+colonia+"', codigopostal="+codigoPostal+", direccion='"+direccion+"' where idcliente='"+idCliente+"'"
            bdEcommerce.update(update)
            return redirect('/')
        if request.form['submitButton']=='user':
            email=request.form['email']
            password=request.form['password']
            confirmPassword=request.form['confirmPassword']
            if email!="":
                sql = "update usuario set email='"+email+"' where idUsuario='"+session['idUsuario']+"'"
                bdEcommerce.update(sql)
            if password=="" and confirmPassword=="":
                pass
            if password!="":
                if confirmPassword!="":
                    sql = "update usuario set contraseña='"+password+"' where idUsuario='"+session['idUsuario']+"'"
                    bdEcommerce.update(sql)
                else:
                    return render_template("updateUserInfo.html",nombre=row[2],apellidoP=row[3],
                                apellidoM=row[4],telefono=row[5],estado=row[7],ciudad=row[8],
                                colonia=row[9],codigoPostal=row[10],direccion=row[11],
                                email=bdEcommerce.buscarUnaLinea("usuario","idUsuario",session['idUsuario'])[0][1], error="Las contraseñas no coinciden")
            return redirect('/')
    else:
        if session['idUsuario'] in row:
            return render_template("updateUserInfo.html",nombre=row[2],apellidoP=row[3],
                                apellidoM=row[4],telefono=row[5],estado=row[7],ciudad=row[8],
                                colonia=row[9],codigoPostal=row[10],direccion=row[11],
                                email=bdEcommerce.buscarUnaLinea("usuario","idUsuario",session['idUsuario'])[0][1])
    return redirect("/checkout")
    
@app.route('/logout')
def cerrar_sesion():
    if 'idUsuario' in session:
        session.pop('idUsuario', None)
        session.pop('email', None)
        return redirect('/')

@app.route('/checkout',methods=['GET','POST'])
def checkout():
    if 'email' in session:
        if request.method=='POST':
            idCliente=str(datetime.today().strftime('%d%m%H%S%M'))
            idUsuario=session['idUsuario']
            nombre=request.form['nombre']
            apellidoP=request.form['apellidoP']
            apellidoM=request.form['apellidoM']
            telefono=request.form['telefono']
            pais=request.form.get('pais')
            estado=request.form['estado']
            ciudad=request.form['ciudad']
            colonia=request.form['colonia']
            codigoPostal=int(request.form['codigoPostal'])
            direccion=request.form['direccion']
            fechaRegistro=str(datetime.today().strftime('%Y-%m-%d'))
            datos={
                'idCliente':idCliente,
                'idUsuario':idUsuario,
                'nombre':nombre,
                'apellidoP':apellidoP,
                'apellidoM':apellidoM,
                'telefono':telefono,
                'pais':pais,
                'estado':estado,
                'ciudad':ciudad,
                'colonia':colonia,
                'codigoPostal':codigoPostal,
                'direccion':direccion,
                'fechaRegistro':fechaRegistro
            }
            print(datos)
            row=bdEcommerce.buscarUnaLinea("usuario","idUsuario",idUsuario)
            if idUsuario in row[0]:
                bdEcommerce.insertar("clientes",datos)
                return redirect('/')
        else:
            return render_template('checkout.html',email=session['email'])
    return redirect('/login')

@app.route('/registro',methods=["GET","POST"])
def registro():
    error=None
    if request.method=='POST':
        idUsuario=str(datetime.today().strftime('%m%d%H%S%M'))
        email=request.form['correo']
        contraseña=request.form['password']
        confirmarContraseña=request.form['ConfirmPassword']
        # Verificar si existe el email
        row=bdEcommerce.buscarUnaLinea("usuario","email",email)
        if len(row)>0:
            return render_template('registro.html',error="El correo electronico ya existe.")
        if contraseña!=confirmarContraseña:
            return render_template('registro.html', error="Las contraseñas no coinciden")
        else:
            session['idUsuario']=idUsuario
            session['email']=email
            dicUsiario={'idUsuario':idUsuario,'email':email,'contraseña':contraseña,'tipo':'cliente'}
            bdEcommerce.insertar('usuario',dicUsiario)
            return redirect('/checkout')
    else:
        return render_template('registro.html')

@app.route('/login',methods=["GET","POST"])
def login():
    error=None
    if request.method == 'POST':
        email=request.form['correo']
        password=request.form['password']
        
        row=bdEcommerce.buscarUnaLinea("usuario","email",email)
        
        if email=="" or password=="":
            return render_template('login.html',error="Ingresa un correo y/o una contraseña")
        if len(row)==0:
            return render_template('login.html',error="Correo invalido")
        if (email in row[0]):
            if (password == row[0][2]):
                session['email']=email
                session['idUsuario']=row[0][0]
                session['tipo']=row[0][3]
                return redirect('/')
            else:
                return render_template('login.html',error="Correo o contraseña incorrectos")     
        else:
            return render_template('login.html',error="Correo o contraseña incorrectos")
    return render_template('login.html')