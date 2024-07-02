WITH stuactvs AS (
	SELECT
		s.dcid studcid,
		g.name actname,
		ps_customfields.getStudentscf(s.id, g.value) actval
	FROM
		students s ~[if#cursel.%param1%=Yes]
		INNER JOIN ~[temp.table.current.selection:students] stusel ON stusel.dcid = s.dcid [/if#cursel]
		JOIN gen g ON g.cat = 'activity'
	WHERE
		s.enroll_status = 0
		AND s.schoolid = 495
	ORDER BY
		s.dcid
)


SELECT
	stu.student_number,
	stu.lastfirst Student_Name,
	stu.grade_level,
	sec.course_number,
	sec.section_number,
	tea.lastfirst Teacher_Name,
	PGF.grade,
	listagg(UNIQUE sa.actname, ' | ') within GROUP (ORDER BY sa.actname) as stu_activities
FROM
	students stu
	join pgfinalgrades PGF on PGF.studentid = stu.id
	join sections sec on sec.id = PGF.sectionid
	join teachers tea on tea.id = sec.teacher
	JOIN stuactvs sa ON sa.studcid = stu.dcid
	AND sa.actval = 1
WHERE
	PGF.grade = 'F'
	AND sa.actname = 'Wrestling, Boys'
	AND  sec.termid LIKE '33%%'
GROUP BY
	stu.student_number,
	stu.lastfirst,
	stu.grade_level,
	sec.course_number,
	sec.section_number,
	tea.lastfirst,
	PGF.grade
ORDER BY
	stu.lastfirst