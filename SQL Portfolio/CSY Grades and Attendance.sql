with curStu as (
SELECT
	s.id as id,
	s.student_number as student_number,
	s.lastfirst as lastfirst,
	s.grade_level as grade_level,
	s.enroll_status as enroll_status,
	s.entrydate as entrydate,
	s.exitdate as exitdate
FROM
	students s
WHERE
	s.entrydate >= (SELECT t.firstday FROM terms t WHERE t.id = ~(curyearid)*100 AND t.schoolid = ~(curschoolid))
	and s.schoolid = ~(curschoolid)
)

SELECT
--	cs.id,
	cs.student_number,
	cs.lastfirst,
	cs.grade_level,
	cs.enroll_status,
--	cs.entrydate,
--	cs.exitdate 
	sgs.grade_level as Course_Level,
	sgs.course_name,
	sgs.credit_type,
	MAX(CASE sgs.storecode WHEN 'Q1' THEN sgs.percent ELSE NULL END) AS Q1,
	MAX(CASE sgs.storecode WHEN 'Q1' THEN sgs.absences ELSE NULL END) AS Q1ABS,
	MAX(CASE sgs.storecode WHEN 'Q2' THEN sgs.percent ELSE NULL END) AS Q2,
	MAX(CASE sgs.storecode WHEN 'Q2' THEN sgs.absences ELSE NULL END) AS Q2ABS,
	MAX(CASE sgs.storecode WHEN 'Q3' THEN sgs.percent ELSE NULL END) AS Q3,
	MAX(CASE sgs.storecode WHEN 'Q3' THEN sgs.absences ELSE NULL END) AS Q3ABS,
	MAX(CASE sgs.storecode WHEN 'Q4' THEN sgs.percent ELSE NULL END) AS Q4,
	MAX(CASE sgs.storecode WHEN 'Q4' THEN sgs.absences ELSE NULL END) AS Q4ABS,
	MAX(CASE sgs.storecode WHEN 'Y1' THEN sgs.percent ELSE NULL END) AS Y1,
	MAX(CASE sgs.storecode WHEN 'Y1' THEN sgs.absences ELSE NULL END) AS Y1ABS
FROM
curStu cs
join storedgrades sgs on cs.id = sgs.studentid
WHERE
sgs.termid >= ~(curyearid)*100 --comment out for cumalative YTD results
GROUP BY
--	cs.id,
	cs.student_number,
	cs.lastfirst,
	cs.grade_level,
	cs.enroll_status,
--	cs.entrydate,
--	cs.exitdate 
	sgs.grade_level,
	sgs.course_name,
	sgs.credit_type
ORDER BY
	cs.grade_level ASC,
	cs.lastfirst ASC,
	sgs.grade_level DESC
