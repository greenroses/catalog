# Catalog App
The Item Catalog project consists of developing an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items. 

## How to run the app
1. Install Vagrant and VirtualBox if you have not
2. Clone or download the catalog folder
3. Launch the Vagrant VM (vagrant up), and login (vagrant ssh)
4. Run the application within the VM (python /vagrant/catalog/application.py)
5. Access the application by visiting http://localhost:8000

## _Note: if you want to repopulate the database, you may delete the categoryitemwithusers.db file, and run `python lotsofitems.py`. You can also edit the lotsofitems.py file to customize the database._ 


