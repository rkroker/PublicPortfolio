SELECT 
  s.schoolid,
  s.grade_level,
  s.LastFirst,
  s.student_number||'@email.edu' stumail,
  COALESCE(s.street,'-Missing-') Street_Addr, 
  COALESCE(s.city,'-Missing-') City,
  COALESCE(s.state,'-Missing-') State, 
  COALESCE(s.zip,'-Missing-') Zip,
  COALESCE(MAX(CASE WHEN sca.contactpriorityorder = '1' THEN p.FIRSTNAME ELSE '-Not Recorded-' END), '-Not Recorded-') AS C1_Firstname,
  COALESCE(MAX(CASE WHEN sca.contactpriorityorder = '1' THEN p.LASTNAME ELSE '-Not Recorded-' END), '-Not Recorded-') AS C1_Lastname,
  COALESCE(MAX(CASE WHEN sca.contactpriorityorder = '1' THEN e.EmailAddress ELSE '-Not Recorded-' END), '-Not Recorded-') AS C1_Email,
  COALESCE(MAX(CASE WHEN sca.contactpriorityorder = '1' THEN TO_CHAR(ph.phonenumber) ELSE '-Not Recorded-' END), '-Not Recorded-') AS C1_Phone,
  COALESCE(MAX(CASE WHEN sca.contactpriorityorder = '2' THEN p.FIRSTNAME ELSE '-Not Recorded-' END), '-Not Recorded-') AS C2_Firstname,
  COALESCE(MAX(CASE WHEN sca.contactpriorityorder = '2' THEN p.LASTNAME ELSE '-Not Recorded-' END), '-Not Recorded-') AS C2_Lastname,
  COALESCE(MAX(CASE WHEN sca.contactpriorityorder = '2' THEN e.EmailAddress ELSE '-Not Recorded-' END), '-Not Recorded-') AS C2_Email,
  COALESCE(MAX(CASE WHEN sca.contactpriorityorder = '2' THEN TO_CHAR(ph.phonenumber) ELSE '-Not Recorded-' END), '-Not Recorded-') AS C2_Phone
FROM 
  Students s
  INNER JOIN STUDENTCONTACTASSOC sca ON s.dcid = sca.STUDENTDCID
  INNER JOIN Person p ON sca.PERSONID = p.ID
  LEFT JOIN PERSONEMAILADDRESSASSOC pea ON p.ID = pea.PERSONID
  LEFT JOIN EMAILADDRESS e ON pea.EMAILADDRESSID = e.EmailAddressID
  LEFT JOIN PERSONPHONENUMBERASSOC pha ON p.ID = pha.PERSONID
  LEFT JOIN PHONENUMBER ph ON pha.PHONENUMBERID = ph.PHONENUMBERID 
WHERE
  s.schoolid = ~(curschoolid)
  AND s.grade_level = ~(curgradelevel)
  AND sca.contactpriorityorder IN ('1', '2')
GROUP BY
  s.schoolid,
  s.grade_level,
  s.LastFirst,
  s.Student_Number,
  s.street,
  s.city,
  s.state,
  s.zip
  ORDER BY
  s.grade_level ASC,
  s.lastfirst ASC
  
