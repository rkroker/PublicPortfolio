SELECT
	bell_schedule.dcid,
	bell_schedule.id,
	bell_schedule.schoolid,
	bell_schedule.year_id,
	bell_schedule.attendance_conversion_id,
	bell_schedule.name,
	bell_schedule.psguid
FROM
	bell_schedule
	join bell_schedule_items on bell_schedule.id = bell_schedule_items.bell_schedule_id
	join calendar_day on bell_schedule.id = calendar_day.bell_schedule_id
WHERE
	(((substr('~[current.time.no.colon]', 1, 2)) * 3600) + ((substr('~[current.time.no.colon]', 3,2)) * 60)) > bell_schedule_items.start_time
	and (((substr('~[current.time.no.colon]', 1, 2)) * 3600) + ((substr('~[current.time.no.colon]', 3,2)) * 60)) < bell_schedule_items.end_time
	and bell_schedule.schoolid = ~(curschoolid)
	and bell_schedule.year_id = ~(curyearid)
	and calendar_day.date_value like sysdate