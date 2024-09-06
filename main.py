from flask import Flask,render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
#creating flask app
app=Flask(__name__)
app.secret_key="7uhu987u98uiufrge5@3*(*4"
#creating datbase called samplebd in the root directory(same folder)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///database.sqlite3"

#creating flask connection with sqlachemy
db=SQLAlchemy(app)
app.app_context().push()

#creating models 
class Customer(db.Model):
    cust_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    #cusername=db.Column(db.String(),unique=True,nullable=False)
    cemail=db.Column(db.String(),unique=True,nullable=False)
    cpassword=db.Column(db.String(),nullable=False)
    cname=db.Column(db.String(),nullable=False)
    caddress=db.Column(db.String(),nullable=False)
    cpincode=db.Column(db.String(),nullable=False)

class Professionals(db.Model):
    prof_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    #pusername=db.Column(db.String(),unique=True,nullable=False)
    pemail=db.Column(db.String(),unique=True,nullable=False)
    ppassword=db.Column(db.String(),nullable=False)
    pname=db.Column(db.String(),nullable=False)
    pserviceName=db.Column(db.String(),nullable=False)
    pexp=db.Column(db.Integer(),nullable=False)
    pdoc=db.Column(db.PickleType())
    paddress=db.Column(db.String(),nullable=False)
    ppincode=db.Column(db.String(),nullable=False)

class Service(db.Model):
    s_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    sname=db.Column(db.String(),unique=True,nullable=False)
    #psDateCreated=db.Column(db.String(),unique=True,nullable=False)
    #ps_exp=db.Column(db.String(),nullable=False)
    stime_req=db.Column(db.String())
    sbaseprice=db.Column(db.Integer())
    sdescription=db.Column(db.String(),nullable=False)
    pServiceType=db.Column(db.String(),nullable=False)

class Service_request(db.Model):
    sr_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    cust_id=db.Column(db.Integer(),db.ForeignKey("customer.cust_id"),nullable=False)
    prof_id=db.Column(db.Integer(),db.ForeignKey("professionals.prof_id"),nullable=False)
    ps_id_id=db.Column(db.Integer(),db.ForeignKey("service.s_id"),nullable=False)
    date_of_req=db.Column(db.String(),nullable=False)
    date_of_com=db.Column(db.String(),nullable=False)
    status=db.Column(db.String(),nullable=False)
    remarks=db.Column(db.String())

#initializing model
db.create_all()

#rendering all templates 

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get("username")
        password=request.form.get("password")
        cust=Customer.query.filter_by(cemail=username).first()
        prof=Professionals.query.filter_by(pemail=username).first()
        # what if a person has registered as both cust and prof with same username
        if username=="admin" and password=="123456":
            session["username"]="admin"
            session["password"]="123456"
            return redirect("/admin")
        elif cust:
            if cust.cpassword==password:
                session["username"]=cust.cemail
                session["password"]=cust.cpassword
                return render_template("customer.html")
            else:
                return render_template("login.html",msg="Invalid Credentials")
        elif prof:
            if prof.ppassword==password:
                session["username"]=prof.pemail
                session["password"]=prof.ppassword
                return render_template("professionals.html")
            else:
                return render_template("login.html",msg="Invalid Credentials")  
        else:
            return render_template("login.html",msg="Enter valid Username")       
                     
    else:
        return render_template("login.html")

@app.route("/admin")
def admin():
    if session["username"]=="admin":
        prof=Professionals.query.all()
        cust=Customer.query.all()
        service=Service.query.all()
        return render_template("admin.html",cust=cust,prof=prof,service=service)
    else:
        return redirect("/login")

@app.route('/customer_signUp',methods=['GET','POST'])
def customer_signUp():
    if request.method=="POST":
        cemail=request.form.get("cemail")
        cpassword=request.form.get("cpassword")
        cname=request.form.get("cname")
        caddress=request.form.get("caddress")
        cpincode=request.form.get("cpincode")
        c1=Customer(cemail=cemail,cpassword=cpassword,cname=cname,caddress=caddress,cpincode=cpincode)
        db.session.add(c1)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template("csignup.html")
    
@app.route('/professional_signUp',methods=['GET','POST'])
def professional_signUp():
    if request.method=="POST":
        pemail=request.form.get("cemail")
        ppassword=request.form.get("cpassword")
        pname=request.form.get("cname")
        pserviceName=request.form.get("serviceName")
        pexp=request.form.get("exp")
        paddress=request.form.get("caddress")
        ppincode=request.form.get("cpincode")
        p1=Professionals(pemail=pemail,ppassword=ppassword,pname=pname,pserviceName=pserviceName,pexp=pexp,paddress=paddress,ppincode=ppincode)
        db.session.add(p1)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template("profsignUp.html")

@app.route("/new_service",methods=["GET","POST"])
def new_service():
    if session["username"]=="admin":
        if request.method=="POST":
            serviceName=request.form.get("servName")
            sdesc=request.form.get("sdesc")
            baseprice=request.form.get("baseprice")
            time=request.form.get("timereq")
            servtype=request.form.get("servtype")
            s1=Service(sname=serviceName,stime_req=time,sbaseprice=baseprice,sdescription=sdesc,pServiceType=servtype)
            db.session.add(s1)
            db.session.commit()
            return redirect("/admin")
        else:
            return render_template("newService.html")
    else:
        return redirect("/login")
    
@app.route("/logout")
def logout():
    session["username"]=None
    session["password"]=None
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)