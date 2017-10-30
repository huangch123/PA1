-- Get UID of a user
SELECT UID FROM USER WHERE EMAIL = 'zqzhang@bu.edu';

-- Register.
INSERT INTO USER (EMAIL, PASSWORD, FNAME, LNAME, GENDER) VALUES ('chahuang@bu.edu', 'hello', 'Charles', 'Huang', 'M');

-- Check if an email address has already been used.
SELECT * FROM USER WHERE EMAIL = 'zqzhang@bu.edu';

-- List all friends of a user.
SELECT F.UID2, U.EMAIL, U.FNAME, U.LNAME
FROM FRIENDSHIP F, USER U
WHERE F.UID1 = 3 AND F.UID2 = U.UID;

-- Find friends to add.
SELECT UID, EMAIL, FNAME, LNAME
FROM USER
WHERE EMAIL = 'zqzhang@bu.edu' AND FNAME = 'Zuoqi' AND LNAME = 'Zhang';

-- Add a new friend.
INSERT INTO FRIENDSHIP VALUES (1, 2);
INSERT INTO FRIENDSHIP VALUES (2, 1);

-- Recommend a new friend.
SELECT U.UID, U.EMAIL, U.FNAME, U.LNAME
FROM USER U, FRIENDSHIP F1, FRIENDSHIP F2
WHERE F1.UID1 = 'zqzhang'
  AND F1.UID2 = F2.UID1
  AND F2.UID2 <> F1.UID1
  AND U.UID = F2.UID2
  AND (F1.UID1, F2.UID2) NOT IN ( SELECT * FROM FRIENDSHIP F )
GROUP BY F2.UID2
ORDER BY COUNT(*) DESC;

-- Find top 10 users.
SELECT U.UID, U.EMAIL, U.FNAME, U.LNAME, TMP1.photoCnt + TMP2.commentCnt AS TOTAL
FROM USER U,
    ( SELECT A.UID , COUNT(*) AS photoCnt
      FROM PHOTO P, ALBUM A
      WHERE P.AID = A.AID
      GROUP BY A.UID
    ) AS TMP1,
    ( SELECT C.UID, COUNT(*) AS commentCnt
      FROM COMMENT C
      GROUP BY C.UID
    ) AS TMP2
WHERE U.UID = TMP1.UID AND TMP1.UID = TMP2.UID
GROUP BY U.UID
ORDER BY TOTAL DESC
LIMIT 10;

-- Leave a comment. (Users cannot leave comments for their own photos.)
SELECT A.UID
FROM PHOTO P, ALBUM A
WHERE P.AID = A.AID AND PID = 1;

INSERT INTO COMMENT (CONTENT, UID, PID) VALUES ('', 3, 1);

-- Add a like to a photo.
INSERT INTO FAVORITE (UID, PID) VALUES (3, 1);

-- Display likes.
SELECT COUNT(*) FROM FAVORITE WHERE PID = 1;

SELECT U.UID, U.FNAME, U.LNAME
FROM FAVORITE F, USER U
WHERE F.UID = U.UID AND F.PID = 1;

-- Show all tags of your photos.
SELECT DISTINCT AE.HASHTAG
FROM PHOTO P, ALBUM AM, ASSOCIATE AE
WHERE P.PID = AE.PID AND P.AID = AM.AID AND AM.UID = 3;

-- Show your photos by tag name.
SELECT P.PID, P.DATA
FROM PHOTO P, ALBUM AM, ASSOCIATE AE
WHERE P.PID = AE.PID AND P.AID = AM.AID AND AE.HASHTAG = 'boston';

-- Show all photos by tag name.
SELECT P.PID, P.DATA
FROM PHOTO P, ASSOCIATE A
WHERE P.PID = A.PID AND A.HASHTAG = 'boston';

-- Show the most popular tags.
SELECT HASHTAG
FROM ASSOCIATE
GROUP BY HASHTAG
ORDER BY HASHTAG DESC;

-- Search photos by tags.
SELECT P.PID, P.DATA
FROM PHOTO P, ASSOCIATE A
WHERE P.PID = A.PID AND A.HASHTAG = 'boston';


--------------- NEW QUERIES ---------------

