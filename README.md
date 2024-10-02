# AZHouseService

#  Questions faced during project
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
