SELECT
	t.firstday
FROM
	terms t
WHERE
	t.id = ~(curyearid)*100
	AND t.schoolid = ~(curschoolid)