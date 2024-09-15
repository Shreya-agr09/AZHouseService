from flask import Flask,render_template,request,redirect,session,flash,url_for,send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy import or_
from sqlalchemy import func
from io import BytesIO
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

#creating flask app
app=Flask(__name__)
app.secret_key="7uhu987u98uiufrge5@3*(*4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    cphoneNo=db.Column(db.String(),nullable=False)
    is_allowed=db.Column(db.String(),nullable=False)
    service_requests = db.relationship('Service_request', backref='customer')

class Professionals(db.Model):
    prof_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    #pusername=db.Column(db.String(),unique=True,nullable=False)
    pemail=db.Column(db.String(),unique=True,nullable=False)
    ppassword=db.Column(db.String(),nullable=False)
    pname=db.Column(db.String(),nullable=False)
    pserviceName=db.Column(db.String(),nullable=False)
    pexp=db.Column(db.Integer(),nullable=False)
    pdocData=db.Column(db.LargeBinary)
    pdocFilename=db.Column(db.String(50))
    paddress=db.Column(db.String(),nullable=False)
    pphoneNo=db.Column(db.String(),nullable=False)
    ppincode=db.Column(db.String(),nullable=False)
    is_approved=db.Column(db.String(),nullable=False)
    price=db.Column(db.Integer(),nullable=False)
    service_requests = db.relationship('Service_request', backref='professional')

class Service(db.Model):
    s_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    sname=db.Column(db.String(),unique=True,nullable=False)
    #psDateCreated=db.Column(db.String(),unique=True,nullable=False)
    #ps_exp=db.Column(db.String(),nullable=False)
    stime_req=db.Column(db.String())
    sbaseprice=db.Column(db.Integer())
    sdescription=db.Column(db.String(),nullable=False)
    pServiceType=db.Column(db.String(),nullable=False)
    service_requests = db.relationship('Service_request', backref='service')

class Service_request(db.Model):
    sr_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    cust_id=db.Column(db.Integer(),db.ForeignKey("customer.cust_id"),nullable=False)
    prof_id=db.Column(db.Integer(),db.ForeignKey("professionals.prof_id"),nullable=False)
    s_id=db.Column(db.Integer(),db.ForeignKey("service.s_id"),nullable=False)
    price=db.Column(db.Integer(),nullable=False)
    date_of_req=db.Column(db.String(),nullable=False)
    cpay=db.Column(db.Boolean(),nullable=False)
    ppay=db.Column(db.Boolean(),nullable=False)
    date_of_com=db.Column(db.String())
    srating=db.Column(db.Integer())
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
                if cust.is_allowed=="Allowed":
                    if cust.cpassword == password:
                        session["username"] = cust.cemail
                        session["password"] = cust.cpassword
                        session["id"] = cust.cust_id
                        session["role"]="customer"
                        return redirect("/customer")
                    else:
                        return render_template("login.html", msg="Invalid Credentials")
                else:
                    flash("You are blocked by the author or you have deleted your account")
                    return redirect("/login")
            else:
                return render_template("login.html", msg="Invalid Username")

        elif role == 'professional':
            prof = Professionals.query.filter_by(pemail=username).first()
            if prof:
                    if prof.is_approved=="Accepted":
                        if prof.ppassword == password:
                            session["username"] = prof.pemail
                            session["password"] = prof.ppassword
                            session["id"] = prof.prof_id
                            session["role"] = "professional"
                            return redirect("/professional")
                        else:
                            return render_template("login.html", msg="Invalid Credentials")
                    else:
                        flash("either you acc has been rejected or blocked or you deleted your account")
                        return redirect("/login")
            else:
                return render_template("login.html", msg="Invalid Username")
                
        else :
            return render_template("login.html", msg="Enter valid Username or Password")       
                     
    else:
        return render_template("login.html")
#===============================Admin================================================================================
@app.route("/admin")
def admin():
    if "role" in session and session["role"]=="admin":
        prof=Professionals.query.filter(or_(Professionals.is_approved == "Waiting", 
                                              Professionals.is_approved == "Accepted")).all()
        cust=Customer.query.filter(Customer.is_allowed=="Allowed").all()
        service=Service.query.all()
        serv_req=(db.session.query(Customer,Service_request,Professionals)
                 .join(Service_request, Customer.cust_id == Service_request.cust_id)
                 .join(Professionals, Professionals.prof_id == Service_request.prof_id)
                 .join(Service, Service.s_id == Service_request.s_id).all())  
        return render_template("admin.html",cust=cust,prof=prof,service=service,serv_req=serv_req)
    else:
        return redirect("/login")
    
