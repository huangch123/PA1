Project 1: Photo Share
Zuoqi Zhang & Charles Huang

1. Please run schema.sql in your terminal first to create tables and initialize.
2. After initialization, there will be four users in the database, some of our functions may require user to login. For your convenience, please login as test user, email address is test@bu.edu, and password is test.
3. The /upload folder is used to store original photos. There are already three photos in it. We only store the relative path of the photo in our database. There is a record of like and a record of comment in the database.
4. Please access specific photo or album by typing urls like /photo/123 or /album/123.
5. We show most popular photos and you-may-like photos, top 10 user and top 10 tags on the homepage.
6. On the photo page, you can like and write a comment on the photo. You need to press the button to see tags and people who like this photo, this information is initially hidden when you see this page.
7. On the upload page, you can save the photo to an existed album or create a new one (this will link to a new page). Also, you can add several tags separating them by spaces. The select boxes show existed albums and tags.
8. Go to the drop down menu of your name and select friends to see your friends. And on this page you can search and add new friends, recommended friends will appear on this page as well.

Use cases:
1. Register and login button is on the right top corner. After logging in, click the button named Friends under the drop down menu under your name, you can see your friends and add a new friend here. Top 10 users are listed on homepage.
2. In our website, user has to login to browse photos and albums. You can click on a photo or check them out from albums.
3. To search photos by tag name, click the search button in the top navigation bar.
4. On the photo page, you can like a photo or write a comment.
5. Friend recommendation is shown on search_friend page.
