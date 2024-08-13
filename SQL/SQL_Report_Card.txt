SELECT
	stu.student_number,
	stu.id as student_id,
	stu.last_name,
	stu.first_name,
	stu.grade_level,
	sgs.schoolid,
	sgs.termid,
	sec.course_number,
	sec.section_number,
	sec.id as section_id,
	sec.external_expression,
	sgs.teacher_name,
	MAX(CASE sgs.storecode WHEN 'Q1' THEN sgs.percent ELSE NULL END) AS Q1,
	MAX(CASE sgs.storecode WHEN 'Q2' THEN sgs.percent ELSE NULL END) AS Q2,
	MAX(CASE sgs.storecode WHEN 'Q3' THEN sgs.percent ELSE NULL END) AS Q3,
	MAX(CASE sgs.storecode WHEN 'Q4' THEN sgs.percent ELSE NULL END) AS Q4
FROM
	storedgrades sgs
	JOIN sections sec ON sgs.sectionid = sec.id
	JOIN students stu ON sgs.studentid = stu.id
WHERE
	stu.schoolid = ~(curschoolid)
	AND sgs.termid IN (select terms.id from terms where terms.id like '~(curyearid)%')
	AND sgs.storecode IN ('Q1', 'Q2', 'Q3', 'Q4')
GROUP BY
	stu.student_number,
	stu.last_name,
	stu.id,
	stu.first_name,
	stu.grade_level,
	sgs.schoolid,
	sgs.termid,
	sec.course_number,
	sec.section_number,
	sec.id,
	sec.external_expression,
	sgs.teacher_name
ORDER BY
	stu.last_name ASC,
	stu.first_name ASC,
	sgs.termid ASC;