#------------------Admin Service---------------------------------------------------
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

@app.route('/admin_search', methods=['GET','POST'])
def admin_search():
    if request.method=="POST":
        search_by = request.form.get('search_by')
        search_text = request.form.get('search_text')
        if search_by == 'service_request':
            # Search in the service request table, including multiple fields
            search_results = (db.session.query(Service_request)
                            .filter(or_(
                                Service_request.status.ilike(f'%{search_text}%'),
                                Service_request.srating.ilike(f'%{search_text}%'),
                                Service_request.date_of_req.ilike(f'%{search_text}%')
                            )).all())
        elif search_by == 'customers':
            # Search customers by name, email, or address
            search_results = (db.session.query(Customer)
                            .filter(or_(
                                Customer.cname.ilike(f'%{search_text}%'),
                                Customer.cemail.ilike(f'%{search_text}%'),
                                Customer.caddress.ilike(f'%{search_text}%'),
                                Customer.cemail.ilike(f'%{search_text}%'),
                                Customer.cphoneNo.ilike(f'%{search_text}%'),
                                Customer.cpincode.ilike(f'%{search_text}%')
                            )).all())
        elif search_by == 'professionals':
            # Search professionals by name, service, or experience
            search_results = (db.session.query(Professionals)
                            .filter(or_(
                                Professionals.pname.ilike(f'%{search_text}%'),
                                Professionals.pserviceName.ilike(f'%{search_text}%'),
                                Professionals.pexp.ilike(f'%{search_text}%'),
                                Professionals.pemail.ilike(f'%{search_text}%'),
                                Professionals.pphoneNo.ilike(f'%{search_text}%'),
                                Professionals.paddress.ilike(f'%{search_text}%'),
                                Professionals.ppincode.ilike(f'%{search_text}%'),
                                Professionals.is_approved.ilike(f'%{search_text}%')
                            )).all())
        elif search_by == 'service':
            # Search professionals by name, service, or experience
            search_results = (db.session.query(Service)
                            .filter(or_(
                                Service.sname.ilike(f'%{search_text}%'),
                                Service.stime_req.ilike(f'%{search_text}%'),
                                Service.sbaseprice.ilike(f'%{search_text}%'),
                                Service.sdescription.ilike(f'%{search_text}%'),
                                Service.pServiceType.ilike(f'%{search_text}%')
                            )).all())
        else:
            search_results = []

        return render_template('adminSearch.html', search_results=search_results, search_by=search_by,search_text=search_text)
    else:
        return render_template("adminSearch.html")

