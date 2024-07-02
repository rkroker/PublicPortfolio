select
	students.id,
	students.student_number,
	students.lastfirst,
	students.grade_level,
	u.lastfirst as Councilour
from
	students
	join studentcounselor sc on sc.studentdcid = students.dcid
	join users u on u.dcid = sc.userdcid
where
	students.enroll_status = 0
	and students.schoolid = 495