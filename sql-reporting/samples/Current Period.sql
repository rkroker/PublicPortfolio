SELECT
	period.abbreviation 
FROM
	bell_schedule_items bsi
	join bell_schedule on bsi.bell_schedule_id = bell_schedule.id
	join calendar_day on bsi.bell_schedule_id = calendar_day.bell_schedule_id
	join period on bsi.period_id = period.id
WHERE
	(((substr('~[current.time.no.colon]', 1, 2)) * 3600) + ((substr('~[current.time.no.colon]', 3,2)) * 60)) > bsi.start_time
	and (((substr('~[current.time.no.colon]', 1, 2)) * 3600) + ((substr('~[current.time.no.colon]', 3,2)) * 60)) < bsi.end_time
	and calendar_day.date_value like sysdate
	and calendar_day.schoolid = 495