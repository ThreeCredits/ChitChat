# ChitChat
ChitChat is an open source cross-platform instant messaging application, that gives his user access to both server and client code.

## Quickstart

### Application usage
First, make sure you have all the required python modules installed by running `pip install -r requirements.txt`.
Upon starting `main.py`, you will be presented with the following screen:<p>
![immagine](https://user-images.githubusercontent.com/64363733/201195556-92dc3066-1835-40dc-a039-eab349bb4521.png)<p>
Insert the server and port of the server you want to connect with.<p>
![immagine](https://user-images.githubusercontent.com/64363733/201196905-ef80cfe7-89a9-442c-8eba-5594436d6436.png)<p>
Then, click on Connect.
You will then be prompted with the login form.<p>
### Registering
If you need to register to the server, click on the `New Here? Register` button.  
You will be presented with the following screen:  <p>
![immagine](https://user-images.githubusercontent.com/64363733/201197347-80c36f24-aac2-46b7-9f19-147f4f531844.png)<p>
Fill the form with the desidered username and password. Note that there is a limit of `9999` users with the same username, and that the password needs to have at least 12 characters, with at least on lowercase, uppercase and digit.
### Logging in
If you are already registered, fill the form with your login info. Remember that your tag is the number that you got assigned after your registration.
## After Logging in
You will be presented with the following:<p>
![immagine](https://user-images.githubusercontent.com/64363733/201203810-b62ed603-a389-4595-a637-3879823ae884.png)
In red are highlighted (from left to right, from top to bottom):  
- Your username
- Your usertag (remember to take note of it on your first login, since it is needed to log again!
- The `more` button. Currently, it will only allow you to logout. Note that closing the app normally will log you out from the server, but it is not guaranteed to be instantaneous and it can take up to 60 seconds (the timeout time).
- Your status. You can change your status by clicking on the user image ( which for now is not settable ) and selecting one. A status change is immediately notified to the server.
- Your ping.
- The `New Chat` button, which opens the wizard for creating a new chat with another user. Note that multi user chat are actually natively supported by the server/database, but are yet to be implemented on GUI. If you or the server owner modifies the database to have more than two participants on a chat, it will work fine and become a group chat. For this reason, you can also create multiple chats with the same user, as it is technically a group chat.
### Creating a chat
You will be presented with this.  
![immagine](https://user-images.githubusercontent.com/64363733/201205573-4fcfadbb-a820-44a6-8566-cdbacbe30367.png)<p>
Insert a chat name, chat description, username and user tag and you are ready to go!  
Note that, while the description is not yet visualized in the GUI, it is still stored on both server and client files, so that you won't lose the descriptions and you will be hopefully be able to see them in a release or two.  
If the user you selected does not exist, an error will show. Else, the chat will be created, and will pop up in your chats.
### Using the chats
This is a typical chat screen.<p>
![immagine](https://user-images.githubusercontent.com/64363733/201210712-2931c1a2-f619-481e-ad6b-bd46c4fa7052.png)<p>
If you need help understanding how to use that, you should not use this app.  

## Server setup
First, make sure you have all the required python modules installed by running `pip install -r requirements.txt`.
Then, make sure your database management system is open to connections from your local machine.
Create a database named "chitchat" using a mysql engine. We used `MariaDB`, but you may be able to make it work with other engines.  
Run in order:  
- `Tables.sql`
- `queries.sql`
This setup needs to be only done once.

### Starting the server
To start the server simply execute `server.py`. The server should be ready and running.






