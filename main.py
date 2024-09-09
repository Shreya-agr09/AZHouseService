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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        # Admin login (assuming admin credentials are hard-coded)
        if username == "admin":
            if password == "123456":
                session["username"] = "admin"
                session["password"] = "123456"
                session["role"]="admin"
                return redirect("/admin")
            else:
                return render_template("login.html", msg="Enter valid Username or Password")  
        
        elif role == 'customer':
            cust = Customer.query.filter_by(cemail=username).first()
            if cust:
                if cust.cpassword == password:
                    session["username"] = cust.cemail
                    session["password"] = cust.cpassword
                    session["id"] = cust.cust_id
                    session["role"]="customer"
                    return redirect("/customer")
                else:
                    return render_template("login.html", msg="Invalid Credentials")
            else:
                return render_template("login.html", msg="Invalid Username")

        elif role == 'professional':
            prof = Professionals.query.filter_by(pemail=username).first()
            if prof:
                if prof.ppassword == password:
                    session["username"] = prof.pemail
                    session["password"] = prof.ppassword
                    session["id"] = prof.prof_id
                    session["role"] = "professional"
                    return redirect("/professional")
                else:
                    return render_template("login.html", msg="Invalid Credentials")
            else:
                return render_template("login.html", msg="Invalid Username")
                
        else :
            return render_template("login.html", msg="Enter valid Username or Password")       
                     
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
    servType = db.session.query(Service.pServiceType).distinct().all()
    custHistory = (db.session.query(Professionals, Service_request, Service)
                .join(Service_request, Service_request.prof_id == Professionals.prof_id)
                .join(Service, Service.s_id == Service_request.s_id)
                .filter(Service_request.cust_id == session["id"])
                .all())
    return render_template("customer.html",servType=servType,custHistory=custHistory)

@app.route("/closeService/<ser_reqId>",methods=['GET','POST'])
def closeService(ser_reqId):
    if session["role"]=="customer":
        if request.method=="POST":
            rating = request.form.get('rating')
            date_of_com=date.today()
            remarks=request.form.get('remarks')
            s=Service_request.query.filter_by(sr_id=ser_reqId).one()
            s.status="Closed"
            s.remarks=remarks
            s.date_of_com=date_of_com
            db.session.commit()
            return redirect("/customer")
        else:
            results = (db.session.query(Service_request, Service, Professionals).join(Service, Service_request.s_id == Service.s_id).join(Professionals, Service_request.prof_id == Professionals.prof_id).join(Customer,Service_request.cust_id == Customer.cust_id).filter(Service_request.sr_id==ser_reqId).all())
            print(results)
            dt=date.today()
            return render_template("csremark.html",results=results,dt=dt)
    else:
        return redirect("/login")


@app.route("/profRejectService/<serviceRq_id>")
def profRejectService(serviceRq_id):
    s1=Service_request.query.filter_by(sr_id=serviceRq_id).one()
    s1.status="Rejected"
    db.session.commit()
    return redirect("/professional")


@app.route("/deleteProfProfile")
def deleteProfProfile():
    if session["id"] and session["role"]=="professional":
        check = (db.session.query(Service_request, Professionals).join(Professionals, Service_request.prof_id == Professionals.prof_id).filter(Service_request.status=="Accepted" or Service_request.status=="Requested").all())
        if not check:
            p1 = Professionals.query.filter_by(prof_id=session["id"]).first()
            if p1:
                db.session.delete(p1)
                db.session.commit()
                return redirect("/login")
            else:
                flash("Professional not found.")
                return redirect("/prof_profile")
        else:
            flash("Sorry,you cannot delete your account until all requests are either closed or rejected")
            return redirect("/prof_profile")
    else:
        return redirect("/login")
    
@app.route("/deleteCustProfile")
def deleteCustProfile():
    if session["id"] and session["role"]=="customer":
        check = (db.session.query(Service_request, Customer).join(Customer, Service_request.cust_id == Customer.cust_id).filter(Service_request.status=="Accepted").all())
        if not check:
            c1=Customer.query.filter_by(cust_id=session["id"]).first()
            db.session.delete(c1)
            db.session.commit()
            return redirect("/login")
        else:
            flash("Sorry,you cannot delete your account until all requests are Closed")
            return redirect("/cust_profile")
    else:
        return redirect("/login")

# @app.route("/updateProfProfile/<id>",methods=["GET","POST"])
def updateProfProfile(id):
    if request.method=="POST":
        pemail=request.form.get("cemail")
        c=Professionals.query.filter_by(pemail=pemail).all()
        if pemail.find("@")!=-1:
            if not len(c):
                pname=request.form.get("cname")
                pserviceName=request.form.get("serviceName")
                pexp=request.form.get("exp")
                paddress=request.form.get("caddress")
                ppincode=request.form.get("cpincode")
                p=Professionals.query.filter_by(prof_id=id).one()
            else:
                flash("Username already taken")
                return redirect("/professional_signUp")
        else:
            flash("Please use valid email id")
            return redirect("/professional_signUp")
    else:
        p=Professionals.query.filter_by(prof_id=id).one()
        return render_template("updateProfProfile.html",p=p)

