SELECT
	cycle_day.dcid,
	cycle_day.id,
	cycle_day.schoolid,
	cycle_day.year_id,
	cycle_day.letter,
	cycle_day.day_number,
	cycle_day.abbreviation,
	cycle_day.day_name,
	cycle_day.sortorder,
	cycle_day.psguid
FROM
	cycle_day
WHERE
	cycle_day.schoolid = ~(curschoolid)
	and cycle_day.year_id = ~(curyearid)