SELECT
	cat.cat as Module_Name,
	cat.id as ModuleID,
	rec.text1 as Grade,
	to_char(rec.date1, 'YYYY-MM-DD') AS Date_Updated,	
	rec.double1 as Listening_Proficiency_Level,
	rec.double2 as Speaking_Proficiency_Level,
	rec.double3 as Reading_Proficiency_Level,
	rec.double4 as Writing_Proficiency_Level,
	rec.double5 as Oral_Language_Proficiency_Level,
	rec.double6 as Literacy_Proficiency_Level,
	rec.double7 as Comprehension_Proficiency_Level,
	rec.double8 as Overall_Proficiency_Level,
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
	cat.id = 731980--WIDA Module ID
	AND rec.id > 0 --grabs non-blank records
ORDER BY
	rec.whencreated