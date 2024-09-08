from flask import Flask,render_template,request,redirect,session,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date

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
    s_id=db.Column(db.Integer(),db.ForeignKey("service.s_id"),nullable=False)
    date_of_req=db.Column(db.String(),nullable=False)
    date_of_com=db.Column(db.String())
    status=db.Column(db.String())
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
                session["id"]=cust.cust_id
                return redirect("/customer")
            else:
                return render_template("login.html",msg="Invalid Credentials")
        elif prof:
            if prof.ppassword==password:
                session["username"]=prof.pemail
                session["password"]=prof.ppassword
                session["id"]=prof.prof_id
                return redirect("/professional")
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
        serv_req=(db.session.query(Customer,Service_request,Professionals)
                 .join(Service_request, Customer.cust_id == Service_request.cust_id)
                 .join(Professionals, Professionals.prof_id == Service_request.prof_id)
                 .join(Service, Service.s_id == Service_request.s_id).all())  
        return render_template("admin.html",cust=cust,prof=prof,service=service,serv_req=serv_req)
    else:
        return redirect("/login")
    
@app.route("/customer")
def customer():
    #servType=Service.query.distinct(Service.pServiceType).all()
    servType = db.session.query(Service.pServiceType).distinct().all()
    # custHistory=(db.session.query(Professionals, Service_request, Service).select_from(Service_request)
    #              .join(Service_request, Customer.cust_id == Service_request.cust_id)
    #              .join(Service, Service.s_id == Service_request.s_id)
    #              .filter(Service_request.prof_id == Professionals.prof_id)  # Avoid extra join with Professionals
    #              .filter(Customer.cust_id == session["id"])
    #              .all()) 
    custHistory = (db.session.query(Professionals, Service_request, Service)
                .join(Service_request, Service_request.prof_id == Professionals.prof_id)
                .join(Service, Service.s_id == Service_request.s_id)
                .filter(Service_request.cust_id == session["id"])
                .all())
    return render_template("customer.html",servType=servType,custHistory=custHistory)

@app.route("/professional")
def professional():
    cust_detail_today = (db.session.query(Customer)
                 .join(Service_request, Customer.cust_id == Service_request.cust_id)
                 .join(Professionals, Professionals.prof_id == Service_request.prof_id)
                 .filter(Service_request.prof_id == session["id"]).filter(Service_request.date_of_req == date.today())
                 .all())
    cust_detail_prev = (db.session.query(Customer,Service_request)
                 .join(Service_request, Customer.cust_id == Service_request.cust_id)
                 .join(Professionals, Professionals.prof_id == Service_request.prof_id)
                 .join(Service, Service.s_id == Service_request.s_id)
                 .filter(Service_request.prof_id == session["id"]).filter(Service_request.date_of_req != date.today())
                 .all())    
    return render_template("professionals.html",cust_detail_today=cust_detail_today,cust_detail_prev=cust_detail_prev)
#create customer phone number
#create service rating
#create profession phone no
@app.route("/customer_serviceType/<serviceName>")
def customer_service(serviceName):
    #subServices = Service.query.filter_by(pServiceType=serviceName).distinct(Service.sname).all()
    subServices = (db.session.query(Service).filter_by(pServiceType=serviceName).group_by(Service.sname).all())
    return render_template("customer2.html",subServices=subServices,serviceName=serviceName)

@app.route("/customer_subService/<subService_title>")
def customer_subService(subService_title):
    if session["id"]:
        subServices = (db.session.query(Professionals).filter_by(pserviceName=subService_title).all())
        if len(subServices)>0:
            return render_template("customer3.html",subServices=subServices,subService_title=subService_title)
        else:
            backService = (db.session.query(Service).filter_by(sname=subService_title).one())
            flash("Sorry,no "+subService_title+" pakages available at this point of time.You can try some other pakages.Sorry for the inconvinence")
            return redirect(url_for('customer_service', serviceName=backService.pServiceType))
    else:
        return redirect("/login")
    
@app.route("/book_service/<prof_id>/<subService_title>")
def book_service(prof_id,subService_title):
    # service_id = (db.session.query(Professionals, Service).join(Service, Professionals.pserviceName == Service.sname).filter(Professionals.pserviceName == subService_title)
    # .first())
    service_id = (db.session.query(Service.s_id)
              .join(Professionals, Professionals.pserviceName == Service.sname)
              .filter(Professionals.pserviceName == subService_title)
              .first())

    print(service_id[0])

    s1=Service_request(cust_id=session["id"],prof_id=int(prof_id),s_id=service_id[0],date_of_req=date.today())
    db.session.add(s1)
    db.session.commit()
    flash("Your Service has been booked successfully")
    return redirect("/customer")

@app.route("/customer_signUp",methods=['GET','POST'])
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
        allServices=db.session.query(Service)
        return render_template("profsignUp.html",allServices=allServices)

@app.route("/new_service",methods=["GET","POST"])
def new_service():
    if session["username"]=="admin":
        if request.method=="POST":
            serviceName=(request.form.get("servName")).strip()
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
    
@app.route("/deleteService/<int:id>")
def deleteService(id):
    if session["username"]=="admin":
        delService=Service.query.filter_by(s_id=id).first()
        db.session.delete(delService)
        db.session.commit()
        return redirect("/admin")
    else:
        redirect("/login")

@app.route("/deleteProf/<int:id>")
def deleteProfessional(id):
    if session["username"]=="admin":
        delProf=Professionals.query.filter_by(prof_id=id).first()
        db.session.delete(delProf)
        db.session.commit()
        return redirect("/admin")
    else:
        redirect("/login")

@app.route("/logout")
def logout():
    session["username"]=None
    session["password"]=None
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)