@app.route("/admin_summary")
def admin_summary():
    data = db.session.query(Service_request.status,func.count(Service_request.status).label('count')).group_by(Service_request.status).all()
    service_status,service_count=[],[]
    for status,count in data:
        service_status.append(status)
        service_count.append(count)
    print(service_status,service_count)
    plt.bar(service_status, service_count, color=['#66b3ff', '#99ff99', '#ff9999','#7ec3bf'])
    plt.title('Service Requests Summary')
    plt.ylabel('Number of Requests')
    plt.savefig('service_requests_summary.png')
    plt.clf()
   
    #making rating wise plot graph
    #ratingdata = db.session.query(Service_request.srating,func.count(Service_request.srating).label('count')).group_by#(Service_request.srating).all()
    ratingdata = db.session.query(Service_request.srating).all()
    # rating,count=[],[]
    # for id,count in ratingdata:
    #     rating.append(id)
    #     count.append(count)
    pos=0
    neg=0
    for i in ratingdata:
        print(i)
        if i[0]>3:
            pos+=1
        else:
            neg+=1
    ratings=[pos/len(ratingdata),neg/len(ratingdata),100-pos/len(ratingdata)-neg/len(ratingdata)]


    labels = ['Positive', 'Negative','Not given yet']
    plt.pie(ratings, labels=labels, autopct='%1.1f%%', startangle=90)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    plt.gca().add_artist(centre_circle)
    plt.title('Overall Customer Ratings')
    
    plt.savefig('customer_ratings_summary.png')
    plt.clf()

    #making dataewise plots
    datedata = db.session.query(Service_request.date_of_req,func.count(Service_request.date_of_req).label('count')).group_by(Service_request.date_of_req).all()
    date_d,prof_count=[],[]
    for id,count in datedata:
        date_d.append(id)
        prof_count.append(count)
    print(date_d,prof_count)
    plt.bar(date_d, prof_count, color=['#66b3ff', '#99ff99', '#ff9999','#7ec3bf'])
    plt.title('Professionals no. of order')
    plt.ylabel('Number of Orders')
    plt.xlabel('Date')
    plt.savefig('date_analysis.png')
    plt.clf()


    #making professional wise graph
    profdata = db.session.query(Professionals.pemail,func.count(Service_request.prof_id).label('count')).join(Service_request, Professionals.prof_id == Service_request.prof_id).group_by(Professionals.pemail).all()
    prof_id,prof_count=[],[]
    for id,count in profdata:
        prof_id.append(id)
        prof_count.append(int(count))
    print(prof_id,prof_count)
    plt.bar(prof_id, prof_count, color=['#66b3ff', '#99ff99', '#ff9999','#7ec3bf'])
    plt.title('Professionals no. of order')
    plt.ylabel('Number of Orders')
    plt.xlabel('ID of Professional')
    plt.savefig('prof_analysis.png')
    plt.clf()

    return "your image is saved successfully"

@app.route("/admin_viewProfile/<role>/<id>")
def admin_viewProfile(role,id):
    if session["role"]=="admin":
        if role=="Professional":
            profDetails = Professionals.query.filter_by(prof_id=id).one()
            profReviews = Service_request.query.filter_by(prof_id=id).filter(Service_request.srating.isnot(None)).all()
            return render_template("admin_viewProfile.html",role="Professional",details=profDetails,reviews=profReviews)
        elif role=="Customer":
            custDetails = Customer.query.filter_by(cust_id=id).one()
            return render_template("admin_viewProfile.html",role="Customer",details=custDetails)
        elif role=="Service":
            serviceDetails = Service.query.filter_by(s_id=id).one()
            return render_template("admin_viewProfile.html",role="Service",details=serviceDetails)
        else:
            return redirect("/admin")
    else:
        return redirect("/login")

@app.route("/rejectProfessional/<id>")
def rejectProfessional(id):
    query=Professionals.query.filter_by(prof_id=id).first()
    query.is_approved="Rejected"
    db.session.commit()
    return redirect("/admin")

@app.route("/deleteProf/<id>")
def deleteProf(id):
    query=Professionals.query.filter_by(prof_id=id).first()
    query.is_approved="Deleted"
    db.session.commit()
    return redirect("/admin")

@app.route("/deleteCust/<id>")
def deleteCust(id):
    query=Customer.query.filter_by(cust_id=id).first()
    query.is_allowed="Blocked"
    db.session.commit()
    return redirect("/admin")

@app.route("/viewblockedCust")
def viewblockedCust():
    blockedCust=Customer.query.filter(Customer.is_allowed=="Blocked")
    return render_template("blockedProf.html",blockedCust=blockedCust,role="customer")

@app.route("/acceptProfessional/<id>")
def acceptProfessional(id):
    query=Professionals.query.filter_by(prof_id=id).first()
    query.is_approved="Accepted"
    db.session.commit()
    return redirect("/admin")

@app.route('/view_prof_doc/<prof_id>')
def view_prof_doc(prof_id):
    professional = Professionals.query.get(prof_id)
    
    # If the professional and document exist
    if professional and professional.pdocData:
        return send_file(BytesIO(professional.pdocData), 
                         mimetype='application/pdf',  # Assuming the document is a PDF
                         download_name=professional.pdocFilename)
    else:
        return "Document not found", 404

@app.route("/unblockProf/<id>")
def unblockProf(id):
    p1 = Professionals.query.filter_by(prof_id=id).first()
    p1.is_approved="Accepted"
    db.session.commit()
    return redirect("/admin")

