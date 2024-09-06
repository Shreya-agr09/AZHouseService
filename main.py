from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
#creating flask app
app=Flask(__name__)

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

class Prof_service(db.Model):
    ps_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    psname=db.Column(db.String(),unique=True,nullable=False)
    psDateCreated=db.Column(db.String(),unique=True,nullable=False)
    ps_exp=db.Column(db.String(),nullable=False)
    psdescription=db.Column(db.String(),nullable=False)
    psServiceType=db.Column(db.String(),nullable=False)

class Service_request(db.Model):
    sr_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    cust_id=db.Column(db.Integer(),db.ForeignKey("customer.cust_id"),nullable=False)
    prof_id=db.Column(db.Integer(),db.ForeignKey("professionals.prof_id"),nullable=False)
    ps_id_id=db.Column(db.Integer(),db.ForeignKey("prof_service.ps_id"),nullable=False)
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
            return render_template("admin.html")  
        elif cust:
            if cust.cpassword==password:
                return render_template("customer.html")
            else:
                return render_template("login.html",msg="Invalid Credentials")
        elif prof:
            if prof.ppassword==password:
                return render_template("professionals.html")
            else:
                return render_template("login.html",msg="Invalid Credentials")  
        else:
            return render_template("login.html",msg="Enter valid Username")       
                     
    else:
        return render_template("login.html")
    
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
        p1=Customer(pemail=pemail,ppassword=ppassword,pname=pname,pserviceName=pserviceName,pexp=pexp,paddress=paddress,ppincode=ppincode)
        db.session.add(p1)
        db.session.commit()
    else:
        return render_template("profsignUp.html")
if __name__=="__main__":
    app.run(debug=True)