@app.route("/prof_profile")
def prof_profile():
    if session["id"] and session["role"]=="professional":
        profDetails=Professionals.query.filter_by(prof_id=session["id"]).one()
        category=Service.query.filter_by(sname=profDetails.pserviceName).one()
        return render_template("prof_profile.html",p=profDetails,category=category)
    else:
        return redirect("/login")

@app.route("/cust_profile")
def cust_profile():
    if session["id"] and session["role"]=="customer":
        custDetails=Customer.query.filter_by(cust_id=session["id"]).one()
        return render_template("custprofile.html",c=custDetails)
    else:
        return redirect("/login")

@app.route("/professional")
def professional():
    cust_detail_today = (db.session.query(Customer,Service_request)
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
#profession rating 
#create profession phone no
#service request status default requested
#status can take : Accepted,Rejected,Requested,Closed
@app.route("/profAcceptService/<serviceRq_id>")
def profAcceptService(serviceRq_id):
    s1=Service_request.query.filter_by(sr_id=serviceRq_id).one()
    s1.status="Accepted"
    db.session.commit()
    return redirect("/professional")

@app.route("/customer_serviceType/<serviceName>")
def customer_service(serviceName):
    if session["role"]=="customer":
        subServices = (db.session.query(Service).filter_by(pServiceType=serviceName).group_by(Service.sname).all())
        #retieving history of customer 
        custHistory = (db.session.query(Professionals, Service_request, Service)
                    .join(Service_request, Service_request.prof_id == Professionals.prof_id)
                    .join(Service, Service.s_id == Service_request.s_id)
                    .filter(Service_request.cust_id == session["id"])
                    .all())
        return render_template("customer2.html",subServices=subServices,serviceName=serviceName,custHistory=custHistory)
    else:
        return redirect("/login")

@app.route("/customer_subService/<subService_title>")
def customer_subService(subService_title):
    if session["id"] and session["role"]=="customer":
        subServices = (db.session.query(Professionals).filter_by(pserviceName=subService_title).all())
        custHistory = (db.session.query(Professionals, Service_request, Service)
                .join(Service_request, Service_request.prof_id == Professionals.prof_id)
                .join(Service, Service.s_id == Service_request.s_id)
                .filter(Service_request.cust_id == session["id"])
                .all())
        if len(subServices)>0:
            return render_template("customer3.html",subServices=subServices,subService_title=subService_title,custHistory=custHistory)
        else:
            backService = (db.session.query(Service).filter_by(sname=subService_title).one())
            flash("Sorry,no "+subService_title+" pakages available at this point of time.You can try some other pakages.Sorry for the inconvinence")
            return redirect(url_for('customer_service', serviceName=backService.pServiceType))
    else:
        return redirect("/login")
    
@app.route("/book_service/<prof_id>/<subService_title>")
def book_service(prof_id,subService_title):
    if session["role"]=="customer":
        service_id = (db.session.query(Service.s_id)
                .join(Professionals, Professionals.pserviceName == Service.sname)
                .filter(Professionals.pserviceName == subService_title)
                .first())
        s1=Service_request(cust_id=session["id"],prof_id=int(prof_id),s_id=service_id[0],date_of_req=date.today(),status="Requested")
        db.session.add(s1)
        db.session.commit()
        flash("Your Service has been booked successfully")
        return redirect("/customer")
    else:
        return redirect("/login")

@app.route("/update_service/<serviceId>",methods=["GET","POST"])
def editService(serviceId):
    if request.method=="POST":
        up_sdesc=request.form.get("sdesc")
        up_baseprice=request.form.get("baseprice")
        up_time=request.form.get("timereq")
        up_servtype=request.form.get("servtype")
        s1=Service.query.filter_by(s_id=serviceId).one()
        s1.sbaseprice=up_baseprice
        s1.servType=up_servtype
        s1.stime_req=up_time
        s1.sdescription=up_sdesc
        db.session.commit()
        return redirect("/admin")
    else:
        s=Service.query.filter_by(s_id=serviceId).one()
        return render_template("serviceEdit.html",s=s)
    pass
@app.route("/customer_signUp",methods=['GET','POST'])
def customer_signUp():
    if request.method=="POST":
        cemail=request.form.get("cemail")
        c=Customer.query.filter_by(cemail=cemail).all()
        if cemail.find("@")!=-1 and not len(c):
            cpassword=request.form.get("cpassword")
            cname=request.form.get("cname")
            caddress=request.form.get("caddress")
            cpincode=request.form.get("cpincode")
            c1=Customer(cemail=cemail,cpassword=cpassword,cname=cname,caddress=caddress,cpincode=cpincode)
            db.session.add(c1)
            db.session.commit()
            return redirect("/login")
        else:
            flash("Please select another username")
            return redirect("/customer_signUp")
    else:
        return render_template("csignup.html")
    
@app.route('/professional_signUp',methods=['GET','POST'])
def professional_signUp():
    if request.method=="POST":
        pemail=request.form.get("cemail")
        c=Professionals.query.filter_by(pemail=pemail).all()
        if pemail.find("@")!=-1:
            if not len(c):
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
                flash("Username already taken")
                return redirect("/professional_signUp")
        else:
            flash("Please use valid email id")
            return redirect("/professional_signUp")
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
    session["id"]=None
    session["role"]=None
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)