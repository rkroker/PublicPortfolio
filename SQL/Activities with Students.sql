WITH stuactvs AS (
	SELECT
		s.dcid studcid,
		g.name actname,
		ps_customfields.getStudentscf(s.id, g.value) actval
	FROM
		students s
		JOIN gen g ON g.cat = 'activity'
	WHERE
		s.enroll_status = 0
		AND s.schoolid = 495
	ORDER BY
		s.dcid
)
SELECT
	s.dcid,
	sa.actname,
	s.lastfirst,
	s.grade_level
FROM
	students s
	JOIN stuactvs sa ON sa.studcid = s.dcid
	AND sa.actval = 1
	AND sa.actname IN ('Football')
ORDER BY
	sa.actname,
	s.lastfirst