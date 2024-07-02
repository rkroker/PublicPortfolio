WITH split_courses AS (
	SELECT
		s.school_number as school_number,
		REGEXP_SUBSTR(s.activecrslist, '[^;]+', 1, LEVEL) AS course
	FROM
		schools s
	WHERE
		s.school_number = ~(curschoolid)
	CONNECT BY
		LEVEL <= REGEXP_COUNT(s.activecrslist, ';') + 1
)
SELECT
	sc.school_number,
	sc.course
FROM
	split_courses sc