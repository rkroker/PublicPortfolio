	SELECT
		period.abbreviation as period, --Sets Current Period by Local Time & Configuration
		cycle_day.letter as day, --Sets current Day type by Local Time & Configuration
		period.abbreviation || '(' || cycle_day.letter || ')' as current_exp, --Sets Current Expression by Period and Day
		(SELECT LISTAGG(terms.id, ', ') FROM terms WHERE sysdate >= terms.firstday AND sysdate <= terms.lastday and terms.schoolid = ~(curschoolid)) as actTerms, --Sets list of active terms
		(SELECT ~(curyearid)*100 FROM dual) as year --Sets year id in term format
	FROM
		bell_schedule_items bsi
		join bell_schedule on bsi.bell_schedule_id = bell_schedule.id
		join calendar_day on bsi.bell_schedule_id = calendar_day.bell_schedule_id
		join period on bsi.period_id = period.id
		JOIN cycle_day ON calendar_day.cycle_day_id = cycle_day.id
	WHERE
		(((substr('~[current.time.no.colon]', 1, 2)) * 3600) + ((substr('~[current.time.no.colon]', 3,2)) * 60)) > bsi.start_time
		and (((substr('~[current.time.no.colon]', 1, 2)) * 3600) + ((substr('~[current.time.no.colon]', 3,2)) * 60)) < bsi.end_time
		and calendar_day.date_value like sysdate
		and calendar_day.schoolid = ~(curschoolid)