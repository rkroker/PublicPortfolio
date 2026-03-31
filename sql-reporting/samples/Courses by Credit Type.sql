SELECT
	s.student_number,
	s.lastfirst as Student_Name,
	s.grade_level as Student_Grade,
	u.lastfirst as Councilour,
	sched.course_number as Course_Number,
	c.course_name as Course_Name,
	t.lastfirst as Teacher_Name,
	sched.expression as Period
	
FROM
	cc sched
	JOIN courses c ON c.course_number = sched.course_number
	JOIN students s on s.id = sched.studentid
	join studentcounselor sc on sc.studentdcid = s.dcid
	join users u on u.dcid = sc.userdcid
	join teachers t on t.id	= sched.teacherid
	
WHERE
	sched.schoolid = 495
	AND c.credittype IN (##)
	AND sched.termid = 3302
ORDER BY
	s.lastfirst ASC