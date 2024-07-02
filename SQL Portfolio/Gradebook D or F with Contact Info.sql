WITH cont AS (
	SELECT
		s.dcid studcid,
		p.id persid,
		CASE
			WHEN p.firstname IS NULL
			AND p.lastname IS NULL THEN '-No Name-'
			ELSE p.firstname || ' ' || p.lastname
		END pname,
		relcs.code relname,
		row_number() over (
			PARTITION BY s.dcid
			ORDER BY
				sca.contactpriorityorder
		) rnk
	FROM
		person p
		JOIN studentcontactassoc sca ON sca.personid = p.id
		JOIN studentcontactdetail scd ON scd.studentcontactassocid = sca.studentcontactassocid
		JOIN students s ON s.dcid = sca.studentdcid
		JOIN codeset relcs ON relcs.codesetid = scd.relationshiptypecodesetid
	WHERE
		p.isactive = 1
		AND trunc(SYSDATE) BETWEEN nvl(scd.startdate, trunc(SYSDATE))
		AND nvl(scd.enddate, trunc(SYSDATE))
	ORDER BY
		s.dcid
),
filtered_cont AS (
	SELECT
		studcid,
		persid,
		pname,
		relname,
		rnk
	FROM
		cont
	WHERE
		rnk = (
			SELECT
				MIN(rnk)
			FROM
				cont c2
			WHERE
				c2.studcid = cont.studcid
		)
),
priemail AS (
	SELECT
		ct.persid pid,
		ea.emailaddress emailaddr,
		row_number() over (
			PARTITION BY ct.persid
			ORDER BY
				peaa.emailaddresspriorityorder
		) rnk
	FROM
		emailaddress ea
		JOIN personemailaddressassoc peaa ON peaa.emailaddressid = ea.emailaddressid
		JOIN cont ct ON ct.persid = peaa.personid
	ORDER BY
		ct.persid
),
priphone AS (
	SELECT
		ct.persid pid,
		ppna.phonenumberasentered pnum,
		phcs.code ptype,
		row_number() over (
			PARTITION BY ct.persid
			ORDER BY
				ppna.ispreferred DESC,
				ppna.phonenumberpriorityorder
		) rnk
	FROM
		personphonenumberassoc ppna
		JOIN cont ct ON ct.persid = ppna.personid
		JOIN codeset phcs ON phcs.codesetid = ppna.phonetypecodesetid
	ORDER BY
		ct.persid
)
SELECT
	S.STUDENT_NUMBER,
	S.LASTFIRST,
	S.GRADE_LEVEL,
	SE.special_education_iep_code IEP,
	C .COURSE_NAME,
	T.LASTFIRST TEACHER_NAME,
	PGF.finalgradename TERM_NAME,
	PGF.GRADE,
	PGF.PERCENT,
	COALESCE(U.LASTFIRST, 'No Counselor Assigned') AS COUNSELOR_NAME,
	nvl(FC.relname, '-None-') RELATIONSHIP,
	FC.pname CONTACT_NAME,
	nvl(pem.emailaddr, '-None-') CONTACT_EMAIL,
	nvl(pph.pnum, '-None-') CONTACT_PHONE
FROM
	STUDENTS S
	INNER JOIN CC ON CC.STUDENTID = S.ID
	INNER JOIN SECTIONS SEC ON SEC.ID = CC.SECTIONID
	INNER JOIN PGFINALGRADES PGF ON PGF.SECTIONID = CC.SECTIONID
	AND PGF.STUDENTID = S.ID
	INNER JOIN COURSES C ON C .COURSE_NUMBER = CC.COURSE_NUMBER
	LEFT OUTER JOIN s_pa_stu_x SE ON SE.studentsdcid = S.dcid
	LEFT OUTER JOIN studentCounselor sco ON S.dcid = sco.studentdcid
	AND sco.isPrimary = 1
	LEFT OUTER JOIN users U ON sco.userdcid = U.dcid
	INNER JOIN TEACHERS T ON T.ID = CC.TEACHERID
	INNER JOIN filtered_cont FC ON FC.studcid = S.dcid
	LEFT OUTER JOIN priemail pem ON pem.pid = FC.persid
	AND pem.rnk = 1
	LEFT OUTER JOIN priphone pph ON pph.pid = FC.persid
	AND pph.rnk = 1
WHERE
	CC.TERMID IN (
		SELECT
			TR.ID
		FROM
			TERMS TR
		WHERE
			TR.SCHOOLID = S.SCHOOLID
			AND SYSDATE BETWEEN TR.FIRSTDAY
			AND TR.LASTDAY
	)
	AND PGF.FINALGRADENAME = 'Q3' --%param1%
	AND PGF.PERCENT < 70
	AND PGF.GRADE IN ('D', 'F')
	AND S.SCHOOLID = ~(curschoolid)
ORDER BY
	S.LASTFIRST,
	SEC.External_EXPRESSION