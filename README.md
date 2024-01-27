# RSS-Newsfeed-Global Reader 

Documentation for the RSS-Newsfeed-Global Flask project. This is an A-level project made for AQA-NEA and reflects a two year course.

# Table of contents
- [RSS-Newsfeed-Global Reader](#rss-newsfeed-global-reader)
- [Table of contents](#table-of-contents)
- [Installation / Deployment](#installation-and-deployment)
- [Using the website](#using-the-website)




# Installation and Deployment
1. Download or clone this repository 
2. Open terminal
3. Navigate to project directory
4. Setup a virtual environment -> information on how to can be found [here](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/)
5. In the virtual environment, run ``~ pip install -r requirements.txt``
6. For the first time usage, run ``Testing/account_setup.py``
7. Then run ``main.py``

# Using the website
If the website was run with the testing module `account_setup.py` then there will be a basic admin account created, along with some initial data set. The default username and password for this account are: email - > "sysadmin@gmail.com", pwd -> "1234567"
If the website was just run from main, there will be no websites within the database and no admin account. This means that the first account that is created will inherit this admin role.

**General usage**
Create an account and login using the top left links on the website. Once logged in, you will be redirected to either the "Home" page or the "Discover" page. 
*Home Page*
The left sidebar allows for navigation between websites of different tags. Select the website to retrieve the latest articles. Articles can be saved using the button on each one, or can be read by clicking the redirect button.
*Discover Page*
Randomly selects unsaved websites from the database and presents each one to the user in their tag groupings. Tags are recommended based on a weighting system and will vary.