@app.route("/blockCust/<id>")
def blockCust(id):
    check = (db.session.query(Service_request, Customer).join(Customer, Service_request.cust_id == Customer.cust_id).filter(or_(Service_request.status == "Accepted",Service_request.status == "Requested")).all())
    if session["role"]=="admin":
        if not check:
            p1 = Customer.query.filter_by(cust_id=id).first()
            p1.is_allowed="Blocked"
            db.session.commit()
            return redirect("/admin")
        else:
            flash("Sorry,you cannot delete your account until all requests are Closed")
            return redirect("/admin")
    else:
        return redirect("/login")
    

@app.route("/unblockCust/<id>")
def unblockCust(id):
    p1 = Customer.query.filter_by(cust_id=id).first()
    p1.is_allowed="Allowed"
    db.session.commit()
    return redirect("/admin")

@app.route("/viewBlockedProf")
def viewBlockedProf():
    blockedProf=Professionals.query.filter(Professionals.is_approved=="Blocked")
    return render_template("blockedProf.html",blockedProf=blockedProf)

@app.route("/blockProf/<int:id>")
def blockProf(id):
    if session["role"]=="admin":
        check = (db.session.query(Service_request, Professionals).join(Professionals, Service_request.prof_id == Professionals.prof_id).filter(or_(Service_request.status == "Accepted",Service_request.status == "Requested")).all())
        if not check:
            p1 = Professionals.query.filter_by(prof_id=id).first()
            p1.is_approved="Blocked"
            db.session.commit()
            return redirect("/admin")
            
        else:
            flash("Sorry,you cannot delete your account until all requests are either closed or rejected")
            return redirect("/admin")
    else:
        return redirect("/login")

@app.route("/deleteCust/<int:id>")
def deleteCustomer(id):
    if session["role"]=="admin":
        check = (db.session.query(Service_request, Customer).join(Customer, Service_request.cust_id == Customer.cust_id).filter(Service_request.status=="Accepted").all())
        if not check:
            c1=Customer.query.filter_by(cust_id=id).first()
            c1.is_allowed="Deleted"
            db.session.commit()
            return redirect("/admin")
        else:
            flash("Sorry,you cannot delete their account until all requests are Closed.Keep check manually and try later on.")
            return redirect("/admin")
    else:
        return redirect("/login")

#================================Customer==============================================================================

@app.route("/customer")
def customer():
    servType = db.session.query(Service.pServiceType).distinct().all()
    custHistory = (db.session.query(Professionals, Service_request, Service)
                .join(Service_request, Service_request.prof_id == Professionals.prof_id)
                .join(Service, Service.s_id == Service_request.s_id)
                .filter(Service_request.cust_id == session["id"])
                .all())
    return render_template("customer.html",servType=servType,custHistory=custHistory)

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
        subServices = (db.session.query(Professionals).filter_by(pserviceName=subService_title).filter(Professionals.is_approved=="Accepted").all())
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



@app.route("/book_service/<prof_id>/<subService_title>/<price>")
def book_service(prof_id,subService_title,price):
    if session["role"]=="customer":
        service_id = (db.session.query(Service.s_id)
                .join(Professionals, Professionals.pserviceName == Service.sname)
                .filter(Professionals.pserviceName == subService_title).filter(Professionals.is_approved=="Accepted")
                .first())
        s1=Service_request(cust_id=session["id"],prof_id=int(prof_id),s_id=service_id[0],date_of_req=date.today(),price=price,status="Requested",cpay=False,ppay=False)
        db.session.add(s1)
        db.session.commit()
        flash("Your Service has been booked successfully")
        return redirect("/customer")
    else:
        return redirect("/login")
#---------------------------------------Cstomer profile-----------------
@app.route("/deleteCustProfile")
def deleteCustProfile():
    if session["id"] and session["role"]=="customer":
        check = (db.session.query(Service_request, Customer).join(Customer, Service_request.cust_id == Customer.cust_id).filter(or_(Service_request.status == "Accepted",Service_request.status == "Requested")).all())
        if not check:
            c1=Customer.query.filter_by(cust_id=session["id"]).first()
            c1.is_allowed="Left"
            db.session.commit()
            return redirect("/login")
        else:
            flash("Sorry,you cannot delete your account until all requests are Closed")
            return redirect("/cust_profile")
    else:
        return redirect("/login")

