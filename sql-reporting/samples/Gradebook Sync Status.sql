SELECT
	t.lastfirst AS Teacher,
	s.termid as Term,
	s.course_number AS Course,
	CASE
		WHEN EXISTS (
			SELECT
				*
			FROM
				pgfinalgrades
			WHERE
				pgfinalgrades.sectionid = s.id
		) THEN MAX(g.lastgradeupdate)
		ELSE NULL
	END AS LastGradeUpdate,
	CASE
		WHEN EXISTS (
			SELECT
				*
			FROM
				pgfinalgrades
			WHERE
				pgfinalgrades.sectionid = s.id
		) THEN 'Grades Synchronized'
		ELSE 'No Grade Synchronized'
	END AS GradeStatus
FROM
	Sections s
	JOIN Teachers t ON s.teacher = t.id
	LEFT OUTER JOIN pgfinalgrades g ON s.id = g.sectionid
WHERE 
	t.schoolid = ~(curschoolid)
	and s.termid between (~(curyearid)*100) AND ((~(curyearid)*100)+99)
GROUP BY
	t.lastfirst,
	s.termid,
	s.course_number,
	s.id
ORDER BY
	t.lastfirst