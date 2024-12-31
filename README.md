# AZHouseService

It is a multi-user app (requires one admin and other service professionals/ 
customers) which acts as platform for providing comprehensive home servicing and solutions. 

# Technologies used 
Html / CSS / JS: Frontend technology for user interface design and interactivity 

Flask: A backend framework in python used for building web applications

Flask SQLite: Database management system for storing application data 

SQLAlchemy: ORM (object-relational mapping) tool for database interaction 

Matplotlib: A library in python used for creating charts

Date time: Used for manipulating dates and times, such as creating timestamps, calculating date differences, and formatting dates. 

BytesIO: A module in python that creates an in-memory byte stream, often used to handle binary data like images or files without saving to disk. 

func: Function from the SQLAlchemy module that provides access to SQL functions and expressions,allowing you to use SQL functions (like COUNT, SUM, MAX) directly within SQLAlchemy queries. 

_or: Function from the SQLAlchemy module combines multiple conditions with an OR logical operation in SQL queries, allowing flexible filtering with multiple criteria. 

## Core Functionalities
The app have a suitable model to store and differentiate all the types of user of the app.

### Admin Dashboard - for the Admin
Admin will manage all the users (customers/service professional)

Admin will approve a service professional after verification of profile documents

Admin will block customer/service professional based on fraudulent activity/poor reviews

### Service Management - for the Admin
Create a new service with a base price.

Update an existing service - e.g. name, price, time_required and/or other fields

Delete an existing service
### Service Request - for the customers
Create a new service request based on the services available

Edit an existing service request - e.g. date_of_request, completion status, remarks etc

Close an existing service request.

A dummy payment portal 

Can see all the Transaction History
### Search for available services

The customers are able to search for available services based on their location, name, pin code etc.

The admin is able to search for a professional to block/unblock/review them.
### Take action on a particular service request - for the service professional
Ability to view all the service requests from all the customers

Ability to accept/reject a particular service request

Ability to close the service request once completed

##  Questions faced during project
1.What if same person has registered a customer and professional both 

2.Can two professionals register for same service

3.How can we retrieve booking is done by proper authentication

4.In Professional profile previous service sholuld include only closed or accepted closed both

5.What sholud be done if a professional rejects a service request

6.What if a customer/professional register herself as admin

7.What will happen to the pending sevices if the professional deletes his account 

8.What will happen if there are some services pending related to that customer

9.If admin deletes any professional it will be marked as blocked in profesionals.status as to not lost any data and if they leave themselves it will be marked as left same goes for customer.

Service_request status:Requested(Default),Accepted,Rejected,Closed

professional is_approved:Waiting(Default),Accepted,Rejectd,Blocked,Left,Deleted

Customer is_allowed:Allowed,Blocked,Left,Deleted