@app.route("/updateCustProfile/<id>",methods=["GET","POST"])
def updateCustProfile(id):
    if request.method=="POST":
        up_cname=request.form.get("cname")
        up_cexp=request.form.get("exp")
        up_caddress=request.form.get("caddress")
        up_cpincode=request.form.get("cpincode")
        up_cphoneNo=request.form.get("cphoneNo")
        p=Customer.query.filter_by(cust_id=id).one()
        p.cname=up_cname
        p.cexp=up_cexp
        p.caddress=up_caddress
        p.cpincode=up_cpincode
        p.cphoneNo=up_cphoneNo
        db.session.commit()
        return redirect("/customer")
    else:
        c=Customer.query.filter_by(cust_id=id).one()
        return render_template("updateCustProfile.html",c=c)
    
@app.route("/cust_profile")
def cust_profile():
    if session["id"] and session["role"]=="customer":
        custDetails=Customer.query.filter_by(cust_id=session["id"]).one()
        return render_template("custprofile.html",c=custDetails)
    else:
        return redirect("/login")
#---------------------------------------PAYMENT--------------------------------------------------
@app.route("/payment/<id>",methods=["GET","POST"])
def payment(id):
    if request.method=="POST":
        cradnum=request.form.get("cradnumber")
        exprire=request.form.get("expiry")
        cvv=request.form.get("cvv")
        s=Service_request.query.filter(Service_request.sr_id==id).one()
        s.cpay=True
        s.status="C Pay done"
        db.session.commit()
        return redirect("/customer")
    else:
        return render_template("paymentPortal.html",id=id)
@app.route("/pPaymentConfirm/<id>")
def ppayconfirm(id):
    s=Service_request.query.filter(Service_request.sr_id==id).one()
    s.ppay=True
    s.status="Payment Verified"
    db.session.commit()
    return redirect("/professional")

@app.route("/transHistory/<id>")
def transHistory(id):
    s=(db.session.query(Professionals, Service_request)
                .join(Service_request, Service_request.prof_id == Professionals.prof_id)
                .join(Service, Service.s_id == Service_request.s_id)
                .filter(Service_request.cust_id == id).filter(Service_request.ppay==True)
                .all())
    return render_template("transHistory.html",s=s)
    

#---------------------------------------extra------------------------------
@app.route("/custSummary")
def custSummary():
    cudata = db.session.query(Service_request.status,func.count(Service_request.status).label('count')).filter(Service_request.cust_id==session["id"]).group_by(Service_request.status).all()
    service_status,service_count=[],[]
    for status,count in cudata:
        service_status.append(status)
        service_count.append(count)
    print(service_status,service_count)
    plt.bar(service_status, service_count, color=['#66b3ff', '#99ff99', '#ff9999','#7ec3bf'])
    plt.title('Service Requests Summary')
    plt.ylabel('Number of Requests')
    plt.savefig('cust_service_requests_summary.png')
    plt.clf()

     #making seactor wise graph
    sectordata = db.session.query(Service_request.Service.sname,func.count(Service_request.Service.sname).label('count')).group_by(Service_request.Service.sname).filter(Service_request.cust_id==session["id"]).all()
    sector,prof_count=[],[]
    for id,count in sectordata:
        sector.append(id)
        prof_count.append(int(count))
    print(sector,prof_count)
    plt.bar(sector, prof_count, color=['#66b3ff', '#99ff99', '#ff9999','#7ec3bf'])
    plt.title('Services')
    plt.ylabel('Number of Orders')
    plt.ylabel('Services')
    plt.savefig('serv_analysis.png')
    plt.clf()

    
    #making rating wise plot graph
    # ratingdata = db.session.query(Service_request.srating,func.count(Service_request.srating).label('count')).group_by(Service_request.srating).all()
    # rating,count=[],[]
    # for id,count in ratingdata:
    #     rating.append(id)
    #     count.append(count)
    # print(rating,count)
    # plt.bar(rating, count, color=['#66b3ff', '#99ff99', '#ff9999','#7ec3bf','#8b78ce'])
    # plt.title('Rating of all orders')
    # plt.ylabel('Number of Orders')
    # plt.xlabel('Rating')
    # plt.savefig('rating.png')
    # plt.clf() 

    return "your image is saved successfully"

