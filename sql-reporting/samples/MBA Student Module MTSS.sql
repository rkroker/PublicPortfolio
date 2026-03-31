SELECT
	cat.id,
	cat.cat,
	rec.text1 as Intervention,
	rec.text2 as Subject,
	rec.text3 as Tier,
	to_char(rec.date1, 'YYYY-MM-DD') AS Start_Date,
	to_char(rec.date2, 'YYYY-MM-DD') AS End_Date,	
	rec.int1 as Grade_Level,
	rec.schoolid as SchoolID,
	rec.yearid as YearID,
	rec.whocreated,
	to_char(rec.whencreated, 'YYYY-MM-DD HH24:MI:SS') AS whencreated,
	rec.whomodified,
	to_char(rec.whenmodified, 'YYYY-MM-DD HH24:MI:SS') AS whenmodified
FROM
	u_mba_app_records rec
	JOIN u_mba_app_modules cat ON rec.u_mba_app_modulesid = cat.id
WHERE
	cat.id = 707505--insert Module ID
	AND rec.id > 0 --grabs non-blank records
ORDER BY
	rec.whencreated