-- YOU MAY ALSO LIKE (NEEDS TESTING) IN PHOTO/HOMEPAGE/SEARCH???
SELECT DISTINCT P3.PID, P3.CAPTION, P3.DATA -- ALL PHOTOS WITH 5 TO 1 OF THE TOP TAGS AND LEAST TO GREATEST TOTAL TAGS
FROM PHOTO P3,
    ALBUM AM2,
    ASSOCIATE AE3,
    (SELECT DISTINCT P2.PID P2ID, COUNT(AE2.HASHTAG) C2
    FROM PHOTO P2,
        ASSOCIATE AE2,
        (SELECT TOP 5 DISTINCT AE.HASHTAG AEHT, COUNT(AEHT) C
        FROM USER U, ALBUM AM, PHOTO P, ASSOCIATE AE
        WHERE U.UID = AM.UID AND AM.AID = P.AID AND P.PID = AE.PID AND U.UID = '0' -- CURRENT USER ID
        GROUP BY AEHT
        ORDER BY C DESC) AS TOPFIVE -- TOP FIVE TAGS OF CURRENT USER
    WHERE P2.PID = AE2.PID AND AE2.HASHTAG = TOPFIVE.AEHT
    GROUP BY P2.PID
    ORDER BY C2 DESC) AS WITHTOP -- ALL PHOTOS WITH 5 TO 1 OF THE TOP TAGS
WHERE P3.PID = WITHTOP.P2ID AND P3.PID = AE3.PID AND P3.AID = AM2.AID AND AM2.UID <> U.UID -- PHOTOS CANNOT BE CURRENT USER'S
GROUP BY P3.PID
ORDER BY WITHTOP.C2 DESC, COUNT(DISTINCT AE3.HASHTAG) ASC;

-- FRIEND RECOMMENDATIONS (NEEDS TESTING) IN SEARCH_FRIENDS
SELECT DISTINCT U3.UID, U3.FNAME, U3.LNAME -- FRIENDS OF FRIENDS
FROM USER U, FRIENDSHIP F, USER U2, FRIENDSHIP F2, USER U3
WHERE U.UID = F.UID1
  AND F.UID2 = U2.UID
  AND U2.UID = F2.UID1
  AND F2.UID2 = U3.UID
  AND U.UID <> U3.UID -- RECOMMENDED FRIEND CANNOT BE CURRENT USER
  AND U.UID = '0' -- CURRENT USER ID
GROUP BY U3.UID
ORDER BY COUNT(U3.UID) DESC; -- NUMBER OF TIMES FRIEND OF FRIEND SHOWS UP

-- SEARCH ON COMMENTS (NEEDS TESTING) IN SEARCH_FRIENDS
SELECT DISTINCT U.UID, U.FNAME, U.LNAME
FROM USER U, COMMENT C
WHERE U.UID = C.UID
  AND U.UID <> '0' -- RECOMMENDED USER CANNOT BE CURRENT USER
  AND C.CONTENT LIKE '%TEXT%' -- TEXT IS THE SEARCH TEXT   NOTE: MUST BE IN THIS FORMAT
GROUP BY U.UID
ORDER BY COUNT(C.CONTENT) DESC; -- ORDER BY NUMBER OF COMMENTS A USER MADE WITH SEARCH TEXT

-- TOP 10 USERS (NEEDS TESTING) IN HOMEPAGE
SELECT TOP 10 DISTINCT U.UID, U.FNAME, U.LNAME, (COUNT(NUMP.CP) + COUNT(NUMC.CC)) AS POINTS
FROM USER U,
    (SELECT AM.UID AS AMUID, COUNT(P.PID) AS CP
    FROM ALBUM AM, PHOTO P
    WHERE AM.AID = P.AID
    GROUP BY AMUID
    ORDER BY CP DESC) AS NUMP, -- NUM PHOTOS
    (SELECT C.UID AS CUID, COUNT(C.CID) AS CC
    FROM COMMENT C
    GROUP BY CUID
    ORDER BY CC) AS NUMC -- NUM COMMENTS
WHERE U.UID = NUMP.AMUID AND U.UID = NUMC.CUID
GROUP BY U.UID
ORDER BY POINTS DESC;