@app.route("/customer_search",methods=["GET","POST"])
def customer_search():
    if request.method=="POST":
        search_by = request.form.get('search_by')
        search_text = request.form.get('search_text')
        
        if search_by in ["ServiceName","Time Required","Category"]:
            search_results = (db.session.query(Service)
                            .filter(or_(
                                Service.sname.ilike(f'%{search_text}%'),
                                Service.stime_req.ilike(f'%{search_text}%'),
                                Service.pServiceType.ilike(f'%{search_text}%')
                            )).all())
        elif search_by in ["Location","Pincode","Professional Name"]:
            
            search_results = (db.session.query(Professionals)
                            .filter(or_(
                                Professionals.pname.ilike(f'%{search_text}%'),
                                Professionals.ppincode.ilike(f'%{search_text}%'),
                                Professionals.paddress.ilike(f'%{search_text}%')
                            )).filter(Professionals.is_approved=="Accepted").all())
        elif search_by in ["Status","Rating","Date Of Appointment"]:
            search_results = (db.session.query(Service_request)
                            .filter(or_(
                                Service_request.status.ilike(f'%{search_text}%'),
                                Service_request.srating.ilike(f'%{search_text}%'),
                                Service_request.date_of_req.ilike(f'%{search_text}%')
                            )).filter(Service_request.cust_id == session["id"]).all())
        else:
            search_results=[]

        return render_template('custSearch.html', search_results=search_results,search_by=search_by,search_text=search_text)
    else:
        return render_template("custSearch.html")

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
            s.srating=rating
            db.session.commit()
            return redirect("/customer")
        else:
            results = (db.session.query(Service_request, Service, Professionals).join(Service, Service_request.s_id == Service.s_id).join(Professionals, Service_request.prof_id == Professionals.prof_id).join(Customer,Service_request.cust_id == Customer.cust_id).filter(Service_request.sr_id==ser_reqId).all())
            print(results)
            dt=date.today()
            return render_template("csremark.html",results=results,dt=dt)
    else:
        return redirect("/login")
    
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
            cphoneNo=request.form.get("phoneNo")
            c1=Customer(cemail=cemail,cpassword=cpassword,cname=cname,caddress=caddress,cpincode=cpincode,cphoneNo=cphoneNo,is_allowed="Allowed")
            db.session.add(c1)
            db.session.commit()
            return redirect("/login")
        else:
            flash("Please select another username")
            return redirect("/customer_signUp")
    else:
        return render_template("csignup.html")
#================================PROFESSIONALS===========================================================================
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

@app.route("/professional_search",methods=["GET","POST"])
def professional_search():
    if request.method=="POST":
        search_by = request.form.get('search_by')
        search_text = request.form.get('search_text')
        query = db.session.query(Service_request).filter_by(prof_id=session["id"])
        if search_by == 'Date':
            search_results = query.filter(Service_request.date_of_req.ilike(f'%{search_text}%')).all()
        elif search_by == 'Location':
            search_results = query.join(Customer).filter(Customer.caddress.ilike(f'%{search_text}%')).filter(Customer.is_allowed=="Allowed").all()
        elif search_by == 'PinCode':
            search_results = query.join(Customer).filter(Customer.cpincode.ilike(f'%{search_text}%')).filter(Customer.is_allowed=="Allowed").all()
        elif search_by=="Name":
            search_results = query.join(Customer).filter(Customer.cname.ilike(f'%{search_text}%')).filter(Customer.is_allowed=="Allowed").all()
        elif search_by=="Email":
            search_results = query.join(Customer).filter(Customer.cemail.ilike(f'%{search_text}%')).filter(Customer.is_allowed=="Allowed").all()
        elif search_by=="Rating": 
            search_results = query.filter(Service_request.srating.ilike(f'%{search_text}%')).all()
        elif search_by=="Status":
            search_results = query.filter(Service_request.status.ilike(f'%{search_text}%')).all()
        elif search_by=="Phone Number":
            search_results = query.join(Customer).filter(Customer.cphoneNo.ilike(f'%{search_text}%')).filter(Customer.is_allowed=="Allowed").all()
        else:
            search_results=[]

        return render_template('professional_search.html', search_results=search_results,search_by=search_by,search_text=search_text)
    else:
        return render_template("professional_search.html")

