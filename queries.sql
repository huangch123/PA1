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