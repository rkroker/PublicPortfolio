select
	cc.schoolid,
	cc.course_number,
	c.course_name,
	cc.section_number,
	t.lastfirst,
	cc.studentid,
	s.student_number,
	s.lastfirst,
	s.lunchstatus
from
	cc
	join students s on cc.studentid = s.id
	join courses c on cc.course_number = c.course_number
	join teachers t on cc.teacherid = t.id
	join s_pa_crs_x pacrs on pacrs.coursesdcid = c.dcid 
where
	cc.termid like '33%'
	and c.course_name like 'AP %'
	and c.course_number NOT LIKE '0%'
	and c.course_number NOT LIKE '1%'
	and c.course_number NOT LIKE '2%'
	and c.course_number NOT LIKE '3%'
	and c.course_number NOT LIKE '4%'
	and c.course_number NOT LIKE '5%'
	and c.course_number NOT LIKE '6%'
	and c.course_number NOT LIKE '7%'
	and c.course_number NOT LIKE '8%'
	and c.course_number NOT LIKE '9%'
	and c.course_number NOT LIKE 'F0%'
	and c.course_number NOT LIKE 'F1%'
	and c.course_number NOT LIKE 'S0%'
	and c.course_number NOT LIKE 'S1%'