@app.route("/deleteProfProfile")
def deleteProfProfile():
    if session["id"] and session["role"]=="professional":
        check = (db.session.query(Service_request, Professionals).join(Professionals, Service_request.prof_id == Professionals.prof_id).filter(or_(Service_request.status == "Accepted",Service_request.status == "Requested")).filter(Professionals.prof_id==session["id"]).all())
        print(check)
        if not check:
            p1 = Professionals.query.filter_by(prof_id=session["id"]).first()
            if p1:               
                p1.is_approved="Left"
                db.session.commit()
                return redirect("/login")
            else:
                flash("Professional not found.")
                return redirect("/prof_profile")
        else:
            flash("Sorry,you cannot delete your account until all requests are either closed or rejected")
            return redirect("/prof_profile")
    else:
        flash("Please login first")
        return redirect("/login")

@app.route("/updateProfProfile/<id>",methods=["GET","POST"])
def updateProfProfile(id):
    if request.method=="POST":
        up_pname=request.form.get("name")
        up_pexp=request.form.get("exp")
        up_paddress=request.form.get("address")
        up_ppincode=request.form.get("pincode")
        up_pphoneNo=request.form.get("phoneNo")
        p=Professionals.query.filter_by(prof_id=id).one()
        p.pname=up_pname
        p.pexp=up_pexp
        p.paddress=up_paddress
        p.ppincode=up_ppincode
        p.pphoneNo=up_pphoneNo
        db.session.commit()
        return redirect("/professional")
    else:
        p=Professionals.query.filter_by(prof_id=id).one()
        print(p)
        return render_template("updateProfProfile.html",p=p)
    
@app.route("/prof_profile")
def prof_profile():
    if session["id"] and session["role"]=="professional":
        profDetails=Professionals.query.filter_by(prof_id=session["id"]).one()
        category=Service.query.filter_by(sname=profDetails.pserviceName).one()
        return render_template("prof_profile.html",p=profDetails,category=category)
    else:
        return redirect("/login")

@app.route("/viewRejectedRequest")
def viewRejectedRequest():
    ser= (db.session.query(Customer,Service_request)
                 .join(Service_request, Customer.cust_id == Service_request.cust_id)
                 .join(Professionals, Professionals.prof_id == Service_request.prof_id)
                 .filter(Service_request.prof_id == session["id"]).filter(Service_request.status == "Rejected")
                 .all())
    return render_template("viewRejectedRequest.html",ser)

#status can take : Accepted,Rejected,Requested,Closed,C Pay done,Payment verified
@app.route("/profAcceptService/<serviceRq_id>")
def profAcceptService(serviceRq_id):
    s1=Service_request.query.filter_by(sr_id=serviceRq_id).one()
    s1.status="Accepted"
    db.session.commit()
    return redirect("/professional")
@app.route("/profDeleteService/<serviceRq_id>")
def profDeleteService(serviceRq_id):
    s1=Service_request.query.filter_by(sr_id=serviceRq_id).one()
    s1.status="Deleted"
    db.session.commit()
    return redirect("/professional")

@app.route("/profRejectService/<serviceRq_id>")
def profRejectService(serviceRq_id):
    s1=Service_request.query.filter_by(sr_id=serviceRq_id).one()
    s1.status="Rejected"
    db.session.commit()
    return redirect("/professional")

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
                file = request.files['document']
                paddress=request.form.get("caddress")
                ppincode=request.form.get("cpincode")
                pphoneNo=request.form.get("cphoneNo")
                price=request.form.get("price")
                p1=Professionals(pemail=pemail,pdocData=file.read(),pdocFilename=file.filename,ppassword=ppassword,pname=pname,pserviceName=pserviceName,pexp=pexp,paddress=paddress,ppincode=ppincode,pphoneNo=pphoneNo,price=price,is_approved="Waiting")
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

@app.route("/logout")
def logout():
    session["username"]=None
    session["password"]=None
    session["id"]=None
    session["role"]=None
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)