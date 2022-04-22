from flask import Flask, render_template, request, session
from flask.templating import render_template_string
from numpy import empty
from werkzeug.utils import redirect
from datetime import datetime
import secrets
import bd,sys
import json


bdEcommerce=bd.datos()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/shop',methods=["GET","POST"])
def tienda():
    return render_template('shop.html')

@app.route('/añadiralcarrito',methods=["GET","POST"])
def añadircarrito():
    print(request.form.get('p1'))
    return redirect('/')

@app.route('/')
def index():
    error=None
    if 'idUsuario' in session and 'tipo' in session:
        if session['tipo']=='Admin':
            return render_template('index.html',tipo=session['tipo'])
        else:
            row=bdEcommerce.buscarUnaLinea("clientes","idUsuario",session['idUsuario'])
            return render_template('index.html',user=row[0][2])
    return render_template('index.html')

@app.route('/actualizarDatosCliente',methods=['GET','POST'])
def actualizarDatosUsuario():
    error=None
    
    row=list()
    if (session['idUsuario']) and session['tipo']=='cliente':
        row=bdEcommerce.buscarUnaLinea("clientes","idUsuario",session['idUsuario'])[0]
    
        
    if request.method=='POST':
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
        print(email)
        print(password)
        row=bdEcommerce.buscarUnaLinea("usuario","email",email)
        print(row[0])
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