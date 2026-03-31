SELECT
	period.dcid,
	period.id,
	period.schoolid,
	period.year_id,
	period.period_number,
	period.name,
	period.abbreviation,
	period.sort_order,
	period.psguid
FROM
	Period
where
	period.schoolid = ~(curschoolid)
	and period.year_id = ~(curyearid)