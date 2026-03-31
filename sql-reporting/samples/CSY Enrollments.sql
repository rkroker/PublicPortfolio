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
	cs.id,
	cs.student_number,
	cs.lastfirst,
	cs.grade_level,
	cs.enroll_status
	cs.entrydate,
	cs.exitdate 
FROM
curStu cs